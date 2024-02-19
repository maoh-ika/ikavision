<template>
  <div>
    <Pie :data="data" :options="options" :style="chartStyle"/>
  </div>
 </template>
    
<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { Pie } from 'vue-chartjs'
import { getColorByString } from '@/modules/Utils'
import { calcBattleCount } from '@/modules/Environment'
import type { BattleEnvironment, BattleCount } from '@/modules/BattleEnvironmentApi'
import type { BattleStage } from '@/models/Battle'

export default defineComponent({
  name: 'BattleCountStageBreakdonwChart',
  components: { Pie },
  props: {
    width: {
      type: Number
    },
    height: {
      type: Number
    },
    radius: {
      type: String,
      default: '100%'
    },
    showLegend: {
      type: Boolean,
      default: true
    }
  },
  setup(props) {
    const store = useStore()
    const { t } = useI18n()
    const options = ref()

    onMounted(async () => {
      options.value = makeOptions()
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
    
    const data = computed(() => {
      const data: number[] = []
      const colors: string[] = []
      const labels: string[] = []

      const envs = store.getters['battleEnvironment/getSeasonEnvironments']() as BattleEnvironment[]
      const counts: any[] = []
      envs.forEach(env => {
        let count = calcBattleCount(env.battles)
        counts.push({ season: env.seasonName, count })
      })
      counts.sort((a, b) => b.count - a.count)
      counts.forEach(count => {
        const color = getColorByString(count.stage)
        data.push(count.count)
        colors.push(color)
        labels.push(count.season)
      })

      return {
        datasets: [{
          data: data,
          backgroundColor: colors,
          radius: props.radius
        }],
        labels: labels
      }
    })
    
    const makeOptions = (): any => {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: props.showLegend,
            position: 'right'
          },
          tooltip: {
            mode: 'point',
            usePointStyle: true
          }
        }
      }
    }

    return {
      chartStyle,
      options,
      data,
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