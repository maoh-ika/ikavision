import type { Commit } from 'vuex'
import { type SearchParams, type AnalysisResultIndex, type SearchResult, search } from '@/modules/AnalysisResultIndexApi'
import { toHash } from '@/modules/Utils'

interface IndexState {
  params: SearchParams
  searchResult: SearchResult
}

interface State {
  indexStates: {[key:string]:IndexState} // hash-index
  lastParamsHash: string
  loading: boolean
}

const initialState: State = {
  indexStates: {},
  lastParamsHash: '',
  loading: false
}

export default {
  namespaced: true,
  state: initialState,
  getters: {
    getSearchResult: (state: State) => (params: SearchParams): SearchResult | undefined => {
      const hash = toHash(params)
      return state.indexStates[hash] === undefined ? undefined : state.indexStates[hash].searchResult
    },
    getSearchResultByHash: (state: State) => (hash: string): SearchResult | undefined => {
      return state.indexStates[hash] === undefined ? undefined : state.indexStates[hash].searchResult
    },
    getSearchParams: (state: State) => (hash: string): SearchParams | undefined => {
      return state.indexStates[hash] === undefined ? undefined : state.indexStates[hash].params
    },
    getLastSearchParams: (state: State): SearchParams | undefined => {
      if (state.lastParamsHash === '') {
        return undefined
      }
      return state.indexStates[state.lastParamsHash] === undefined ? undefined : state.indexStates[state.lastParamsHash].params
    },
    isLoading: (state: State): boolean => {
      return state.loading
    }
  },
  mutations: {
    setSearchResult(state: State, data: {params: SearchParams, searchResult: SearchResult}): void {
      const hash = toHash(data.params)
      state.indexStates[hash] = { ...data }
      state.lastParamsHash = hash
    },
    setLoading(state: State, loading: boolean): void {
      state.loading = loading
    }
  },
  actions: {
    async search(context: { state: State, commit: Commit, getters: any }, params: SearchParams): Promise<SearchResult> {
      const result = context.getters['getSearchResult'](params)
      if (result !== undefined) {
        return result
      }
      try {
        context.commit('setLoading', true)
        const newResult = await search(params)
        context.commit('setSearchResult', { params: params, searchResult: newResult })
        return newResult
      } catch (err) {
        console.log(err)
        throw err
      } finally {
        context.commit('setLoading', false)
      }
    },
  }
}
