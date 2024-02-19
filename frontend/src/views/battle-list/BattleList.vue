<template>
  <q-layout view="hhh lpr fff">
    <div class="q-pa-md q-gutter-sm">
      <q-breadcrumbs>
        <q-breadcrumbs-el icon="home" to="/" />
        <q-breadcrumbs-el :label="$t('drawer.battleList')" icon="list" />
      </q-breadcrumbs>
    </div>
    <q-page class="q-pa-md column">
      <div class="q-px-md q-mb-xl">
        <q-tabs
          v-model="tab"
          narrow-indicator
          align="justify"
          class="text-primary"
          @update:model-value="updateUrl"
        >
          <q-tab style="max-width: 150px" :ripple="false" name="completed" :label="$t('jobList.completedTab')" />
          <!--<q-tab style="max-width: 150px" :ripple="false" name="processing" :label="$t('jobList.processingTab')" />-->
          <q-space/>
        </q-tabs>
      </div>
      <div v-if="isReady">
        <CompletedAnalysisList  v-if="tab === 'completed'" :user-id="userId" />
        <!--<<ProcessingAnalysisList v-if="tab === 'processing'" :user-id="userId" />-->
      </div>
    </q-page>
  </q-layout>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import CompletedAnalysisList from './CompletedAnalysisList.vue'
import ProcessingAnalysisList from './ProcessingAnalysisList.vue'

export default defineComponent({
  name: 'BattleList',
  components: {
    CompletedAnalysisList,
    ProcessingAnalysisList
  },
  props: {
    tab: {
      type: String,
      default: 'completed'
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
        await store.dispatch('battleStatistics/fetchMasterStatistics', {userId, statisticsId: userId})
        await store.dispatch('analysisJob/fetchProcessingJobs', {userId})
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