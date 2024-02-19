<template>
  <q-layout view="hhh lpr fff">
    <div class="q-pa-md q-gutter-sm column">
      <q-breadcrumbs>
        <q-breadcrumbs-el icon="home" to="/" />
        <q-breadcrumbs-el :label="$t('drawer.battleSearch')" icon="search" />
      </q-breadcrumbs>
    </div>
    <q-page class="q-pa-md column items-center">
      <div style="min-width: 60%;">
        <div class="text-right cst-caption">{{ $t('search.condition.help1') }}<RouterLink to="/docs/search-conditions"><span class="cst-caption">{{ $t('search.condition.help2') }}</span></RouterLink></div>
        <SearchConditionEditor :updated="search" />
      </div>
      <div v-if="searchResult !== undefined" class="full-width q-my-lg">
        <div class="text-center q-mb-md">{{ `${$t('search.resultCount')}${searchResult.totalCount}` }}</div>
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
          <div v-if="pageIndices.length > 0" class="row items-start" style="max-width: 80%;" > 
            <BattleCard
              v-for="index in pageIndices"
              class="q-ma-sm"
              :user-id="userId"
              :job-id="index.jobId"
              :result-id="index.resultId"
              :key="index.resultId"
            />
          </div>
          <div v-else>
            {{ $t('search.notFound') }}
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
    </q-page>
  </q-layout>
</template>
  
<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
import BattleCard from '@/components/BattleCard.vue'
import type { SearchResult, SearchParams, AnalysisResultIndex } from '@/modules/AnalysisResultIndexApi'
import type { AnalysisResultSammary } from '@/modules/AnalysisResultApi'
import SearchConditionEditor from './SearchConditionEditor.vue'
import { toHash } from '@/modules/Utils'

export default defineComponent({
  name: 'CompletedAnalysisList',
  components: { BattleCard, SearchConditionEditor },
  props: {
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
    const currentParams = ref<SearchParams>()
    const userId = store.getters['user/getUserId']

    const pageCount = 6

    const searchResult = computed(() => {
      if (currentParams.value === undefined) {
        return undefined
      }
      const result = store.getters['analysisResultIndex/getSearchResult'](currentParams.value) as SearchResult
      if (result === undefined) {
        return undefined
      }
      return result
    })
    
    const lastPage = computed(() => {
      if (searchResult.value === undefined) {
        return 0
      }
      return Math.ceil(searchResult.value.totalCount / props.itemsPerPage)
    })

    const maxPages = computed(() => {
      const maxPage = pageCount + currentPage.value - 1
      return Math.min(maxPage, lastPage.value)
    })

    const pageIndices = computed(() => {
      if (searchResult.value === undefined) {
        return []
      }
      const indices = [...searchResult.value.indices]
      indices.sort((a, b) => b.battleDate - a.battleDate)
      return indices
    })

    const toSammary = (index: AnalysisResultIndex): AnalysisResultSammary => {
      return {
        jobId: index.jobId,
        userId: index.userId,
        resultId: index.resultId,
        movieFrames: index.battleDuration * 30,
        frameRate: 30,
        battleDate: index.battleDate,
        battleOpenFrame: index.battleOpenFrame,
        battleEndFrame: index.battleEndFrame,
        resultStartFrame: index.resultStartFrame,
        resultEndFrame: index.resultEndFrame,
        result: index.battleResult,
        teamResultCount: index.teamResultCount,
        enemyResultCount: index.enemyResultCount,
        rule: index.battleRule,
        stage: index.battleStage,
        matchType: index.matchType,
        matchRate: index.matchRate,
        team: index.team.map((t, idx) => { return { name: t.name, side: 'team', lamp_ord: idx } }),
        enemy: index.enemy.map((t, idx) => { return { name: t.name, side: 'enemy', lamp_ord: idx } }),
        mainPlayerIndex: index.team.findIndex(t => t.name === index.mainPlayerName),
        teamColor: [0,0,0],
        enemyColor: [0,0,0],
        teamBukis: index.teamBukis,
        enemyBukis: index.enemyBukis,
        killCount: index.killCount,
        deathCount: index.deathCount,
        spCount: index.spCount
      }
    }

    const search = (params: SearchParams) => {
      if (currentParams.value !== undefined) {
        const paramsNoPage = {
          ...currentParams.value,
          pageSize: 0,
          pageIndex: 0
        }
        // ignore same conditions as current
        if (toHash(params) === toHash(paramsNoPage)) {
          return
        }
      }
      params.pageSize = props.itemsPerPage
      params.pageIndex = 0
      currentParams.value = params
      movePage(1)
    }
    
    const movePage = async (page: number) => {
      if (currentParams.value === undefined) {
        return
      }
      try {
        const newParams: SearchParams = {
          ...currentParams.value,
          pageIndex: page - 1
        }
        loading.value = true
        $q.loading.show()
        const result = await store.dispatch('analysisResultIndex/search', newParams) as SearchResult
        const sammaries = result.indices.map(index => toSammary(index))
        store.commit('analysisResult/setSammaries', sammaries)
        currentParams.value = newParams
      } catch (err) {
        console.log('failed to search indices')
      } finally {
        $q.loading.hide()
        loading.value = false
      }
      currentPage.value = page
    }

    return {
      userId,
      loading,
      searchResult,
      currentPage,
      maxPages,
      pageCount,
      pageIndices,
      movePage,
      search
    }
  }
})
</script>

<style scoped>
</style>