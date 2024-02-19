<template>
  <q-layout view="hhh lpr fff">
    <div class="q-pa-md q-gutter-sm">
      <q-breadcrumbs>
        <q-breadcrumbs-el icon="home" to="/" />
        <q-breadcrumbs-el :label="`${$t('drawer.battleStatistics')}(${$t('general.rule')})`" icon="insights" :to="{name: 'battleStatistics', query: {tab: 'rule'}}" />
        <q-breadcrumbs-el :label="$t(`battleRule.${rule}`)" />
      </q-breadcrumbs>
    </div>
    <q-page class="q-pa-md column items-center root">
      <div class="q-mt-xl full-width column items-center">
        <div class="q-pa-sm cst-rounded-boarder titleLabel">{{ $t(`battleRule.${rule}`) + $t('statistics.ruleStatistics.detailTitle') }}</div>
        <div class="q-mt-xl">{{ $t('statistics.ruleStatistics.descDetail') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <StatisticsSammary :user-id="userId" :rule="rule" />
        <div class="q-mt-xl">{{ $t('statistics.bukiStatistics.desc') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <BukiStatisticsTableBreakdown :user-id="userId" :rule="rule" :breakdown-stage-enabled="true"/>
        <div class="q-mt-xl">{{ $t('statistics.stageStatistics.desc') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <StageStatisticsTableBreakdown :user-id="userId" :rule="rule" :breakdown-buki-enabled="true" />
      </div>
    </q-page>
  </q-layout>
</template>
  
<script lang="ts">
import { defineComponent, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
import StatisticsSammary from '@/components/StatisticsSammary.vue'
import StageStatisticsTableBreakdown from '@/components/StageStatisticsTableBreakdown.vue'
import BukiStatisticsTableBreakdown from '@/components/BukiStatisticsTableBreakdown.vue'

export default defineComponent({
  name: 'RuleStatisticsDetail',
  components: {
    StatisticsSammary,
    StageStatisticsTableBreakdown,
    BukiStatisticsTableBreakdown
  },
  props: {
    userId: {
      type: String
    },
    rule: {
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