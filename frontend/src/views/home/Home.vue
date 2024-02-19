<template>
  <q-layout view="hHh lpR fFf">
  <q-page class="q-pa-md column items-center">
    <div class="row full-width q-mb-xl">
      <div class="full-width text-center">
        <div class="text-accent text-weight-bolder" :class="isSmallDevice() ? 'text-h2' : 'text-h1'">{{ $t('home.lead1') }}</div>
        <div class="text-accent text-weight-bolder" :class="isSmallDevice() ? 'text-h2' : 'text-h1'">{{ $t('home.lead2') }}</div>
        <div class="row" style="align-items: flex-end;">
          <!--<div class="q-pa-xs q-ml-sm text-accent text-weight-bolder cst-rounded-boarder" :style="{ border: '3px solid', width: 'fit-content' }">{{ $t(('general.testType')) }}</div>-->
        </div>
        <div class="text-accent q-mt-sm">{{ $t('home.lead3') }}</div>
      </div>
    </div>
    <div class="full-width column items-center justify-center q-mb-lg relative-position">
      <SectionTitle :title="$t('home.allBattles')" />
      <LabelValue :value="allBattleCount.toString()"/>
      <q-btn
        class="detailButton"
        text-color="primary"
        outline
        :label="$t('home.ranking.goBattleSearch')"
        no-caps
        @click="goBattleSearch"
      />
      <q-inner-loading
          :showing="!isReady"
          label-class="text-teal"
          label-style="font-size: 1.1em"
      />
    </div>
    <div class="full-width column">
      <SectionTitle class="justify-center q-mb-sm" :title="$t('home.ranking.newArrrivals')" />
      <NewArrivalBattles />
      <q-btn
        class="detailButton"
        text-color="primary"
        outline
        :label="$t('home.ranking.goBattleList')"
        no-caps
        @click="goBattleList"
      />
    </div>

    <q-separator class="full-width q-my-md"/>

    <div class="full-width column">
      <SectionTitle class="justify-center q-mb-sm" :title="$t('home.ranking.usageRule')" :info="$t('environment.bukiUsage.infoRuleBased')" />
      <BukiUsageRuleRanking />
      <q-btn
        class="detailButton"
        text-color="primary"
        :label="$t('home.ranking.goDetail')"
        no-caps
        outline
        @click="goUsageRuleDetail"
      />
    </div>
      
    <q-separator class="full-width q-my-md"/>
    
    <div class="full-width column">
      <SectionTitle class="justify-center q-mb-sm" :title="$t('home.ranking.usageStage')" :info="$t('environment.bukiUsage.infoStageBased')" />
      <BukiUsageStageRanking />
      <q-btn
        class="detailButton"
        text-color="primary"
        :label="$t('home.ranking.goDetail')"
        no-caps
        outline
        @click="goUsageStageDetail"
      />
    </div>

    <q-separator class="full-width q-my-md"/>
    
    <div class="full-width column">
      <SectionTitle class="justify-center q-mb-sm" :title="$t('home.ranking.winRateRule')" />
      <BukiWinRateRuleRanking />
      <q-btn
        class="detailButton"
        text-color="primary"
        :label="$t('home.ranking.goDetail')"
        no-caps
        outline
        @click="goWinRateRuleDetail"
      />
    </div>

    <q-separator class="full-width q-my-md"/>
    
    <div class="full-width column">
      <SectionTitle class="justify-center q-mb-sm" :title="$t('home.ranking.winRateStage')" />
      <BukiWinRateStageRanking />
      <q-btn
        class="detailButton"
        text-color="primary"
        :label="$t('home.ranking.goDetail')"
        no-caps
        outline
        @click="goWinRateStageDetail"
      />
    </div>
  </q-page>
</q-layout>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import SectionTitle from '@/components/SectionTitle.vue'
import LabelValue from '@/components/LabelValue.vue'
import type { BattleCount, BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import { calcBattleCount } from '@/modules/Environment'
import { toHash, isSmallDevice } from '@/modules/Utils'
import { calcSeasonEnvironmentDaysBefore } from '@/modules/Environment'
import NewArrivalBattles from './NewArrivalBattles.vue'
import BukiUsageRuleRanking from './BukiUsageRuleRanking.vue'
import BukiUsageStageRanking from './BukiUsageStageRanking.vue'
import BukiWinRateRuleRanking from './BukiWinRateRuleRanking.vue'
import BukiWinRateStageRanking from './BukiWinRateStageRanking.vue'

export default defineComponent({
  name: 'Home',
  components: {
    SectionTitle,
    LabelValue,
    NewArrivalBattles,
    BukiUsageRuleRanking,
    BukiUsageStageRanking,
    BukiWinRateRuleRanking,
    BukiWinRateStageRanking
  },
  setup() {
    const store = useStore()
    const $q = useQuasar()
    const router = useRouter()
    const isReady = ref(false)
    
    onMounted(async () => {
      try {
        $q.loading.show()
        await store.dispatch('battleEnvironment/fetchSeasonEnvironments')
        const latestEnv = store.getters['battleEnvironment/getSeasonEnvironments']('latest') as BattleEnvironment[]
        const today = latestEnv.length === 0 ? new Date() : new Date(latestEnv[0].latestBattleDate)
        const dayBefore = new Date(today)
        dayBefore.setDate(dayBefore.getDate() - 2)
        await store.dispatch('battleEnvironment/fetchDailyEnvironemts', {
          startDate: dayBefore.getTime(),
          endDate: today.getTime()
        })
        const matchType = store.getters['battleEnvironment/getEnvironmentMatchType']
        const matchRate = store.getters['battleEnvironment/getEnvironmentXMatchRate']
        for (const days of [1, 2]) {
          const params = { days: days, fromNow: false, matchType, matchRate }
          let cacheKey = toHash(params)
          if (store.getters['battleEnvironment/getCache'](cacheKey) === undefined) {
            const env = await calcSeasonEnvironmentDaysBefore(params.days, params.fromNow)
            store.commit('battleEnvironment/setCache', { cacheKey, env })
          }
        }
        isReady.value = true
      } finally {
        $q.loading.hide()
      }
    })
    
    const allBattleCount = computed(() => {
      const battles = store.getters['battleEnvironment/getAllBattles']() as BattleCount[]
      return calcBattleCount(battles)
    })

    const goBattleSearch = () => {
      router.push({ name: 'battleSearch' })
    }
    
    const goBattleList = () => {
      router.push({ name: 'battleList' })
    }

    const goUsageRuleDetail =  () => {
      router.push({ name: 'battleEnvironment', query: { tab: 'usage', section: 'rule' } })
    }
    
    const goUsageStageDetail =  () => {
      router.push({ name: 'battleEnvironment', query: { tab: 'usage', section: 'stage' } })
    }
    
    const goWinRateRuleDetail =  () => {
      router.push({ name: 'battleEnvironment', query: { tab: 'winRate', section: 'rule' } })
    }
    
    const goWinRateStageDetail =  () => {
      router.push({ name: 'battleEnvironment', query: { tab: 'winRate', section: 'stage' } })
    }

    return {
      isReady,
      allBattleCount,
      isSmallDevice,
      goBattleSearch,
      goBattleList,
      goUsageRuleDetail,
      goUsageStageDetail,
      goWinRateRuleDetail,
      goWinRateStageDetail
    }
  }
})
</script>

<style scoped>
.detailButton {
  width: fit-content;
  margin: 8px auto;
}
</style>
