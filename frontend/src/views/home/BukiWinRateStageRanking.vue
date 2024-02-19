<template>
  <BukiStageRankingTable :make-ranking="makeRanking" :value-column-name="$t('general.winRate')" value-unit="%" />
</template>
  
<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
import { calcWinRate } from '@/modules/Statistics'
import type { BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import { round } from '@/modules/Utils'
import type { BattleStage } from '@/models/Battle'
import BukiStageRankingTable, { type BukiItem } from './BukiStageRankingTable.vue'
import type { MainWeapon } from '@/models/Buki'

export default defineComponent({
  name: 'BukiWinRateStageTable',
  components: { BukiStageRankingTable },
  setup(props) {
    const store = useStore()

    const seasonEnvironments = computed(() => {
      return store.getters['battleEnvironment/getSeasonEnvironments']() as BattleEnvironment[]
    })
    
    const calcRoc24h = (buki: MainWeapon, stage: BattleStage, envYesterday: BattleEnvironment, envDayBefore: BattleEnvironment): number => {
      if (envYesterday === undefined || envDayBefore === undefined) {
        return 0
      }
      const winRateYesterday = calcWinRate(envYesterday.bukiEnvironments, undefined, stage, buki)
      const winRateDayBefore = calcWinRate(envDayBefore.bukiEnvironments, undefined, stage, buki)
      return winRateDayBefore === 0 ? 0 : (winRateYesterday - winRateDayBefore) / winRateDayBefore
    }
    
    const makeRanking = (stage: BattleStage): BukiItem[] => {
      if (seasonEnvironments.value === undefined) {
        return []
      }
      const allBukis = store.getters['battleEnvironment/getAllBukis']() as MainWeapon[]
      const allEnvs = seasonEnvironments.value.map(env => env.bukiEnvironments).flat()
      const matchType = store.getters['battleEnvironment/getEnvironmentMatchType']
      const matchRate = store.getters['battleEnvironment/getEnvironmentXMatchRate']
      const cacheKeyYesterday = { days: 1, fromNow: false, matchType, matchRate }
      const envYesterday = store.getters['battleEnvironment/getCache'](cacheKeyYesterday) as BattleEnvironment
      const cacheKeyBefore = { days: 2, fromNow: false, matchType, matchRate }
      const envDayBefore = store.getters['battleEnvironment/getCache'](cacheKeyBefore) as BattleEnvironment
      const _items: BukiItem[] = []
      allBukis.forEach(buki => {
        const winRate = calcWinRate(allEnvs, undefined, stage, buki)
        _items.push({
          bukiId: buki,
          value: round(winRate * 100, 10).toString(),
          rocIn24h: calcRoc24h(buki, stage, envYesterday, envDayBefore)
        })
      })
      _items.sort((a, b) => +b.value - +a.value)
      return _items
    }

    return {
      makeRanking
    }
  }
})
</script>

<style scoped>
.rowItem {
  font-size: 1rem;
}
</style>