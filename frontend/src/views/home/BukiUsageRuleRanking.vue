<template>
  <BukiRuleRankingTable :make-ranking="makeRanking" :value-column-name="$t('general.avePerBattle')" />
</template>
  
<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
import { calcBattleCount, calcUsageCount } from '@/modules/Environment'
import type { BattleCount, BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import { round } from '@/modules/Utils'
import type { BattleRule } from '@/models/Battle'
import BukiRuleRankingTable, { type BukiItem } from './BukiRuleRankingTable.vue'
import type { MainWeapon } from '@/models/Buki'

export default defineComponent({
  name: 'BukiUsageRuleRanking',
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
      const battlesYesterday = calcBattleCount(envYesterday.battles, rule)
      const battlesDayBefore = calcBattleCount(envDayBefore.battles, rule)
      if (battlesYesterday === 0 || battlesDayBefore === 0) {
        return 0
      }
      const usageYesterday = calcUsageCount(envYesterday.bukiEnvironments, rule, undefined, buki) / battlesYesterday
      const usageDayBefore = calcUsageCount(envDayBefore.bukiEnvironments, rule, undefined, buki) / battlesDayBefore
      return usageDayBefore === 0 ? 0 : (usageYesterday - usageDayBefore) / usageDayBefore
    }
    
    const makeRanking = (rule: BattleRule): BukiItem[] => {
      if (seasonEnvironments.value === undefined) {
        return []
      }
      const allBukis = store.getters['battleEnvironment/getAllBukis']() as MainWeapon[]
      const allBattles = store.getters['battleEnvironment/getAllBattles']() as BattleCount[]
      const allEnvs = seasonEnvironments.value.map(env => env.bukiEnvironments).flat()
      const matchType = store.getters['battleEnvironment/getEnvironmentMatchType']
      const matchRate = store.getters['battleEnvironment/getEnvironmentXMatchRate']
      const cacheKeyYesterday = { days: 1, fromNow: false, matchType, matchRate }
      const envYesterday = store.getters['battleEnvironment/getCache'](cacheKeyYesterday) as BattleEnvironment
      const cacheKeyBefore = { days: 2, fromNow: false, matchType, matchRate }
      const envDayBefore = store.getters['battleEnvironment/getCache'](cacheKeyBefore) as BattleEnvironment
      const battleCount = calcBattleCount(allBattles, rule)
      const _items: BukiItem[] = []
      allBukis.forEach(buki => {
        const usage = calcUsageCount(allEnvs, rule, undefined, buki)
        const value = battleCount === 0 ? 0 : usage / battleCount
        _items.push({
          bukiId: buki,
          value: round(value, 1000).toString(),
          rocIn24h: calcRoc24h(buki, rule, envYesterday, envDayBefore)
        })
      })
      _items.sort((a, b) => +b.value - +a.value)
      return _items
    }

    return {
      round,
      makeRanking
    }
  }
})
</script>

<style scoped>
.rowItem {
  font-size: 1rem;
}
.increase {
  color: red;
}
.decrease {
  color: blue;
}
</style>