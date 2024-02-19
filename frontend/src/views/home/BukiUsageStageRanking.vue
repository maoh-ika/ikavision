<template>
  <BukiStageRankingTable :make-ranking="makeRanking" :value-column-name="$t('general.avePerBattle')" />
</template>
  
<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
import { calcBattleCount, calcUsageCount } from '@/modules/Environment'
import type { BattleCount, BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import { round } from '@/modules/Utils'
import type { BattleStage } from '@/models/Battle'
import BukiStageRankingTable, { type BukiItem } from './BukiStageRankingTable.vue'
import type { MainWeapon } from '@/models/Buki'

export default defineComponent({
  name: 'BukiUsageStageTable',
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
      const battlesYesterday = calcBattleCount(envYesterday.battles, undefined, stage)
      const battlesDayBefore = calcBattleCount(envDayBefore.battles, undefined, stage)
      if (battlesYesterday === 0 || battlesDayBefore === 0) {
        return 0
      }
      const usageYesterday = calcUsageCount(envYesterday.bukiEnvironments, undefined, stage, buki) / battlesYesterday
      const usageDayBefore = calcUsageCount(envDayBefore.bukiEnvironments, undefined, stage, buki) / battlesDayBefore
      return usageDayBefore === 0 ? 0 : (usageYesterday - usageDayBefore) / usageDayBefore
    }

    
    const makeRanking = (stage: BattleStage): BukiItem[] => {
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
      const battleCount = calcBattleCount(allBattles, undefined, stage)
      const _items: BukiItem[] = []
      allBukis.forEach(buki => {
        const usage = calcUsageCount(allEnvs, undefined, stage, buki)
        const value = battleCount === 0 ? 0 : usage / battleCount
        _items.push({
          bukiId: buki,
          value: round(value, 1000).toString(),
          rocIn24h: calcRoc24h(buki, stage, envYesterday, envDayBefore)
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
</style>