<template>
  <HistoryChartBase
    ref="chartBase"
    :user-id="userId"
    :data="data"
    :title="$t('statistics.sammary.winLoseHistory')"
    :label-y="$t('statistics.sammary.allBattleCount')"
    :width="width"
    :height="height"
  />
 </template>
    
<script lang="ts">
import { defineComponent, computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { calcWinLoseCountHistory } from '@/modules/Statistics'
import type { BattleRule, BattleStage } from '@/models/Battle'
import type { MainWeapon } from '@/models/Buki'
import HistoryChartBase from './HistoryChartBase.vue'

export default defineComponent({
  name: 'WinLoseCountHistoryChart',
  components: { HistoryChartBase },
  props: { 
    userId: {
      type: String,
      required: true
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
      const stats = chartBase.value.statistics
      const [winHisotry, loseHistory] = calcWinLoseCountHistory(stats, rule, stage, buki)
      
      const ds_win = {
        label: t('statistics.rateChart.winCountTotalLegend'),
        data: winHisotry.total,
        backgroundColor: `rgb(255,0,0,1)`,
        pointBorderColor: 'rgba(255,0,0,1)',
        pointRadius: 4,
        pointBorderWidth: 2,
        borderColor: 'rgba(255,0,0,0.2)',
        borderWidth: 1
      }
      
      const ds_lose = {
        label: t('statistics.rateChart.loseCountDailyLegend'),
        data: loseHistory.total,
        backgroundColor: `rgb(0,0,255,1)`,
        pointBorderColor: 'rgba(0,0,255,1)',
        pointRadius: 4,
        pointBorderWidth: 2,
        borderColor: 'rgba(0,0,255,0.2)',
        borderWidth: 1
      }
      
      return {
        datasets: [ds_win, ds_lose]
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