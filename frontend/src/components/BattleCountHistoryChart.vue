<template>
  <HistoryChartBase
    ref="chartBase"
    :user-id="userId"
    :data="data"
    :title="$t('statistics.sammary.battleCountHisotry')"
    :label-y="$t('statistics.sammary.allBattleCount')"
    :width="width"
    :height="height"
  />
 </template>
    
<script lang="ts">
import { defineComponent, computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { calcBattleCountHistory } from '@/modules/Statistics'
import { calcBattleCountHistory as calcBattleCountHistoryEnv } from '@/modules/Environment'
import type { BattleRule, BattleStage } from '@/models/Battle'
import type { MainWeapon } from '@/models/Buki'
import HistoryChartBase from './HistoryChartBase.vue'
import { toMMDDHHmm } from '@/modules/Utils'

export default defineComponent({
  name: 'BattleCountHistoryChart',
  components: { HistoryChartBase },
  props: { 
    userId: {
      type: String
    },
    rule: {
      type: String
    },
    stage: {
      type: String
    },
    buki: {
      type: String
    },
    width: {
      type: Number,
      required: true
    },
    height: {
      type: Number,
      required: true
    },
    useEnv: {
      type: Boolean
    }
  },
  setup(props) {
    const { t } = useI18n()
    const chartBase = ref()
    
    const data = computed(() => {
      if (chartBase.value?.statistics === undefined) {
        return { datasets: [ { data: [] }] }
      }
      
      const rule = props.rule as BattleRule
      const stage = props.stage as BattleStage
      const buki = props.buki as MainWeapon
      const history = props.useEnv ? calcBattleCountHistoryEnv(chartBase.value.environments, rule, stage) : calcBattleCountHistory(chartBase.value.statistics, rule, stage, buki)
      const data = history.daily.map(d => { return { x: d.x, y: d.y, tooltip: `${toMMDDHHmm(d.startTs)} - ${toMMDDHHmm(d.endTs)}`}})
      
      const ds_rate_daily = {
        label: t('statistics.rateChart.battleCountDailyLegend'),
        data: data,
        backgroundColor: `rgb(0,0,255,1)`,
        pointBorderColor: 'rgba(0,0,255,1)',
        pointRadius: 4,
        pointBorderWidth: 2,
        borderColor: 'rgba(0,0,255,0.2)',
        borderWidth: 1
      }
      
      return {
        datasets: [ds_rate_daily]
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