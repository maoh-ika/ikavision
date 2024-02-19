<template>
  <ChartBase
    ref="base"
    :user-id="userId"
    :job-id="jobId"
    :result-id="resultId"
    :title="chartTitle"
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
  </ChartBase>
 </template>
    
<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { Line } from 'vue-chartjs'
import { BattleTimer } from '@/modules/Battle'
import { toMMSS } from '@/modules/Utils'
import { isContained, toTime } from '@/modules/Chart'
import type { AnalysisResult } from '@/modules/AnalysisResultApi'
import ChartBase from '@/components/ChartBase.vue'

const componentName = 'BattleScoreChart'
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
    
    onMounted(async () => {
      options.value = makeOptions()
      isReady.value = true
    })

    const analysisResult = computed((): AnalysisResult => {
      return store.getters['analysisResult/getResult'](props.resultId)
    })
    
    const chartTitle = computed(() => {
      return analysisResult.value.rule === 'nawabari' ? t('viewer.battleCount.titleNawabari') : t('viewer.battleCount.titleGachi')
    })

    const chartLabelY = computed(() => {
      return analysisResult.value.rule === 'nawabari' ? t('viewer.battleCount.labelYNawabari') : t('viewer.battleCount.labelYGachi')
    })
    
    const makeOptions = (): any => {
      const battleTimer = new BattleTimer(analysisResult.value!)
      const ops: any = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true
          },
          tooltip: {
            mode: 'index',
            callbacks: {
              title: (tooltipItem: any) => {
                return `${t('viewer.battleCount.title')}`
              },
              label: (tooltipItem: any) => {
                const time = base.value.getTime()
                const data = [...tooltipItem.dataset.data].reverse()
                const item = data.find(d => d.x <= time)
                const value = item !== undefined ? item.y : ''
                return `${tooltipItem.dataset.label} ${value}`
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
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: t('viewer.battleCount.labelX')
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
              text: chartLabelY.value
            },
            min: 0,
            max: analysisResult.value.rule === 'nawabari' ? undefined : 100
          },
        }   
      }
      return ops
    }
    
    const data = computed(() => {
      if (
          analysisResult.value === undefined ||
          analysisResult.value.teamCountEvents === undefined ||
          analysisResult.value.enemyCountEvents === undefined) {
        return {
          datasets: [ { data: [] }]
        }
      }
      
      const battleTimer = new BattleTimer(analysisResult.value)
      const teamData: any[] = []
      analysisResult.value.teamCountEvents.forEach(evt => {
        teamData.push({ x: battleTimer.convertFrameToBattleSecond(evt.startFrame), y: evt.count })
      })
      const enemyData : any[] = []
      analysisResult.value.enemyCountEvents.forEach(evt => {
        enemyData.push({ x: battleTimer.convertFrameToBattleSecond(evt.startFrame), y: evt.count })
      })

      const ds_team = {
        label: t('viewer.battleCount.teamLegend'),
        data: teamData,
        backgroundColor: `rgb(${analysisResult.value.teamColor.join(',')})`,
        borderColor: 'rgba(0,0,0,0.2)',
        borderWidth: 1
      }
      const ds_enemy = {
        label: t('viewer.battleCount.enemyLegend'),
        data: enemyData,
        backgroundColor: `rgb(${analysisResult.value.enemyColor.join(',')})`,
        borderColor: 'rgba(0,0,0,0.2)',
        borderWidth: 1
      }

      return {
        datasets: [ds_team, ds_enemy],
      }
    })

    const setTime = (movieTime: number) => {
      base.value.setTime(movieTime)
    }

    return {
      componentName,
      base,
      subInkCanvas,
      analysisResult,
      chartArea,
      isReady,
      data,
      options,
      chartTitle,
      setTime,
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