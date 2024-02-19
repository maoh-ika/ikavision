<template>
  <HistoryChartBase
    ref="chartBase"
    user-id=""
    :data="data"
    :title="$t('environment.bukiUsage.historyTitle')"
    :label-y="$t('environment.bukiUsage.usageRate')"
    :width="width"
    :height="height"
  />
 </template>
    
<script lang="ts">
import { defineComponent, computed, ref, type PropType } from 'vue'
import { useI18n } from 'vue-i18n'
import { calcBattleCountHistory, calcUsageCountHistory } from '@/modules/Environment'
import type { BattleRule, BattleStage } from '@/models/Battle'
import type { MainWeapon } from '@/models/Buki'
import { getColorByString } from '@/modules/Utils'
import HistoryChartBase from './HistoryChartBase.vue'
import type { BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import { toMMDDHHmm } from '@/modules/Utils'

export default defineComponent({
  name: 'BukiUsageRuleHistoryChart',
  components: { HistoryChartBase },
  props: { 
    width: {
      type: Number
    },
    height: {
      type: Number
    },
    buki: {
      type: String,
      required: true
    },
    stage: {
      type: String
    },
    rules: {
      type: Array as PropType<BattleRule[]>,
      default: () => []
    }
  },
  setup(props) {
    const { t } = useI18n()
    const chartBase = ref()

    const makeData = (color: string, style: string, rule: BattleRule, data: any[]): any => {
      return {
        label: t(`battleRule.${rule}`),
        data: data,
        backgroundColor: color,
        pointBorderColor: 'black',
        pointRadius: 4,
        pointBorderWidth: 1,
        borderColor: 'black',
        borderWidth: 1,
        pointStyle: style
      }
    }

    const data = computed(() => {
      if (chartBase.value?.environments === undefined) {
        return { datasets: [ { data: [] }] }
      }
      
      const datasets: any[] = []
      const envs = chartBase.value.environments as BattleEnvironment[]
      const mainWeapon = props.buki as MainWeapon

      props.rules.forEach(rule => {
        const battleRule = rule as BattleRule
        const battleStage = props.stage as BattleStage
        const battleCountHistory = calcBattleCountHistory(envs, battleRule, battleStage)
        const battleUsageHistory = calcUsageCountHistory(envs, battleRule, battleStage, mainWeapon)
        const data = battleUsageHistory.daily.map((usage, i) => {
          const battleCount = battleCountHistory.total[i].y
          return {
            x: usage.x,
            y: battleCount === 0 ? 0 : usage.y / battleCount,
            tooltip: `${toMMDDHHmm(usage.startTs)} - ${toMMDDHHmm(usage.endTs)}`
          }
        })
        const color = getColorByString(rule)
        datasets.push(makeData(color, 'circle', battleRule, data))
      })
      
      return {
        datasets
      }
    })

    return {
      chartBase,
      data
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