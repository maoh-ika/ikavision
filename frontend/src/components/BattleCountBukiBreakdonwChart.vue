<template>
  <div :style="chartStyle">
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
import type { BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import type { MainWeapon } from '@/models/Buki'

export default defineComponent({
  name: 'BattleCountBukiBreakdonwChart',
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
    
    const environments = computed(() => {
      return store.getters['battleEnvironment/getSeasonEnvironments']() as BattleEnvironment[]
    })
   
    const data = computed(() => {
      const data: number[] = []
      const colors: string[] = []
      const labels: string[] = []

      const allBukiEnvs = environments.value.map(env => env.bukiEnvironments).flat()
      const bukis = store.getters['battleEnvironment/getAllBukis']() as MainWeapon[]
      const counts: any[] = []
      bukis.forEach(buki => {
        let count = 0
        allBukiEnvs.forEach(env => {
          if (env.buki === buki) {
            count += calcBattleCount(env.battles)
          }
        })
        counts.push({ buki, count })
      })
      counts.sort((a, b) => b.count - a.count)
      counts.forEach(count => {
        const color = getColorByString(count.buki)
        data.push(count.count)
        colors.push(color)
        labels.push(t(`buki.main.${count.buki}`))
      })

      return {
        datasets: [{
          data: data,
          backgroundColor: colors,
          radius: props.radius,
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
      environments,
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