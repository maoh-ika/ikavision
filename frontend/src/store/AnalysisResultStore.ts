import type { Commit } from 'vuex'
import {
  type AnalysisResultSammary,
  type AnalysisResult,
  querySammaries,
  getResult,
  getResults,
  querySammariesPagination,
  updateResult,
  deleteResult
} from '@/modules/AnalysisResultApi'
import type { BattleRule, BattleStage, MatchType } from '@/models/Battle'

export interface SammaryRequestParams {
  userId: string
  jobIds: string[]
}

export interface ResultRequestParams {
  userId: string
  jobId: string
}

export interface ResultUpdateParams {
  userId: string
  resultId: string
  rule?: BattleRule
  stage?: BattleStage
  matchType?: MatchType
  matchRate?: number
}

export interface ResultDeleteParams {
  userId: string
  resultId: string
}

interface State {
  sammaries: {[key:string]:AnalysisResultSammary} // resultId to sammary
  results: {[key:string]:AnalysisResult} // resultId to result
  sammaryLoaded: {[key:string]:boolean} // jobId to flag
  resultLoaded: {[key:string]:boolean} // jobId to flag
  sammariesPagination: {[key:string]:AnalysisResultSammary[]} // userId to sammaries
  sammaryPageToken?: any
  sammaryPaginationLoaded: boolean
}

const initialState: State = {
  sammaries: {},
  results: {},
  sammaryLoaded: {},
  resultLoaded: {},
  sammariesPagination: {},
  sammaryPageToken: undefined,
  sammaryPaginationLoaded: false
}

export default {
  namespaced: true,
  state: initialState,
  getters: {
    getSammaries: (state: State) => (userId?: string, jobId?: string | undefined): AnalysisResultSammary[] => {
      let sammaries = Object.values(state.sammaries)
      if (userId !== undefined) {
        sammaries = sammaries.filter(s => s.userId === userId)
      }
      if (jobId !== undefined) {
        sammaries = sammaries.filter(s => s.jobId === jobId)
      }
      return sammaries
    },
    getSammariesPagination: (state: State) => (userId: string): AnalysisResultSammary[] => {
      if (state.sammariesPagination[userId] === undefined) {
        return []
      }
      return state.sammariesPagination[userId]
    },
    getSammary: (state: State) => (resultId: string): AnalysisResultSammary | undefined => {
      return state.sammaries[resultId]
    },
    getResults: (state: State) => (userId?: string, jobId?: string): AnalysisResult[] => {
      let results = Object.values(state.results) as AnalysisResult[]
      if (userId !== undefined) {
        results = results.filter(r => r.userId === userId)
      }
      if (jobId !== undefined) {
        results = results.filter(r => r.jobId === jobId)
      }
      return results
    },
    getResult: (state: State) => (resultId: string): AnalysisResult | undefined => {
      return state.results[resultId]
    },
    isSammaryPaginationLoaded(state: State): boolean {
      return state.sammaryPaginationLoaded
    }
  },
  mutations: {
    setSammaries(state: State, sammaries: AnalysisResultSammary[]): void {
      sammaries.forEach(s => state.sammaries[s.resultId] = s)
    },
    setResults(state: State, results: AnalysisResult[]): void {
      results.forEach(r => state.results[r.resultId] = r)
    },
    setSammaryLoaded(state: State, payload: {jobId: string, loaded: boolean}): void {
      state.sammaryLoaded[payload.jobId] = payload.loaded
    },
    setResultLoaded(state: State, payload: {jobId: string, loaded: boolean}): void {
      state.resultLoaded[payload.jobId] = payload.loaded
    },
    addSammariesPagination(state: State, payload: {userId: string, sammaries: AnalysisResultSammary[]}): void {
      if (state.sammariesPagination[payload.userId] === undefined) {
        state.sammariesPagination[payload.userId] = []
      }
      state.sammariesPagination[payload.userId] = state.sammariesPagination[payload.userId].concat(payload.sammaries)
    },
    setSammaryPageToken(state: State, sammaryPageToken?: any): void {
      state.sammaryPageToken = sammaryPageToken
    },
    setSammaryPaginationLoaded(state: State, loaded: boolean): void {
      state.sammaryPaginationLoaded = loaded
    },
    updateResult(state: State, result: AnalysisResult): void {
      if (state.results[result.resultId]) {
        state.results[result.resultId] = result
      }
    },
    updateSammary(state: State, sammary: AnalysisResultSammary): void {
      if (state.sammaries[sammary.resultId]) {
        state.sammaries[sammary.resultId] = sammary
      }
    },
    deleteResult(state: State, resultId: string): void {
      if (state.results[resultId]) {
        state.results[resultId] = { ...state.results[resultId] }
        delete state.results[resultId]
      }
    },
    deleteSammary(state: State, resultId: string): void {
      if (state.sammaries[resultId]) {
        state.sammaries[resultId] = { ...state.sammaries[resultId] }
        delete state.sammaries[resultId]
      }
    }
  },
  actions: {
    async fetchSammaries(context: { state: State, commit: Commit }, payload: SammaryRequestParams): Promise<void> {
      const jobIds = payload.jobIds.filter(jobId => !context.state.sammaryLoaded[jobId])
      if (jobIds.length === 0) {
        return
      }
      try {
        const sammaries = await querySammaries(payload.userId, jobIds)
        sammaries.forEach((s, idx) => {
          context.commit('setSammaries', s)
          context.commit('setSammaryLoaded', { jobId: jobIds[idx], loaded: true })
        })
      } catch (err) {
        console.log(err)
        throw err
      }
    },
    async fetchResult(context: { state: State, commit: Commit, getters: any }, payload: { userId: string, resultId: string }): Promise<AnalysisResult | undefined> {
      if (context.state.results[payload.resultId]) {
        return context.state.results[payload.resultId]
      }
      try {
        const result = await getResult(payload.userId, payload.resultId)
        context.commit('setResults', [result])
        return result
      } catch (err) {
        console.log(err)
        throw err
      }
    },
    async fetchResults(context: { state: State, commit: Commit, getters: any }, payload: ResultRequestParams): Promise<AnalysisResult[] | undefined> {
      if (context.state.resultLoaded[payload.jobId]) {
        return context.getters['getResults'](payload.userId, payload.jobId)
      }
      try {
        const results = await getResults(payload.userId, payload.jobId)
        context.commit('setResults', results)
        context.commit('setResultLoaded', {jobId: payload.jobId, loaded: true})
        return results
      } catch (err) {
        console.log(err)
        throw err
      }
    },
    async fetchSammariesPagination(context: { state: State, commit: Commit, getters: any }, payload: { userId: string, pageSize: number }): Promise<AnalysisResult[] | undefined> {
      if (context.state.sammaryPaginationLoaded) {
        return context.getters['getSammariesPagination']
      }
      try {
        const res = await querySammariesPagination(payload.userId, payload.pageSize, context.state.sammaryPageToken)
        context.commit('addSammariesPagination', {userId: payload.userId, sammaries: res.sammaries})
        context.commit('setSammaries', res.sammaries)
        if (res.pageToken === null) {
          context.commit('setSammaryPageToken', undefined)
          context.commit('setSammaryPaginationLoaded', true)
        } else {
          context.commit('setSammaryPageToken', res.pageToken)
        }
      } catch (err) {
        console.log(err)
        throw err
      }
    },
    async updateResult(context: { state: State, commit: Commit, getters: any }, payload: ResultUpdateParams) {
      if (context.state.results[payload.resultId] === undefined) {
        return
      }
      await updateResult(
        payload.userId,
        payload.resultId,
        payload.rule,
        payload.stage,
        payload.matchType,
        payload.matchRate
      )
      const result = { ...context.state.results[payload.resultId] }
      result.rule = payload.rule || result.rule
      result.stage = payload.stage || result.stage
      result.matchType = payload.matchType || result.matchType
      result.matchRate = payload.matchRate || result.matchRate
      context.commit('updateResult', result)
      if (context.state.sammaries[payload.resultId]) {
        const sammary = { ...context.state.sammaries[payload.resultId] }
        sammary.rule = payload.rule || sammary.rule
        sammary.stage = payload.stage || sammary.stage
        sammary.matchType = payload.matchType || sammary.matchType
        sammary.matchRate = payload.matchRate || sammary.matchRate
        context.commit('updateSammary', sammary)
      }
    },
    async deleteResult(context: { state: State, commit: Commit, getters: any }, payload: ResultDeleteParams) {
      if (context.state.results[payload.resultId] === undefined) {
        return
      }
      await deleteResult(
        payload.userId,
        payload.resultId
      )
      context.commit('deleteResult', payload.resultId)
      if (context.state.sammaries[payload.resultId]) {
        context.commit('deleteSammary', payload.resultId)
      }
    }
  }
}
