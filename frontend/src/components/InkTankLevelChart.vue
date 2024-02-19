<template>
  <ChartBase
    ref="base"
    :user-id="userId"
    :job-id="jobId"
    :result-id="resultId"
    :title="$t('viewer.inkLevel.title')"
    :width="width"
    :height="height"
    :chart-area="chartArea"
    :is-ready="isReady"
    :on-dragging="(payload: any) => onDragging(payload, componentName)"
    :on-resizing="(payload: any) => onResizing(payload, componentName)"
  >
    <template v-slot:chart>
      <Line class="baseChart" :data="data" :options="options" :style="{ width: `${width}px`, height: `${height}px`}"/>
    </template>
    <template v-slot:actions>
      <q-item tag="label">
        <q-option-group
          v-model="enabledActions"
          :options="actions"
          type="checkbox"
          @update:model-value="actionsUpdated"
        />
      </q-item>
    </template>
    <template v-slot:overlay>
      <canvas
        v-show="analysisResult !== undefined"
        ref="subInkCanvas"
        class="overlay"
        :width="width"
        :height="height" />
    </template>
  </ChartBase>
 </template>
    
<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { Line } from 'vue-chartjs'
import type { Buki } from '@/models/Buki'
import { BattleTimer } from '@/modules/Battle'
import { drawHorzLine, clearCanvas, isContained, toTime } from '@/modules/Chart'
import { toMMSS } from '@/modules/Utils'
import type { AnalysisResult } from '@/modules/AnalysisResultApi'
import { CandleChart } from '@/modules/CandleChart'
import ChartBase from '@/components/ChartBase.vue'

const componentName = 'InkTankLevelChart'
export default defineComponent({
  name: componentName,
  components: { Line, ChartBase },
  props: {
    userId: {
      type: String,
      required: true
    },
    jobId: {
      type: String,
      required: true
    },
    resultId: {
      type: String,
      required: true
    },
    width: {
      type: Number,
      required: true
    },
    height: {
      type: Number,
      required: true
    },
    onTimeUpdate: {
      type: Function,
      default: () => {}
    },
    onDragging: {
      type: Function,
      default: () => {}
    },
    onResizing: {
      type: Function,
      default: () => {}
    }
  },
  setup(props) {
    const store = useStore()
    const { t } = useI18n()
    const base = ref()
    const subInkCanvas = ref()
    const chartArea = ref({ top: 0, bottom: 0, left: 0, right: 0 })
    const options = ref()
    const isReady = ref(false)

    const enabledActions = ref(['subWeaponInkConsumptionEnabled'])
    
    const subInkColor = 'rgba(0,0,255,0.3)'
    
    const actions = [
      { label: t('viewer.inkLevel.subWeaponInk'), value: 'subWeaponInkConsumptionEnabled' },
    ]

    onMounted(async () => {
      options.value = makeOptions()
      isReady.value = true
    })

    const analysisResult = computed((): AnalysisResult => {
      return store.getters['analysisResult/getResult'](props.resultId)
    })

    const battleTimer = new BattleTimer(analysisResult.value)

    const buki = computed((): Buki | undefined => {
      if (analysisResult.value === undefined) {
        return undefined
      }
      return analysisResult.value.teamBukis[analysisResult.value.mainPlayerIndex]
    })
    
    const subWeaponInkConsumptionEnabled = computed(() => {
      return enabledActions.value.find(v => v === 'subWeaponInkConsumptionEnabled') !== undefined && buki.value !== undefined
    })
    
    const makeOptions = (): any => {
      const ops: any = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            labels: {
              usePointStyle: true,
            }
          },
          tooltip: {
            mode: 'index',
            callbacks: {
              title: (tooltipItem: any) => {
                return `${t('viewer.inkLevel.title')} ${tooltipItem[0].formattedValue}%`
              },
              label: (tooltipItem: any) => {
                return `${t('viewer.inkLevel.labelX')} ${toMMSS(+tooltipItem.label)}`
              }
            }
          },
          hover: {
            onHover: (x: number, y: number, xAxis: any, yAxis: any) => {
              if (isContained(chartArea.value, x, y)) {
                const time = toTime(x, xAxis)
                const movieTime = battleTimer.convertBattleSecondToMovieSecond(time)
                base.value.setTime(movieTime)
                props.onTimeUpdate(movieTime, componentName)
              }
            }
          },
          updated: {
            onUpdate: (chart: any) => {
              chartArea.value = { ...chart.chartArea }
              actionsUpdated(enabledActions.value)
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: t('viewer.inkLevel.labelX')
            },
            min: battleTimer.convertFrameToBattleSecond(analysisResult.value.battleOpenFrame),
            max: battleTimer.convertFrameToBattleSecond(analysisResult.value.battleEndFrame),
            type: 'linear',
            ticks: {
              callback: (value: number, index: number, values: any) => {
                return toMMSS(value)
              }
            }
          },
          y: {
            title: {
              display: true,
              text: t('viewer.inkLevel.labelY')
            },
            min: 0,
            max: 100
          },
        }   
      }
      return ops
    }

    const data = computed(() => {
      if (analysisResult.value === undefined) {
        return {
          datasets: [ { data: [{ x: 0, y: 0 }, { x: 0, y: 0 }] }]
        }
      }

      //const candleChart = new CandleChart(1)
      const candleChart = new CandleChart(analysisResult.value.frameRate)
      analysisResult.value.inkTankStates.forEach(ink => {
        candleChart.addValue({
          value: ink.inkLevel * 100,
          frame: ink.frame
        })
      })
      const battleTimer = new BattleTimer(analysisResult.value)

      const dataPoints: any[] = candleChart.candles.filter(c => c.values.length > 0).map(candle => {
        return {
          x: battleTimer.convertFrameToBattleSecond((candle.startFrame + candle.endFrame) / 2),
          y: Math.round(candle.average)
        }
      })

      const ds_main_ink = {
        label: t('viewer.inkLevel.mainWeaponLegend'),
        data: dataPoints,
        backgroundColor: `rgb(${analysisResult.value.teamColor.join(',')})`,
        borderColor: 'rgba(0,0,0,0.2)',
        borderWidth: 1
      }
      
      const datasets: any[] = [ds_main_ink]
      if (subWeaponInkConsumptionEnabled.value) {

        const ds_sub_ink = {
          label: `${t('viewer.inkLevel.subWeaponLegend')}(${t('buki.sub.' + buki.value!.subWeapon)})`,
          data: [] as any[],
          backgroundColor: subInkColor,
        }

        datasets.push(ds_sub_ink)
      }

      return {
        datasets: datasets
      }
    })

    const drawSubWeaponInk = () => {
      if (buki.value === undefined || chartArea.value === undefined) {
        return
      }
      const subConsumption = buki.value.subInkConsumption / 100
      const y = chartArea.value.bottom - (chartArea.value.bottom - chartArea.value.top) * subConsumption
      drawHorzLine(subInkCanvas.value, subInkColor, y, chartArea.value.left, chartArea.value.right, 2)
    }

    const actionsUpdated = (value: string[]) => {
      if (subWeaponInkConsumptionEnabled.value) {
        drawSubWeaponInk()
      } else {
        clearCanvas(subInkCanvas.value)
      }
    }
    
    const setTime = (time: number) => {
      base.value.setTime(time)
    }

    return {
      componentName,
      base,
      subInkCanvas,
      analysisResult,
      chartArea,
      isReady,
      enabledActions,
      actions,
      subWeaponInkConsumptionEnabled,
      data,
      options,
      setTime,
      actionsUpdated
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
.baseChart {
  position: absolute;
  top: 0;
  left: 0;
}
</style>