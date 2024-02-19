import type { Commit } from 'vuex'
import { getMaster, getDaily, type BattleStatistics } from '@/modules/BattleStatisticsApi'

interface State {
  masterStatistics: {[key:string]:BattleStatistics}
  dailyStatistics: {[key:string]:BattleStatistics[]}
}

const initialState: State = {
  masterStatistics: {},
  dailyStatistics: {}
}

export default {
  namespaced: true,
  state: initialState,
  getters: {
    getMasterStatistics: (state: State) => (userId: string): BattleStatistics | undefined => {
      return state.masterStatistics[userId] !== undefined ? state.masterStatistics[userId] : undefined
    },
    getDailyStatistics: (state: State) => (userId: string): BattleStatistics[] | undefined => {
      return state.dailyStatistics[userId] !== undefined ? state.dailyStatistics[userId] : undefined
    },
    findDailyStatistics: (state: State) => (userId: string, startDate: number, endDate: number): BattleStatistics[] | undefined => {
      if (state.dailyStatistics[userId] === undefined) {
        return []
      }
      return state.dailyStatistics[userId].filter(s => {
        return (startDate <= s.startTimestamp && s.endTimestamp < endDate) ||
          (s.startTimestamp <= startDate && startDate < s.endTimestamp) ||
          (s.startTimestamp <= endDate && endDate < s.endTimestamp)
      })
    }
  },
  mutations: {
    setMasterStatistics(state: State, statistics: BattleStatistics): void {
      state.masterStatistics[statistics.userId] = statistics
    },
    addDailyStatistics(state: State, data: { userId: string , statistics: BattleStatistics[] }): void {
      if (state.dailyStatistics[data.userId] === undefined) {
        state.dailyStatistics[data.userId] = [...data.statistics]
      } else {
        state.dailyStatistics[data.userId] = [...state.dailyStatistics[data.userId], ...data.statistics]
        state.dailyStatistics[data.userId].sort((a, b) => a.startTimestamp - b.startTimestamp)
      }
    }
  },
  actions: {
    async fetchMasterStatistics(context: { state: State, commit: Commit }, payload: { userId: string }): Promise<BattleStatistics> {
      const stat = context.state.masterStatistics[payload.userId]
      if (stat !== undefined) {
        return stat
      }

      const s = await getMaster(payload.userId)
      context.commit('setMasterStatistics', s)
      return s
    },
    async fetchDailyStatistics(context: { state: State, commit: Commit, getters: any }, payload: { userId: string, startDate: number, endDate: number }): Promise<BattleStatistics[]> {
      let stats = context.getters['findDailyStatistics'](payload.userId, payload.startDate, payload.endDate) as BattleStatistics[]
      if (stats.length === 0) {
        const newStats = await getDaily(payload.userId, payload.startDate, payload.endDate)
        context.commit('addDailyStatistics', { userId: payload.userId, statistics: newStats })
        return newStats
      }
      // missing part in front
      const endInFront = stats[0].startTimestamp
      if (payload.startDate < endInFront) {
        const newStats = await getDaily(payload.userId, payload.startDate, endInFront)
        if (newStats.length > 0) {
          context.commit('addDailyStatistics', { userId: payload.userId, statistics: newStats })
          stats = newStats.concat(stats)
        }
      }
      // missing part at back
      const startAtBack = stats[stats.length - 1].endTimestamp
      if (startAtBack < payload.endDate) {
        const newStats = await getDaily(payload.userId, startAtBack, payload.endDate)
        if (newStats.length > 0) {
          context.commit('addDailyStatistics', { userId: payload.userId, statistics: newStats })
          stats = stats.concat(newStats)
        }
      }
      return stats
    }
  }
}
