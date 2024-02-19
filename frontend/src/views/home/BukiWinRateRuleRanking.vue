<template>
  <BukiRuleRankingTable :make-ranking="makeRanking" :value-column-name="$t('general.winRate')" value-unit="%"/>
</template>
  
<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
import { calcWinRate } from '@/modules/Statistics'
import type { BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import { round } from '@/modules/Utils'
import type { BattleRule } from '@/models/Battle'
import BukiRuleRankingTable, { type BukiItem } from './BukiRuleRankingTable.vue'
import type { MainWeapon } from '@/models/Buki'

export default defineComponent({
  name: 'BukiWinRateRuleTable',
  components: { BukiRuleRankingTable },
  setup(props) {
    const store = useStore()

    const seasonEnvironments = computed(() => {
      return store.getters['battleEnvironment/getSeasonEnvironments']() as BattleEnvironment[]
    })
    
    const calcRoc24h = (buki: MainWeapon, rule: BattleRule, envYesterday: BattleEnvironment, envDayBefore: BattleEnvironment): number => {
      if (envYesterday === undefined || envDayBefore === undefined) {
        return 0
      }
      const winRateYesterday = calcWinRate(envYesterday.bukiEnvironments, rule, undefined, buki)
      const winRateDayBefore = calcWinRate(envDayBefore.bukiEnvironments, rule, undefined, buki)
      return winRateDayBefore === 0 ? 0 : (winRateYesterday - winRateDayBefore) / winRateDayBefore
    }
    
    const makeRanking = (rule: BattleRule): BukiItem[] => {
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
        const winRate = calcWinRate(allEnvs, rule, undefined, buki)
        _items.push({
          bukiId: buki,
          value: round(winRate * 100, 10).toString(),
          rocIn24h: calcRoc24h(buki, rule, envYesterday, envDayBefore)
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