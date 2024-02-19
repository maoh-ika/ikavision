<template>
  <q-layout view="hhh lpr fff">
    <div class="q-pa-md q-gutter-sm">
      <q-breadcrumbs>
        <q-breadcrumbs-el icon="home" to="/" />
        <q-breadcrumbs-el :label="$t('drawer.battleSearch')" icon="search" to="/battleSearch" />
        <q-breadcrumbs-el :label="pageTitle" />
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
          <q-tab style="max-width: 150px" :ripple="false" name="battleInfo" :label="$t('viewer.battleInfoTab')" />
          <q-tab style="max-width: 150px" :ripple="false" name="analysisViewer" :label="$t('viewer.analysisViewerTab')" />
          <q-tab v-if="isDev" style="max-width: 150px" :ripple="false" name="battleEdit" :label="$t('viewer.battleEdit')" />
          <q-space/>
        </q-tabs>
      </div>
      <div>
        <BattleInfo v-if="tab === 'battleInfo'" :user-id="userId" :job-id="jobId" :result-id="resultId" />
        <AnalysisResultViewer v-if="tab === 'analysisViewer'" :user-id="userId" :job-id="jobId" :result-id="resultId" />
        <BattleEdit v-if="isDev && tab === 'battleEdit'" :user-id="userId" :job-id="jobId" :result-id="resultId" />
      </div>
    </q-page>
  </q-layout>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import BattleInfo from './BattleInfo.vue'
import AnalysisResultViewer from './AnalysisResultViewer.vue'
import BattleEdit from './BattleEdit.vue'
import { config } from '@/modules/Config'

export default defineComponent({
  name: 'BattleViewer',
  components: {
    BattleInfo,
    AnalysisResultViewer,
    BattleEdit
  },
  props: {
    userId: {
      type: String,
      required: true
    },
    jobId: {
      type: String,
      required: true
    },
    resultId: {
      type: String,
      required: true
    },
    tab: {
      type: String,
      default: 'battleInfo'
    }
  },
  setup(props) {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    const isReady = ref(false)
    const tab = ref(route.query.tab || props.tab)
    
    const pageTitle = computed(() => {
      const job = store.getters['analysisJob/getJob'](props.jobId)
      return job !== undefined ? job.jobName : ''
    })
    
    const updateUrl = (tab: string) => {
      router.replace({ path: route.path, query: { tab: tab } }) 
    }

    const isDev = config.isDev()

    return {
      isDev,
      isReady,
      tab,
      pageTitle,
      updateUrl,
    }
  }
})
</script>

<style scoped>
.parent {
  width: 100%;
  height: 100%; 
  border: 1px solid #000;
  user-select: none;
  position: absolute;
}
.focus {
  z-index: 9;
}
</style>