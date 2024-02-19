<template>
  <PinableCard
    :on-dragging="onDragging"
    :on-resizing="onResizing"
  >
    <template v-slot:title>
      {{ title }}
    </template>
    <template v-slot:actions>
      <q-separator />
      <q-item>
        <q-checkbox
          v-model="movieSyncEnabled"
          :label="$t('viewer.options.movieSync')"
          @update:model-value="movieSyncUpdated"
        />
      </q-item>
      <q-separator/>
      <slot name="actions" />
      <q-item v-if="actions.length > 0" tag="label">
        <q-option-group
          v-model="enabledActions"
          :options="actions"
          type="checkbox"
          @update:model-value="actionsUpdated"
        />
      </q-item>
    </template>
    <template v-slot:content>
      <div class="chartContainer" :style="{ width: `${width}px`, height: `${height}px`}">

        <slot name="chart" />
        <canvas ref="horzLineCanvas" class="overlay" :width="width" :height="height" />

        <DeathEventOverlay
          v-if="analysisResult !== undefined && deathEventEnabled"
          class="overlay"
          :result="analysisResult"
          :area="getEventArea(0, chartDrawArea)"
        />

        <slot name="overlay" />

        <q-inner-loading
          :showing="!isReady"
          label-class="text-teal"
          label-style="font-size: 1.1em"
        />
      </div>
    </template>
  </PinableCard>
 </template>
    
<script lang="ts">
import { defineComponent, ref, computed, toRef, watch, onBeforeUnmount } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { Line } from 'vue-chartjs'
import { BattleTimer } from '@/modules/Battle'
import { drawVertLine } from '@/modules/Chart'
import type { AnalysisResult } from '@/modules/AnalysisResultApi'
import DeathEventOverlay from '@/components/DeathEventOverlay.vue'
import PinableCard from '@/components/PinableCard.vue'

const componentName = 'InkTankLevelChart'
export default defineComponent({
  name: componentName,
  components: { Line, PinableCard, DeathEventOverlay },
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
    title: {
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
    chartArea: {
      type: Object,
      required: true
    },
    actionUpdated: {
      type: Function,
      default: () => {}
    },
    isReady: {
      type: Boolean,
      default: true
    },
    showDeathEvent: {
      type: Boolean,
      default: true
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
    const horzLineCanvas = ref()
    const curTime = ref(0)
    const movieSyncEnabled = ref(store.getters['appConfig/getMovieSyncEnabled'])
    
    const chartDrawArea = toRef(props.chartArea)
    const isReady = toRef(props.isReady)
    const enabledActions = ref([])

    watch(() => props.chartArea, () => {
      chartDrawArea.value = props.chartArea
    })
    watch(() => props.isReady, () => {
      isReady.value = props.isReady
    })
    
    const unsubscribe = store.subscribe((mutation, state) => {
      if (mutation.type === 'appConfig/setMovieSyncEnabled') {
        movieSyncEnabled.value = store.getters['appConfig/getMovieSyncEnabled']
      }
    })
    
    onBeforeUnmount(() => {
      if (unsubscribe) {
        unsubscribe()
      }
    })

    const actions = computed(() => {
      const acts = []
      if (props.showDeathEvent) {
        acts.push({ label: t('viewer.menu.deathEventEnabled'), value: 'deathEventEnabled' })
      }
      return acts
    })

    const deathEventEnabled = computed(() => {
      return props.showDeathEvent && enabledActions.value.find(v => v === 'deathEventEnabled') !== undefined
    })
    
    const analysisResult = computed((): AnalysisResult => {
      return store.getters['analysisResult/getResult'](props.resultId)
    })
        
    const battleTimer = new BattleTimer(analysisResult.value)

    const getEventArea = (eventIndex: number, area: any): number[] => {
      const eventAreaHeightRatio = 0.2
      const height = chartDrawArea.value.bottom - chartDrawArea.value.top
      const areaHeight = height * eventAreaHeightRatio
      const bottom = chartDrawArea.value.bottom - areaHeight * eventIndex
      const top = bottom - areaHeight
      return [
        chartDrawArea.value.left,
        chartDrawArea.value.right,
        top,
        bottom
      ]
    }

    const setTime = (movieTime: number) => {
      const battleTime = battleTimer.convertMovieSecondToBattleSecond(movieTime)
      if (chartDrawArea.value) {
        const x = (chartDrawArea.value.right - chartDrawArea.value.left) * battleTime / battleTimer.battleSeconds + chartDrawArea.value.left
        if (chartDrawArea.value.left <= x && x <= chartDrawArea.value.right) {
          drawVertLine(horzLineCanvas.value, 'red', x, chartDrawArea.value.top, chartDrawArea.value.bottom)
        }
      }
      curTime.value = battleTime
    }

    const getTime = (): number => {
      return curTime.value
    }
    
    const movieSyncUpdated = (enabled: boolean) => {
      store.commit('appConfig/setMovieSyncEnabled', enabled)
    }
    
    const actionsUpdated = (value: string[]) => {
      props.actionUpdated(value)
    }

    return {
      horzLineCanvas,
      analysisResult,
      chartDrawArea,
      isReady,
      enabledActions,
      actions,
      movieSyncEnabled,
      deathEventEnabled,
      getEventArea,
      setTime,
      getTime,
      movieSyncUpdated,
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