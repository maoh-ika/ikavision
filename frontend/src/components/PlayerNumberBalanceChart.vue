<template>
  <ChartBase
    ref="base"
    :user-id="userId"
    :job-id="jobId"
    :result-id="resultId"
    :title="$t('viewer.playerMumberBalance.title')"
    :width="width"
    :height="height"
    :chart-area="chartArea"
    :is-ready="isReady"
    :on-dragging="(payload: any) => onDragging(payload, componentName)"
    :on-resizing="(payload: any) => onResizing(payload, componentName)"
  >
    <template v-slot:chart>
      <Line class="baseChart" :data="data" :options="options" :style="{ width: `${width}px`, height: `${height}px`}"/>
      <canvas ref="balanceCanvas" class="overlay" :width="width" :height="height" />
    </template>
  </ChartBase>
 </template>
    
<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { Line } from 'vue-chartjs'
import { BattleTimer } from '@/modules/Battle'
import { toMMSS } from '@/modules/Utils'
import { drawRect, clearCanvas, isContained, toTime } from '@/modules/Chart'
import type { AnalysisResult } from '@/modules/AnalysisResultApi'
import DeathEventOverlay from '@/components/DeathEventOverlay.vue'
import ChartBase from '@/components/ChartBase.vue'

const componentName = 'PlayerNumberBalanceChart'
export default defineComponent({
  name: componentName,
  components: { Line, ChartBase, DeathEventOverlay },
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
    const balanceCanvas = ref()
    const chartArea = ref({ top: 0, bottom: 0, left: 0, right: 0 })
    const options = ref()
    const isReady = ref(false)

    const chartCanvas = ref()

    const evenColor = 'rgba(0,0,0,0.1)'
    const adColor = 'rgba(0,0,255,0.3)'
    const disColor = 'rgba(255,0,0,0.3)'
      

    watch(chartArea, () => {
      drawNumberBalance()
    })

    onMounted(async () => {
      options.value = makeOptions()
      isReady.value = true
    })

    const analysisResult = computed((): AnalysisResult => {
      return store.getters['analysisResult/getResult'](props.resultId)
    })
    
    const battleTimer = new BattleTimer(analysisResult.value)
    
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
                return `${t('viewer.playerMumberBalance.labelY')} ${tooltipItem[0].formattedValue}人`
              },
              label: (tooltipItem: any) => {
                return `${t('viewer.playerMumberBalance.labelX')} ${toMMSS(+tooltipItem.label)}`
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
              text: t('viewer.playerMumberBalance.labelX')
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
              text: t('viewer.playerMumberBalance.labelY')
            },
            min: -4,
            max: 4
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
      const ds_even= {
        label: t('viewer.playerMumberBalance.even'),
        data: [] as any[],
        backgroundColor: evenColor,
      }
      const ds_ad = {
        label: t('viewer.playerMumberBalance.advantage'),
        data: [] as any[],
        backgroundColor: adColor,
      }
      const ds_dis = {
        label: t('viewer.playerMumberBalance.disadvantage'),
        data: [] as any[],
        backgroundColor: disColor,
      }
      const ds_number = {
        label: t('viewer.playerMumberBalance.number'),
        data: [] as any[],
        backgroundColor: 'rgba(75, 192, 192, 1)',
        borderColor: 'rgba(0,0,0,0.2)',
        borderWidth: 1
      }
      analysisResult.value.playerNumberBalanceEvents.forEach(evt => {
        ds_number.data.push({ x: battleTimer.convertFrameToBattleSecond(evt.startFrame), y: evt.teamNumber - evt.enemyNumber })
      })

      return {
        datasets: [ds_even, ds_ad, ds_dis, ds_number],
      }
    })

    const drawNumberBalance = () => {
      if (analysisResult.value === undefined) {
        return
      }

      const toCood = (movieTime: number) => {
        const battleTime = battleTimer.convertMovieSecondToBattleSecond(movieTime)
        return (chartArea.value.right - chartArea.value.left) * battleTime / battleTimer.battleSeconds + chartArea.value.left
      }

      clearCanvas(balanceCanvas.value)

      let lastTime = battleTimer.battleOpenSecond
      analysisResult.value.playerNumberBalanceEvents.forEach(evt => {
        const startTime = battleTimer.convertFrameToMovieSecond(evt.startFrame)
        const endTime = battleTimer.convertFrameToMovieSecond(evt.endFrame)
        const left = toCood(lastTime < startTime ? lastTime : startTime)
        const right = toCood(endTime)
        lastTime = endTime
        let color = evenColor
        if (evt.balanceState === 'advantage') {
          color = adColor
        } else if (evt.balanceState === 'disadvantage') {
          color = disColor
        }
        drawRect(balanceCanvas.value, left, chartArea.value.top, right - left, chartArea.value.bottom - chartArea.value.top, color) 
      })
    }

    const setTime = (movieTime: number) => {
      base.value.setTime(movieTime)
    }

    return {
      componentName,
      chartCanvas,
      base,
      balanceCanvas,
      analysisResult,
      chartArea,
      isReady,
      data,
      options,
      setTime
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
  z-index: 3;
}
</style>