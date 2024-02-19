<template>
  <div class="row">
    <div class="full-width">
      <div class="row justify-center q-mb-md">
        <q-pagination
          v-if="!loading"
          v-model="currentPage"
          :max="maxPages"
          :max-pages="pageCount"
          direction-links
          outline
          active-design="unelevated"
          @update:model-value="movePage"
        />
      </div>
      <div class="column q-py-md full-width items-center" > 
        <div class="row items-start" style="max-width: 80%;" > 
          <BattleCard
            v-for="sammary in pageSammaries"
            class="q-ma-sm"
            :user-id="userId"
            :job-id="sammary.jobId"
            :result-id="sammary.resultId"
            :key="sammary.resultId"
          />
        </div>
      </div>
      <div class="row justify-center q-mt-md">
        <q-pagination
          v-if="!loading"
          v-model="currentPage"
          :max="maxPages"
          :max-pages="pageCount"
          direction-links
          outline
          active-design="unelevated"
          @update:model-value="movePage"
        />
      </div>
    </div>
  </div>
</template>
  
<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
import type { AnalysisJob } from '@/modules/AnalysisJobApi'
import BattleCard from '@/components/BattleCard.vue'
import type { AnalysisResultSammary } from '@/modules/AnalysisResultApi'
import type { BattleStatistics } from '@/modules/BattleStatisticsApi'

export default defineComponent({
  name: 'CompletedAnalysisList',
  components: { BattleCard },
  props: {
    userId: {
      type: String,
      required: true
    },
    itemsPerPage: {
      type: Number,
      default: 20
    }
  },
  setup(props) {
    const store = useStore()
    const $q = useQuasar()
    const currentPage = ref(1)
    const loading = ref(false)

    const pageCount = 6

    const anslysisSammaries = computed(() => {
      const sammaries = store.getters['analysisResult/getSammariesPagination'](props.userId) as AnalysisResultSammary[]
      if (sammaries === undefined) {
        return []
      }
      return sammaries
    })
    
    const lastPage = computed(() => {
      const s = store.getters['battleStatistics/getMasterStatistics'](props.userId) as BattleStatistics
      return Math.ceil(s.resultCount / props.itemsPerPage)
    })

    const maxPages = computed(() => {
      const maxPage = pageCount + currentPage.value - 1
      return Math.min(maxPage, lastPage.value)
    })

    const pageSammaries = computed(() => {
      const startIndex = props.itemsPerPage * (currentPage.value - 1)
      const endIndex = startIndex + props.itemsPerPage
      const sammaries = anslysisSammaries.value.slice(startIndex, endIndex)
      sammaries.sort((a, b) => b.battleDate - a.battleDate)
      return sammaries
    })
    
    const getJob =(jobId: string): AnalysisJob => {
      return store.getters['analysisJob/getJob'](jobId)
    }
    
    const movePage = async (page: number) => {
      while (
        !store.getters['analysisResult/isSammaryPaginationLoaded'] &&
        anslysisSammaries.value.length < page * props.itemsPerPage
      ) {
        try {
          loading.value = true
          $q.loading.show()
          await store.dispatch('analysisResult/fetchSammariesPagination', {userId: props.userId, pageSize: props.itemsPerPage})
        } catch (err) {
          break
        } finally {
          $q.loading.hide()
          loading.value = false
        }
      }
      currentPage.value = page
    }
      
    movePage(1)
    
    return {
      currentPage,
      pageCount,
      maxPages,
      pageSammaries,
      loading,
      getJob,
      movePage
    }
  }
})
</script>

<style scoped>
</style>