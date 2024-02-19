<template>
  <q-layout view="hhh lpr fff">
    <div class="q-pa-md q-gutter-sm">
      <q-breadcrumbs>
        <q-breadcrumbs-el icon="home" to="/" />
        <q-breadcrumbs-el :label="`${$t('drawer.battleStatistics')}(${$t('general.stage')})`" icon="insights" :to="{name: 'battleStatistics', query: {tab: 'stage'}}" />
        <q-breadcrumbs-el :label="$t(`battleStage.${stage}`)" />
      </q-breadcrumbs>
    </div>
    <q-page class="q-pa-md column items-center root">
      <div class="q-mt-xl full-width column items-center">
        <div class="q-pa-sm cst-rounded-boarder titleLabel">{{ $t(`battleStage.${stage}`) + $t('statistics.stageStatistics.detailTitle') }}</div>
        <div class="q-mt-xl">{{ $t('statistics.bukiStatistics.descDetail') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <StatisticsSammary :user-id="userId" :stage="stage" />
        <div class="q-mt-xl">{{ $t('statistics.bukiStatistics.desc') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <BukiStatisticsTableBreakdown :user-id="userId" :stage="stage" :breakdown-rule-enabled="true"/>
        <div class="q-mt-xl">{{ $t('statistics.ruleStatistics.desc') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <RuleStatisticsTableBreakdown :user-id="userId" :stage="stage" :breakdown-buki-enabled="true" />
      </div>
    </q-page>
  </q-layout>
</template>
  
<script lang="ts">
import { defineComponent, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
import StatisticsSammary from '@/components/StatisticsSammary.vue'
import RuleStatisticsTableBreakdown from '@/components/RuleStatisticsTableBreakdown.vue'
import BukiStatisticsTableBreakdown from '@/components/BukiStatisticsTableBreakdown.vue'

export default defineComponent({
  name: 'StageStatisticsDetail',
  components: {
    StatisticsSammary,
    RuleStatisticsTableBreakdown,
    BukiStatisticsTableBreakdown
  },
  props: {
    userId: {
      type: String
    },
    stage: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const store = useStore()
    const $q = useQuasar()
    const userId = props.userId || store.getters['user/getUserId']
    
    onMounted(async () => {
      try {
        $q.loading.show()
        await store.dispatch('battleStatistics/fetchMasterStatistics', { userId: userId, statisticsId: userId })
      } finally {
        $q.loading.hide()
      }
    })

    return {
      userId
    }
  }
})
</script>

<style scoped>
.titleLabel {
  border-width: 3px ;
  text-align: center;
  border-color: #1d1d1d
}
</style>