<template>
  <q-layout view="hhh lpr fff">
    <div class="q-pa-md q-gutter-sm">
      <q-breadcrumbs>
        <q-breadcrumbs-el icon="home" to="/" />
        <q-breadcrumbs-el :label="`${$t('drawer.battleStatistics')}(${$t('general.buki')})`" icon="insights" :to="{name: 'battleStatistics', query: {tab: 'buki'}}" />
        <q-breadcrumbs-el :label="$t(`buki.main.${bukiId}`)" />
      </q-breadcrumbs>
    </div>
    <q-page class="q-pa-md column items-center root">
      <div class="q-mt-xl full-width column items-center">
        <div class="q-pa-sm cst-rounded-boarder titleLabel">{{ $t(`buki.main.${bukiId}`) + $t('statistics.bukiStatistics.detailTitle') }}</div>
        <div class="q-mt-xl">{{ $t('statistics.bukiStatistics.descDetail') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <StatisticsSammary :user-id="userId" :buki="bukiId" />
        <div class="q-mt-xl">{{ $t('statistics.ruleStatistics.desc') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <RuleStatisticsTableBreakdown :user-id="userId" :buki="bukiId" :breakdown-stage-enabled="true" />
        <div class="q-mt-xl">{{ $t('statistics.stageStatistics.desc') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <StageStatisticsTableBreakdown :user-id="userId" :buki="bukiId" :breakdown-rule-enabled="true"/>
        <div class="q-mt-xl">{{ $t('statistics.bukiStatistics.breakdownFaceoff') }}</div>
        <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
        <BukiFaceoffTable :user-id="userId" :statistics-id="userId" :buki-id="bukiId"/>
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
import StageStatisticsTableBreakdown from '@/components/StageStatisticsTableBreakdown.vue'
import BukiFaceoffTable from '@/components/BukiFaceoffTable.vue'

export default defineComponent({
  name: 'BukiStatisticsDetail',
  components: {
    StatisticsSammary,
    RuleStatisticsTableBreakdown,
    StageStatisticsTableBreakdown,
    BukiFaceoffTable
  },
  props: {
    userId: {
      type: String
    },
    bukiId: {
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