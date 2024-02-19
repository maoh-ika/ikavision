<template>
  <ChartBase
    ref="base"
    :user-id="userId"
    :job-id="jobId"
    :result-id="resultId"
    :title="$t('viewer.death.title')"
    :width="width"
    :height="height"
    :chart-area="chartArea"
    :is-ready="isReady"
    :show-death-event="false"
    :on-dragging="(payload: any) => onDragging(payload, componentName)"
    :on-resizing="(payload: any) => onResizing(payload, componentName)"
  >
    <template v-slot:chart>
      <Bubble class="baseChart" :data="data" :options="options" :style="{ width: `${width}px`, height: `${height}px`}"/>
    </template>
  </ChartBase>
 </template>
    
<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { Bubble } from 'vue-chartjs'
import { BattleTimer } from '@/modules/Battle'
import { toMMSS } from '@/modules/Utils'
import { isContained, toTime } from '@/modules/Chart'
import type { AnalysisResult } from '@/modules/AnalysisResultApi'
import ChartBase from '@/components/ChartBase.vue'

const componentName = 'DeathChart'
export default defineComponent({
  name: componentName,
  components: { Bubble, ChartBase },
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
    
    const battleTimer = new BattleTimer(analysisResult.value)
    
    const makeOptions = (): any => {
      const battleTimer = new BattleTimer(analysisResult.value!)
      const teamCount = analysisResult.value !== undefined ? analysisResult.value.team.length : 4
      const enemyCount = analysisResult.value !== undefined ? analysisResult.value.enemy.length : 4
      const ops: any = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            labels: {
              usePointStyle: true
            }
          },
          tooltip: {
            mode: 'point',
            displayColors: false,
            callbacks: {
              title: (tooltipItem: any) => {
                const time = base.value.getTime()
                return `${t('viewer.death.labelX')} ${toMMSS(time)}`
              },
              label: (tooltipItem: any) => {
                if (analysisResult.value === undefined) {
                  return ''
                }
                const index = tooltipItem.raw.y
                if (index < enemyCount) {
                  return t(`buki.main.${analysisResult.value.enemyBukis[(enemyCount - 1) - index].mainWeapon}`)
                } else {
                  const idx = index - enemyCount
                  return t(`buki.main.${analysisResult.value.teamBukis[(teamCount - 1) - idx].mainWeapon}`)
                }
              },
              footer: () => {
                return ''
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
              text: t('viewer.death.labelX')
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
              text: t('viewer.death.labelY')
            },
            ticks: {
              callback: function(value: number, index: number, values: number[]) {
                if (index === 0 || index === teamCount + enemyCount + 1) {
                  return ''
                }
                const valueIndex = index - 1 // index starts with -1 value
                if (analysisResult.value !== undefined) {
                  if (valueIndex < enemyCount) {
                    return analysisResult.value.enemy[(enemyCount - 1) - valueIndex].name
                  } else {
                    const idx = valueIndex - enemyCount
                    if (idx < teamCount) {
                      return analysisResult.value.team[(teamCount - 1) - idx].name
                    }
                  }
                }
                return 'unknown'
              },
              color: function(context: any) {
                if (analysisResult.value !== undefined) {
                  const valueIndex = context.index - 1 // index starts with -1 value
                  if (valueIndex < analysisResult.value.team.length) {
                    return `rgb(${analysisResult.value.enemyColor.join(',')})`
                  } else {
                    return `rgb(${analysisResult.value.teamColor.join(',')})`
                  }
                }
                return 'black'
              },
              font: {
                size: 14
              }
            },
            grid: {
              color: function(context: any) {
                if (context.index === 0 || context.index === teamCount + enemyCount + 1) {
                  return 'black'
                }
                if (analysisResult.value !== undefined) {
                  const valueIndex = context.index - 1 // index starts with -1 value
                  if (valueIndex < analysisResult.value.team.length) {
                    return `rgb(${analysisResult.value.enemyColor.join(',')})`
                  } else {
                    return `rgb(${analysisResult.value.teamColor.join(',')})`
                  }
                }
                return 'black'
              }
            },
            suggestedMin: -1,
            suggestedMax: teamCount + enemyCount,
          },
        }   
      }
      return ops
    }
    
    const data = computed(() => {
      if (analysisResult.value === undefined) {
        return { datasets: [ { data: [] }] }
      }
      const battleTimer = new BattleTimer(analysisResult.value)
      
      const teamData: any[] = []
      analysisResult.value.deathEvents.forEach(evt => {
        if (evt.deathPlayerSide === 'team') {
          const value = ((analysisResult.value!.team.length - 1)- evt.deathPlayerIndex) + analysisResult.value!.enemy.length
          teamData.push({ x: battleTimer.convertFrameToBattleSecond(evt.startFrame), y: value, r: 6 })
        }
      })

      const enemyData: any[] = []
      analysisResult.value.deathEvents.forEach(evt => {
        if (evt.deathPlayerSide === 'enemy') {
          const value = (analysisResult.value!.enemy.length - 1) - evt.deathPlayerIndex
          enemyData.push({ x: battleTimer.convertFrameToBattleSecond(evt.startFrame), y: value, r: 6 })
        }
      })
      
      const ds_team = {
        label: t('viewer.death.teamLegend'),
        data: teamData,
        backgroundColor: `rgb(${analysisResult.value.teamColor.join(',')})`,
        borderColor: 'rgba(0,0,0,0.2)',
        borderWidth: 1
      }
      const ds_enemy = {
        label: t('viewer.death.enemyLegend'),
        data: enemyData,
        backgroundColor: `rgb(${analysisResult.value.enemyColor.join(',')})`,
        borderColor: 'rgba(0,0,0,0.2)',
        borderWidth: 1
      }
      
      return { datasets: [ds_team, ds_enemy] }
    })

    const setTime = (movieTime: number) => {
      base.value.setTime(movieTime)
    }

    return {
      componentName,
      base,
      analysisResult,
      chartArea,
      isReady,
      data,
      options,
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