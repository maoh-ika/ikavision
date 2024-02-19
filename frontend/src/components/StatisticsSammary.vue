<template>
  <div class="full-width column items-center">
    <div class="q-my-md row full-width justify-center">
      <LabelValue :label="$t('statistics.sammary.allBattleCount')" :value="totalBattles">
        <template v-slot:footer>
          <q-btn outline dense @click="() => { showDialog = true; showBattleCountHistory = true }">{{ $t('statistics.history') }}</q-btn>
        </template>
      </LabelValue>
      <LabelValue :label="$t('statistics.winRate')" :value="winRate" unit="%">
        <template v-slot:footer>
          <q-btn outline dense @click="() => { showDialog = true; showWinRateHistory = true }">{{ $t('statistics.history') }}</q-btn>
        </template>
      </LabelValue>
      <LabelValue :label="$t('statistics.sammary.winLoseCount')" :value="winLoseCount">
        <template v-slot:footer>
          <q-btn outline dense @click="() => { showDialog = true; showWinLoseHistory = true }">{{ $t('statistics.history') }}</q-btn>
        </template>
      </LabelValue>
    </div>
    <div class="q-my-md row full-width justify-center">
      <LabelValue :label="$t('statistics.sammary.killAve')" :value="killAve" :unit="`/${$t('general.battle')}`">
        <template v-slot:footer>
          <q-btn outline dense @click="() => { showDialog = true; showKillAveHistory = true }">{{ $t('statistics.history') }}</q-btn>
        </template>
      </LabelValue>
      <LabelValue :label="$t('statistics.sammary.deathAve')" :value="deathAve" :unit="`/${$t('general.battle')}`">
        <template v-slot:footer>
          <q-btn outline dense @click="() => { showDialog = true; showDeathAveHistory = true }">{{ $t('statistics.history') }}</q-btn>
        </template>
      </LabelValue>
      <LabelValue :label="$t('statistics.sammary.spAve')" :value="spAve" :unit="`/${$t('general.battle')}`">
        <template v-slot:footer>
          <q-btn outline dense @click="() => { showDialog = true; showSpAveHistory = true }">{{ $t('statistics.history') }}</q-btn>
        </template>
      </LabelValue>
    </div>
    <q-dialog v-model="showDialog" @hide="closeDialog">
      <q-card :style="{maxWidth: 'fit-content', maxHeight: 'fit-content'}">
        <q-card-section class="row items-center q-pb-none">
          <q-space />
          <q-btn icon="close" flat round dense @click="() => showDialog = false"/>
        </q-card-section>
        <q-card-section class="q-pa-none">
          <BattleCountHistoryChart v-if="showBattleCountHistory" :user-id="userId" :rule="rule" :stage="stage" :buki="buki" :width="640" :height="320" />
          <WinRateHisotryChart v-else-if="showWinRateHistory" :user-id="userId" :rule="rule" :stage="stage" :buki="buki" :width="640" :height="320" />
          <WinLoseCountHistoryChart v-else-if="showWinLoseHistory" :user-id="userId" :rule="rule" :stage="stage" :buki="buki" :width="640" :height="320" />
          <KillAveHistoryChart v-else-if="showKillAveHistory" :user-id="userId" :rule="rule" :stage="stage" :buki="buki" :width="640" :height="320" />
          <DeathAveHistoryChart v-else-if="showDeathAveHistory" :user-id="userId" :rule="rule" :stage="stage" :buki="buki" :width="640" :height="320" />
          <SpAveHistoryChart v-else-if="showSpAveHistory" :user-id="userId" :rule="rule" :stage="stage" :buki="buki" :width="640" :height="320" />
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>
  
<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useStore } from 'vuex'
import {
  calcBattleCount,
  calcWinRate,
  calcWinLoseCount,
  calcKillAve,
  calcDeathAve,
  calcSpAve
} from '@/modules/Statistics'
import LabelValue from '@/components/LabelValue.vue'
import WinRateHisotryChart from './WinRateHisotryChart.vue'
import BattleCountHistoryChart from './BattleCountHistoryChart.vue'
import WinLoseCountHistoryChart from './WinLoseCountHistoryChart.vue'
import KillAveHistoryChart from './KillAveHistoryChart.vue'
import DeathAveHistoryChart from './DeathAveHistoryChart.vue'
import SpAveHistoryChart from './SpAveHistoryChart.vue'
import type { BattleStatistics } from '@/modules/BattleStatisticsApi'
import type { BattleRule, BattleStage } from '@/models/Battle'
import type { MainWeapon } from '@/models/Buki'

export default defineComponent({
  name: 'StatisticsSammary',
  components: {
    LabelValue,
    BattleCountHistoryChart,
    WinRateHisotryChart,
    WinLoseCountHistoryChart,
    KillAveHistoryChart,
    DeathAveHistoryChart,
    SpAveHistoryChart
  },
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
    }
  },
  setup(props) {
    const store = useStore()
    const showDialog = ref(false)
    const showBattleCountHistory = ref(false)
    const showWinRateHistory = ref(false)
    const showWinLoseHistory = ref(false)
    const showKillAveHistory = ref(false)
    const showDeathAveHistory = ref(false)
    const showSpAveHistory = ref(false)
      
    const rule = props.rule as BattleRule
    const stage = props.stage as BattleStage
    const buki = props.buki as MainWeapon
    
    const statistics = computed(() => {
      return store.getters['battleStatistics/getMasterStatistics'](props.userId) as BattleStatistics
    })

    const totalBattles = computed(() => {
      return statistics.value === undefined ? undefined : calcBattleCount(statistics.value.bukiPerformances, rule, stage, buki).toString()
    })

    const winRate = computed(() => {
      return statistics.value === undefined ? undefined : `${(Math.round(calcWinRate(statistics.value.bukiPerformances, rule, stage, buki) * 1000) / 10)}`
    })
    
    const winLoseCount = computed(() => {
      if (statistics.value === undefined) {
         return undefined
      }
      const winLoseCount = calcWinLoseCount(statistics.value.bukiPerformances, rule, stage, buki)
      return `${winLoseCount[0]}/${winLoseCount[1]}`
    })
    
    const killAve = computed(() => {
      return statistics.value === undefined ? undefined : `${(Math.round(calcKillAve(statistics.value.bukiPerformances, rule, stage, buki) * 10) / 10)}`
    })
    
    const deathAve = computed(() => {
      return statistics.value === undefined ? undefined : `${(Math.round(calcDeathAve(statistics.value.bukiPerformances, rule, stage, buki) * 10) / 10)}`
    })
    
    const spAve = computed(() => {
      return statistics.value === undefined ? undefined : `${(Math.round(calcSpAve(statistics.value.bukiPerformances, rule, stage, buki) * 10) / 10)}`
    })

    const closeDialog = () => {
      showBattleCountHistory.value = false
      showWinRateHistory.value = false
      showWinLoseHistory.value = false
      showKillAveHistory.value = false
      showDeathAveHistory.value = false
      showSpAveHistory.value = false
    }
  
    return {
      showDialog,
      showBattleCountHistory,
      showWinRateHistory,
      showWinLoseHistory,
      showKillAveHistory,
      showDeathAveHistory,
      showSpAveHistory,
      totalBattles,
      winRate,
      winLoseCount,
      killAve,
      deathAve,
      spAve,
      closeDialog
    }
  }
})
</script>

<style scoped>
.itemContainer{
  background-color: white;
  border: solid 0px lightgray;
  color: black;
  text-align: center;
  min-width: 20%;
}
.itemLabel {
  font-size: 1.6rem;
}
.itemValue {
  font-size: 6.4rem;
}
.itemUnit {
  font-size: 1.6rem;
}
</style>