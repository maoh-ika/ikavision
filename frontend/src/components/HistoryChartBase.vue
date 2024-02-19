<template>
  <div>
    <q-card :style="{ boxShadow: 'none'}">
      <q-card-section class="q-px-md q-pt-md q-pb-none row items-center no-wrap">
        <div class="text-center full-width">
          {{ title }}
        </div>
        <q-space />
        <div class="col-auto">
          <q-btn color="grey-7" round flat icon="more_vert">
            <q-menu cover auto-close class="z-max">
              <q-list>
                <q-item v-if="rangeEnabled">
                  <q-option-group
                    :options="rangeOptions"
                    type="radio"
                    v-model="chartRange"
                    @update:model-value="rangeUpdated"
                  />
                </q-item>
                <slot name="actions" />
              </q-list>
            </q-menu>
          </q-btn>
        </div>
      </q-card-section>
      <q-card-section class="q-px-md q-pt-none">
        <Line :data="data" :options="options" :style="chartStyle"/>
      </q-card-section>
    </q-card>
  </div>
 </template>
    
<script lang="ts">
import { defineComponent, ref, watch, onMounted, computed, type PropType } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { useQuasar } from 'quasar'
import { Line } from 'vue-chartjs'
import { getLaunchDate } from '@/modules/Utils'
import { toMMDD, round } from '@/modules/Utils'
import type { BattleStatistics } from '@/modules/BattleStatisticsApi'
import PinableCard from '@/components/PinableCard.vue'

interface ChartRange {
  minTime: number
  maxTime: number
  unit: 'day' | 'month'
}

export default defineComponent({
  name: 'HistoryChartBase',
  components: { Line, PinableCard },
  props: {
    userId: {
      type: String,
    },
    data: {
      type: Object,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    labelY: {
      type: String,
      required: true
    },
    showLegend: {
      type: Boolean,
      default: true
    },
    showTooltipColor: {
      type: Boolean,
      default: true
    },
    tooltipValueFunc: {
      type: Function
    },
    maxX: {
      type: Number,
    },
    width: {
      type: Number
    },
    height: {
      type: Number
    },
    range: {
      type: String,
      default: 'oneMonth'
    },
    rangeEnabled: {
      type: Boolean,
      default: true
    },
    generateLegend: {
      type: Function
    }
  },
  setup(props) {
    const store = useStore()
    const { t } = useI18n()
    const $q = useQuasar()
    const chartRange = ref('oneMonth')
    const options = ref()
    const chartData = ref(props.data)
    let chartInstance: any

    watch(() => props.data, (newData) => {
      chartData.value = newData
    })

    onMounted(async () => {
      try {
        $q.loading.show()
        await rangeUpdated()
        options.value = makeOptions()
      } finally {
        $q.loading.hide()
      }
    })
    
    const rangeOptions = [
      { label: t('statistics.rateChart.range1Week'), value: 'oneWeek' },
      { label: t('statistics.rateChart.range1Month'), value: 'oneMonth' },
      { label: t('statistics.rateChart.range3Months'), value: 'threeMonths' },
      { label: t('statistics.rateChart.range6Months'), value: 'sixMonths' },
      { label: t('statistics.rateChart.rangeAll'), value: 'all' }
    ]
    
    const statistics = computed(() => {
      if (props.userId === undefined) {
        return []
      }
      const range = getChartRange()
      return store.getters['battleStatistics/findDailyStatistics'](props.userId, range.minTime, range.maxTime) as BattleStatistics
    })
    
    const environments = computed(() => {
      const range = getChartRange()
      return store.getters['battleEnvironment/findDailyEnvironments'](range.minTime, range.maxTime) as BattleStatistics
    })

    const chartStyle = computed(() => {
      const style: any = {}
      if (props.width) {
        style.width = `${props.width}px`
      }
      if (props.height) {
        style.height = `${props.height}px`
      }
      return style
    })
    
    const makeOptions = (): any => {
      const initRange = getChartRange()
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: props.showLegend,
            labels: {
              usePointStyle: true,
              generateLabels: props.generateLegend
            }
          },
          tooltip: {
            mode: 'point',
            usePointStyle: true,
            displayColors: props.showTooltipColor,
            callbacks: {
              title: (tooltipItem: any) => {
                return tooltipItem[0].raw.tooltip || toMMDD(tooltipItem[0].raw.x)
              },
              label: (tooltipItem: any) => {
                if (props.tooltipValueFunc) {
                  return props.tooltipValueFunc(tooltipItem)
                } else {
                  return tooltipItem.raw.y === 0 ? '0' : round(tooltipItem.raw.y, 1000)
                }
              }
            }
          },
          updated: {
            onUpdate: (chart: any) => {
              chartInstance = chart
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: t('statistics.rateChart.rateLabelX')
            },
            min: initRange.minTime,
            max: initRange.maxTime,
            type: 'time',
            time: {
              unit: initRange.unit,
              round: initRange.unit,
              displayFormats: {
                day: 'MM/DD ',
              }
            },
          },
          y: {
            title: {
              display: true,
              text: props.labelY
            },
            min: 0,
            suggestedMax: props.maxX
          },
        } 
      }
    }

    const getChartRange = (): ChartRange => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const maxDate = new Date(today)
      maxDate.setDate(maxDate.getDate() + 2)
      const maxTime = maxDate.getTime()
      let minDate = new Date(today)

      switch (chartRange.value) {
        case 'oneWeek': minDate.setDate(minDate.getDate() - 7); break
        case 'oneMonth': minDate.setMonth(minDate.getMonth() - 1); break
        case 'threeMonths': minDate.setMonth(minDate.getMonth() - 3); break
        case 'sixMonths': minDate.setMonth(minDate.getMonth() - 6); break
        case 'all': minDate = getLaunchDate(3); break
        default: minDate.setMonth(minDate.getMonth() - 1); break
      }
      const minTime = minDate.getTime()
      return {
        minTime: minTime,
        maxTime: maxTime,
        unit: 'day'
      }
    }

    const rangeUpdated = async () => {
      const range = getChartRange()
      if (chartInstance !== undefined) {
        chartInstance.options.scales.x.min = range.minTime
        chartInstance.options.scales.x.max = range.maxTime
        chartInstance.update()
      }
      if (props.userId) {
        store.dispatch('battleStatistics/fetchDailyStatistics', {
          userId: props.userId,
          startDate: range.minTime,
          endDate: range.maxTime
        })
      }
      store.dispatch('battleEnvironment/fetchDailyEnvironemts', {
        startDate: range.minTime,
        endDate: range.maxTime
      })
    }

    return {
      statistics,
      environments,
      chartStyle,
      rangeOptions,
      chartRange,
      options,
      data: chartData as any,
      rangeUpdated
    }
  }
})
</script>

<style scoped>
.chartContainer {
  position: relative;
}
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}
</style>