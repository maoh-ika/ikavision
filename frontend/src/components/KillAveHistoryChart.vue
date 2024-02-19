<template>
  <HistoryChartBase
    ref="chartBase"
    :user-id="userId"
    :data="data"
    :title="$t('statistics.sammary.killAveHistory')"
    :label-y="$t('statistics.sammary.killAve')"
    :width="width"
    :height="height"
  />
 </template>
    
<script lang="ts">
import { defineComponent, computed, ref, type PropType } from 'vue'
import { useI18n } from 'vue-i18n'
import { calcKillAveHistory } from '@/modules/Statistics'
import type { BattleRule, BattleStage } from '@/models/Battle'
import type { MainWeapon } from '@/models/Buki'
import HistoryChartBase from './HistoryChartBase.vue'

export default defineComponent({
  name: 'KillAveHistoryChart',
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
      const history = calcKillAveHistory(stats, rule, stage, buki)
      
      const ds_rate = {
        label: t('statistics.rateChart.KillAveTotalLegend'),
        data: history.total,
        backgroundColor: `rgb(255,0,0,1)`,
        pointBorderColor: 'rgba(255,0,0,1)',
        pointRadius: 4,
        pointBorderWidth: 2,
        borderColor: 'rgba(255,0,0,0.2)',
        borderWidth: 1
      }
      
      const ds_rate_daily = {
        label: t('statistics.rateChart.KillAveDailyLegend'),
        data: history.daily,
        backgroundColor: `rgb(0,0,255,1)`,
        pointBorderColor: 'rgba(0,0,255,1)',
        pointRadius: 4,
        pointBorderWidth: 2,
        borderColor: 'rgba(0,0,255,0.2)',
        borderWidth: 1
      }
      
      return {
        datasets: [ds_rate, ds_rate_daily]
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