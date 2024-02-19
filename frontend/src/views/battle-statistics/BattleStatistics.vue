<template>
  <q-layout view="hhh lpr fff">
    <div class="q-pa-md q-gutter-sm column">
      <q-breadcrumbs>
        <q-breadcrumbs-el icon="home" to="/" />
        <q-breadcrumbs-el :label="$t('drawer.battleStatistics')" icon="insights" />
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
          <q-tab style="max-width: 150px" :ripple="false" name="total" :label="$t('statistics.sammaryTab')" />
          <q-tab style="max-width: 150px" :ripple="false" name="buki" :label="$t('statistics.bukiTab')" />
          <q-tab style="max-width: 150px" :ripple="false" name="rule" :label="$t('statistics.ruleTab')" />
          <q-tab style="max-width: 150px" :ripple="false" name="stage" :label="$t('statistics.stageTab')" />
          <q-space/>
        </q-tabs>
      </div>
      <div v-if="isReady">
        <TotalStatistics v-if="tab === 'total'" :user-id="userId" />
        <BukiStatistics v-if="tab === 'buki'" :user-id="userId" />
        <RuleStatistics v-if="tab === 'rule'" :user-id="userId" />
        <StageStatistics v-if="tab === 'stage'" :user-id="userId" />
      </div>
    </q-page>
  </q-layout>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import TotalStatistics from './TotalStatistics.vue'
import BukiStatistics from './BukiStatistics.vue'
import RuleStatistics from './RuleStatistics.vue'
import StageStatistics from './StageStatistics.vue'
import type { BattleStatistics } from '@/modules/BattleStatisticsApi'

export default defineComponent({
  name: 'BattleStatistics',
  components: {
    TotalStatistics,
    BukiStatistics,
    RuleStatistics,
    StageStatistics
  },
  props: {
    tab: {
      type: String,
      default: 'total'
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
        await store.dispatch('battleStatistics/fetchMasterStatistics', {userId}) as BattleStatistics
        isReady.value = true
      } finally {
        $q.loading.hide()
      }
    })
    
    const updateUrl = (tab: string) => {
      router.replace({ path: route.path, query: { tab: tab} }) 
    }
    
    return {
      tab,
      userId,
      isReady,
      updateUrl
    }
  }
})
</script>

<style scoped>
</style>