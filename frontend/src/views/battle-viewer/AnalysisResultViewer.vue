<template>
  <div class="column items-center root full-width">
    <DraggableContainer
      v-if="isReady"
      class="row items-start"
      referenceLineColor="#0f0"
      style="max-width: 1400px;"
    >
      <div
        v-for="compConfig in config.components"
        class="relative-position q-ma-sm"
        :class="{'focus': componentFocus[compConfig.component]}"
        :style="{
          width: `${componentSize.width + componentOffsets[compConfig.component].x}px`,
          height: `${componentSize.height + componentOffsets[compConfig.component].y}px`
        }"
        @click="() => focus(compConfig.component)"
      >
        <component :is="compConfig.component"
          :ref="compConfig.component"
          :user-id="userId"
          :job-id="jobId"
          :result-id="resultId"
          :width="componentSize.width - chartMargins[compConfig.component].x"
          :height="componentSize.height - chartMargins[compConfig.component].y"
          :onTimeUpdate="onTimeUpdate"
          :on-dragging="dragging"
          :on-resizing="resizing"
          @vue:mounted="(ctx: any) => onChartMounted(ctx, compConfig.component, compConfig)"
        />
      </div>
    </DraggableContainer>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useStore } from 'vuex'
import { DraggableContainer } from 'vue3-draggable-resizable'
import type { BattleViewerConfig, ComponentConfig, ViewComponent } from '@/modules/BattleViewer'
import BattleMoviePlayer from '@/components/BattleMoviePlayer.vue'
import InkTankLevelChart from '@/components/InkTankLevelChart.vue'
import PlayerNumberBalanceChart from '@/components/PlayerNumberBalanceChart.vue'
import BattleScoreChart from '@/components/BattleScoreChart.vue'
import DeathChart from '@/components/DeathChart.vue'
import SpecialWeaponChart from '@/components/SpecialWeaponChart.vue'

export default defineComponent({
  name: 'AnalysisResultViewer',
  components: {
    DraggableContainer,
    BattleMoviePlayer,
    InkTankLevelChart,
    PlayerNumberBalanceChart,
    BattleScoreChart,
    DeathChart,
    SpecialWeaponChart
  },
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
      type: String
    }
  },
  setup(props) {
    const $q = useQuasar()
    const store = useStore()
    const curTime = ref(0)
    const isReady = ref(false)
    
    const chartRefs: {[key:string]:any} = {}
    const componentSizes = ref<{[key:string]:{width: number, height: number}}>({})
    const componentOffsets = ref<{[key:string]:{x: number, y: number}}>({})
    const componentFocus = ref<{[key:string]:boolean}>({})
    const chartMargins = ref<{[key:string]:{x: number, y: number}}>({})

    onMounted(async () => {
      try {
        $q.loading.show()
        const resPromise = store.dispatch('analysisResult/fetchResult', { userId: props.userId, resultId: props.resultId })
        const jobPromise = store.dispatch('analysisJob/fetchJob', { userId: props.userId, jobId: props.jobId })
        await Promise.all([resPromise, jobPromise])
        isReady.value = true
      } finally {
        $q.loading.hide()
      }
    })

    const pageTitle = computed(() => {
      const job = store.getters['analysisJob/getJob'](props.jobId)
      return job !== undefined ? job.jobName : ''
    })
    
    const config = computed((): BattleViewerConfig => {
      return store.getters['appConfig/getConfig']
    })

    const componentSize = computed(() => {
      const windowWidth = window.innerWidth
      const width = Math.min(windowWidth - 28)
      return {
        width: width,
        height: 360
      }
    })

    config.value.components.forEach(comp => {
      chartRefs[comp.component] = ref()
      componentOffsets.value[comp.component] = {
        x: 0,
        y: 0
      }
      componentFocus.value[comp.component] = false
      chartMargins.value[comp.component] = {
        x: 0,
        y: 0
      }
    })

    const onTimeUpdate = (time: number, component: ViewComponent) => {
      curTime.value = time
      for (const comp in chartRefs) {
        if (comp === component) {
          continue
        }
        if ((comp === 'BattleMoviePlayer' || component === 'BattleMoviePlayer') && !config.value.movieSyncEnabled) {
          continue
        }
        chartRefs[comp].value[0].setTime(time)
      }
    }

    const onChartMounted = (ctx: any, component: ViewComponent, config: ComponentConfig) => {
      const width = ctx.el.offsetWidth
      const height = ctx.el.offsetHeight
      chartMargins.value[component] = {
        x: width - componentSize.value.width,
        y: height - componentSize.value.height
      }
    }

    const focus = (component: ViewComponent) => {
      for (let key in componentFocus.value) {
        componentFocus.value[key] = false
      }
      componentFocus.value[component] = true
    }
    
    const dragging = (payload: { x: number, y: number }, component: ViewComponent) => {
      componentOffsets.value[component] = {
        x: payload.x,
        y: payload.y
      }
    }

    const resizing = (payload: { x: number, y: number, w: number, h: number }, component: ViewComponent) => {
      componentSizes.value[component] = {
        width: payload.w,
        height: payload.h 
      }
    }

    return {
      curTime,
      config,
      isReady,
      pageTitle,
      ...chartRefs,
      componentSize,
      componentOffsets,
      componentFocus,
      chartMargins,
      onTimeUpdate,
      onChartMounted,
      focus,
      dragging,
      resizing
    }
  }
})
</script>

<style scoped>
.parent {
  width: 100%;
  height: 100%; 
  border: 1px solid #000;
  user-select: none;
  position: absolute;
}
.focus {
  z-index: 9;
}
</style>