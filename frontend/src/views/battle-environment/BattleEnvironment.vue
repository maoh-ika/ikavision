<template>
  <q-layout view="hhh lpr fff">
    <div class="q-pa-md q-gutter-sm column">
      <q-breadcrumbs>
        <q-breadcrumbs-el icon="home" to="/" />
        <q-breadcrumbs-el :label="$t('drawer.battleEnvironment')" icon="hive" />
      </q-breadcrumbs>
    </div>
    <q-page class="q-pa-md column">
      <div class="q-px-md q-mb-xl">
        <q-tabs
          v-model="tab"
          narrow-indicator
          dense
          align="justify"
          class="text-primary"
          @update:model-value="updateUrl"
        >
          <q-tab style="max-width: 150px" :ripple="false" name="battles" :label="$t('environment.battlesTab')" />
          <q-tab style="max-width: 150px" :ripple="false" name="usage" :label="$t('environment.usageTab')" />
          <q-tab style="max-width: 150px" :ripple="false" name="winRate" :label="$t('environment.winRateTab')" />
          <q-space/>
        </q-tabs>
      </div>
      <div class="items-center column full-width" v-if="isReady">
        <div v-if="tab === 'battles'" class="row justify-center full-width">
          <div class="column q-mx-sm items-center">
            <SectionTitle :title="$t('environment.battles.allBattles')" :info="$t('environment.battles.infoAllBattles')" />
            <q-separator class="full-width"/>
            <LabelValue :value="allBattleCount.toString()"/>
          </div>
          <div class="column q-mx-sm items-center full-width">
            <BattleCountHistoryChart class="battleCountChart" :width="400" :height="320" :use-env="true" />
          </div>
          <div class="column q-mt-xl q-mx-sm items-center">
            <SectionTitle :title="$t('environment.battles.bukiBreakdown')" :info="$t('environment.battles.infoBukiBreakdown')" />
            <q-separator class="full-width"/>
            <BattleCountBukiBreakdonwChart :width="400" :height="400" :show-legend="false"/>
          </div>
          <div class="column q-mt-xl q-mx-sm items-center">
            <SectionTitle :title="$t('environment.battles.ruleBreakdown')" :info="$t('environment.battles.infoRuleBreakdown')" />
            <q-separator class="full-width"/>
            <BattleCountRuleBreakdonwChart :width="400" :height="400" />
          </div>
          <div class="column q-mt-xl q-mx-sm items-center">
            <SectionTitle :title="$t('environment.battles.stageBreakdown')" :info="$t('environment.battles.infoStageBreakdown')" />
            <q-separator class="full-width"/>
            <BattleCountStageBreakdonwChart :width="400" :height="400" />
          </div>
          <div class="column q-mt-xl q-mx-sm items-center">
            <SectionTitle :title="$t('environment.battles.seasonBreakdown')" :info="$t('environment.battles.infoSeasonBreakdown')" />
            <q-separator class="full-width"/>
            <BattleCountSeasonBreakdonwChart :width="400" :height="400" />
          </div>
        </div>
        <BukiUsageEnvironment v-if="tab === 'usage'"/>
        <BukiWinRateEnvironment v-if="tab === 'winRate'"/>
      </div>
    </q-page>
    
  </q-layout>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { calcBattleCount } from '@/modules/Environment'
import type { BattleCount } from '@/modules/BattleEnvironmentApi'
import BukiUsageEnvironment from './BukiUsageEnvironment.vue'
import BukiWinRateEnvironment from './BukiWinRateEnvironment.vue'
import LabelValue from '@/components/LabelValue.vue'
import SectionTitle from '@/components/SectionTitle.vue'
import BattleCountBukiBreakdonwChart from '@/components/BattleCountBukiBreakdonwChart.vue'
import BattleCountRuleBreakdonwChart from '@/components/BattleCountRuleBreakdonwChart.vue'
import BattleCountStageBreakdonwChart from '@/components/BattleCountStageBreakdonwChart.vue'
import BattleCountSeasonBreakdonwChart from '@/components/BattleCountSeasonBreakdonwChart.vue'
import BattleCountHistoryChart from '@/components/BattleCountHistoryChart.vue'

export default defineComponent({
  name: 'BattleEnvironment',
  components: {
    LabelValue,
    SectionTitle,
    BukiUsageEnvironment,
    BukiWinRateEnvironment,
    BattleCountBukiBreakdonwChart,
    BattleCountRuleBreakdonwChart,
    BattleCountStageBreakdonwChart,
    BattleCountSeasonBreakdonwChart,
    BattleCountHistoryChart
  },
  props: {
    tab: {
      type: String,
      default: 'battles'
    }
  },
  setup(props) {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    const $q = useQuasar()
    const tab = ref(route.query.tab || props.tab)
    const userId = store.getters['user/getUserId']
    const isReady = ref(false)


    onMounted(async () => {
      try {
        $q.loading.show()
        await store.dispatch('battleEnvironment/fetchSeasonEnvironments')
        isReady.value = true
      } finally {
        $q.loading.hide()
      }
    })

    const allBattleCount = computed(() => {
      const battles = store.getters['battleEnvironment/getAllBattles']() as BattleCount[]
      return calcBattleCount(battles)
    })

    const updateUrl = (tab: string) => {
      router.replace({ path: route.path, query: { tab: tab} }) 
    }
    
    return {
      tab,
      userId,
      isReady,
      allBattleCount,
      updateUrl
    }
  }
})
</script>

<style scoped>
.battleCountChart {
  width: 600px;
}
@media screen and (max-width: 767px) {
  .battleCountChart {
    width: 380px;
  }
}
</style>