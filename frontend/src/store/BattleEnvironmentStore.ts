import type { Commit } from 'vuex'
import {
  querySeasons,
  queryDaily,
  querySeasonsMatch,
  queryDailyMatch,
  querySeasonsXMatch,
  queryDailyXMatch,
  type BattleCount,
  type BattleEnvironment,
  type EnvironmentMatchType,
  type EnvironmentXMatchRate
} from '@/modules/BattleEnvironmentApi'
import { add } from '@/modules/Environment'
import type { MainWeapon } from '@/models/Buki'
import type { BattleStage, BattleRule, XMatchRate } from '@/models/Battle'

const splatoonTitle = 'splatoon3'

interface State {
  matchSeasons: {[key:string]:BattleEnvironment[]} // matchType-seasons
  xMatchSeasons: {[key:string]:BattleEnvironment[]} // rate-seasons
  matchDailies: {[key:string]:BattleEnvironment[]} // matchType-dailies
  xMatchDailies: {[key:string]:BattleEnvironment[]} // rate-dailies
  seasonLoaded: boolean
  matchSeasonLoaded: {[key:string]:boolean} // matchType-loaded
  rateSeasonLoaded: {[key:string]:boolean} // rate-loaded
  xMatcAllRatesSeasons: BattleEnvironment[] // for cache
  xMatcAllRatesDailies: BattleEnvironment[] // for cache
  currentMatchType: EnvironmentMatchType
  currentMatchRate: EnvironmentXMatchRate
  cache: {[key:string]:BattleEnvironment} // cache key to env
}

const initialState: State = {
  matchSeasons: {},
  xMatchSeasons: {},
  matchDailies: {},
  xMatchDailies: {},
  seasonLoaded: false,
  matchSeasonLoaded: {},
  rateSeasonLoaded: {},
  xMatcAllRatesSeasons: [],
  xMatcAllRatesDailies: [],
  currentMatchType: 'all',
  currentMatchRate: 'all',
  cache: {}
}

export default {
  namespaced: true,
  state: initialState,
  getters: {
    getSeasonEnvironments: (state: State) => (
      season: string='all',
      matchType?: EnvironmentMatchType,
      matchRate?: EnvironmentXMatchRate,
      sumAllRates: boolean = true): BattleEnvironment[] => {
      
      matchType = matchType || state.currentMatchType
      matchRate = matchRate || state.currentMatchRate

      let seasons = state.matchSeasons[matchType]
      if (matchType === 'x_match') {
        if (matchRate === 'all') {
          if (sumAllRates) {
            seasons = state.xMatcAllRatesSeasons
          } else {
            seasons = Object.values(state.xMatchSeasons).flat()
          }
        } else {
          seasons = state.xMatchSeasons[matchRate]
        }
      }
      
      if (seasons === undefined) {
        return []
      }

      if (season === 'all') {
        return seasons
      } else if (season === 'latest') {
        return [seasons[seasons.length - 1]]
      } else {
        return seasons.filter(s => s.seasonName === season)
      }
    },
    findDailyEnvironments: (state: State) => (
      startDate: number,
      endDate: number,
      matchType?: EnvironmentMatchType,
      matchRate?: EnvironmentXMatchRate,
      sumAllRates: boolean = true)
      : BattleEnvironment[] => {
      
      matchType = matchType || state.currentMatchType
      matchRate = matchRate || state.currentMatchRate
      
      let dailies = state.matchDailies[matchType]
      if (matchType === 'x_match') {
        if (matchRate === 'all') {
          if (sumAllRates) {
            dailies = state.xMatcAllRatesDailies
          } else {
            dailies = Object.values(state.xMatchDailies).flat()
          }
        } else {
          dailies = state.xMatchDailies[matchRate]
        }
      }
      
      if (dailies === undefined) {
        return []
      }

      return dailies.filter(s => {
        return (startDate <= s.startTimestamp && s.endTimestamp < endDate) ||
          (s.startTimestamp <= startDate && startDate < s.endTimestamp) ||
          (s.startTimestamp <= endDate && endDate < s.endTimestamp)
      })
    },
    getAllBattles: (state: State, getters: any) => (season: string='all', matchType?: EnvironmentMatchType, matchRate?: EnvironmentXMatchRate): BattleCount[] => {
      matchType = matchType || state.currentMatchType
      matchRate = matchRate || state.currentMatchRate
      const allSeasons = getters.getSeasonEnvironments(season, matchType, matchRate) as BattleEnvironment[]
      return allSeasons.map(env => env.battles).flat()
    },
    getAllBukis: (state: State, getters: any) => (season: string='all', matchType?: EnvironmentMatchType, matchRate?: EnvironmentXMatchRate): MainWeapon[] => {
      matchType = matchType || state.currentMatchType
      matchRate = matchRate || state.currentMatchRate
      const allSeasons = getters.getSeasonEnvironments(season, matchType, matchRate) as BattleEnvironment[]
      const allEnvs = allSeasons.map((env: BattleEnvironment) => env.bukiEnvironments).flat()
      return Array.from(new Set(allEnvs.map(e => e.buki)))
    },
    getAllRules: (state: State, getters: any) => (season: string='all', matchType?: EnvironmentMatchType, matchRate?: EnvironmentXMatchRate): BattleRule[] => {
      matchType = matchType || state.currentMatchType
      matchRate = matchRate || state.currentMatchRate
      const allBattles = getters.getAllBattles(season, matchType, matchRate) as BattleCount[]
      return Array.from(new Set(allBattles.map(b => b.rule)))
    },
    getAllStages: (state: State, getters: any) => (season: string='all', matchType?: EnvironmentMatchType, matchRate?: EnvironmentXMatchRate): BattleStage[] => {
      matchType = matchType || state.currentMatchType
      matchRate = matchRate || state.currentMatchRate
      const allBattles = getters.getAllBattles(season, matchType, matchRate) as BattleCount[]
      return Array.from(new Set(allBattles.map(b => b.stage)))
    },
    getEnvironmentMatchType: (state: State): EnvironmentMatchType => {
      return state.currentMatchType
    },
    getEnvironmentXMatchRate: (state: State): EnvironmentXMatchRate => {
      return state.currentMatchRate
    },
    getCache: (state: State) => (cacheKey: number): BattleEnvironment | undefined => {
      return state.cache[cacheKey]
    },
  },
  mutations: {
    setSeasonEnvironments(state: State, data: { envs: BattleEnvironment[], matchType: EnvironmentMatchType }): void {
      state.matchSeasons[data.matchType] = data.envs
      state.matchSeasons[data.matchType].sort((a, b) => a.startTimestamp - b.startTimestamp)
    },
    setSeasonEnvironmentsXMatch(state: State, data: { envs: BattleEnvironment[], matchRate: EnvironmentXMatchRate}): void {
      state.xMatchSeasons[data.matchRate] = data.envs
      state.xMatchSeasons[data.matchRate].sort((a, b) => a.startTimestamp - b.startTimestamp)
    },
    setMatchSeasonLoaded(state: State, data: { loaded: boolean, matchType: EnvironmentMatchType }): void {
      state.matchSeasonLoaded[data.matchType] = data.loaded
    },
    setRateSeasonLoaded(state: State, data: { loaded: boolean, matchRate: EnvironmentXMatchRate}): void {
      state.rateSeasonLoaded[data.matchRate] = data.loaded
    },
    addDailyEnvironments(state: State, data: { envs: BattleEnvironment[], matchType: EnvironmentMatchType }): void {
      if (state.matchDailies[data.matchType] === undefined) {
        state.matchDailies[data.matchType] = []
      }
      state.matchDailies[data.matchType] = [...state.matchDailies[data.matchType], ...data.envs]
      state.matchDailies[data.matchType].sort((a, b) => a.startTimestamp - b.startTimestamp)
    },
    addDailyEnvironmentsXMatch(state: State, data: { envs: BattleEnvironment[], matchRate: EnvironmentXMatchRate}): void {
      if (state.xMatchDailies[data.matchRate] === undefined) {
        state.xMatchDailies[data.matchRate] = []
      }
      state.xMatchDailies[data.matchRate] = [...state.xMatchDailies[data.matchRate], ...data.envs]
      state.xMatchDailies[data.matchRate].sort((a, b) => a.startTimestamp - b.startTimestamp)
    },
    setXMatcAllRatesSeasons(state: State, seasons: BattleEnvironment[]) {
      state.xMatcAllRatesSeasons = seasons
    },
    setXMatcAllRatesDailies(state: State, dailies: BattleEnvironment[]) {
      state.xMatcAllRatesDailies = dailies
    },
    setEnvironmentMatchType: (state: State, type: EnvironmentMatchType) => {
      state.currentMatchType = type
    },
    setEnvironmentXMatchRate: (state: State, rate: EnvironmentXMatchRate) => {
      state.currentMatchRate = rate
    },
    setCache: (state: State, cache: { cacheKey: number, env: BattleEnvironment }) => {
      return state.cache[cache.cacheKey] = cache.env
    }
  },
  actions: {
    async fetchSeasonEnvironments(context: { state: State, commit: Commit, getters: any }, payload: { matchType?: EnvironmentMatchType, matchRate?: EnvironmentXMatchRate } = {}): Promise<BattleEnvironment[]> {
      const matchType = payload.matchType || context.state.currentMatchType
      const matchRate = payload.matchRate || context.state.currentMatchRate
      if (context.state.matchSeasonLoaded[matchType] || (matchType === 'x_match' && context.state.rateSeasonLoaded[matchRate])) {
        return context.getters['getSeasonEnvironments']('all', matchType, matchRate)
      }

      let envs: BattleEnvironment[] = []
      if (matchType === 'all') {
        envs = await querySeasons(splatoonTitle) as BattleEnvironment[]
        context.commit('setSeasonEnvironments', { envs: envs, matchType: matchType })
        context.commit('setMatchSeasonLoaded', { loaded: true, matchType: matchType })
      } else {
        if (matchType === 'x_match') {
          if (matchRate === 'all') {
            // ignore already loaded rates
            const ignoreRates = Object.keys(context.state.matchSeasonLoaded).filter(m => m !== 'all') as XMatchRate[]
            envs = await querySeasonsXMatch(splatoonTitle, ignoreRates) as BattleEnvironment[]
            const rateEnvs: any = {}
            // gather envs per match type
            envs.forEach(env => {
              if (rateEnvs[env.matchRate] === undefined) {
                rateEnvs[env.matchRate] = []
              }
              rateEnvs[env.matchRate].push(env)
            })
            Object.keys(rateEnvs).forEach(rate => {
              context.commit('setSeasonEnvironmentsXMatch', { envs: rateEnvs[rate], matchRate: rate })
              context.commit('setRateSeasonLoaded', { loaded: true, matchRate: rate })
            })
            // update all rate cache
            const xMatchSeasons = context.getters['getSeasonEnvironments']('all', 'x_match', 'all', false) as BattleEnvironment[]
            const seasonToEnvs: {[key:string]: BattleEnvironment[]} = {}
            // gather all rates per season
            xMatchSeasons.forEach(env => {
              if (seasonToEnvs[env.seasonName] === undefined) {
                seasonToEnvs[env.seasonName] = []
              }
              seasonToEnvs[env.seasonName].push(env)
            })
            const allRatesSeasons: BattleEnvironment[] = []
            Object.values(seasonToEnvs).forEach(rateSeasons => {
              let season = rateSeasons[0]
              rateSeasons.slice(1).forEach(s => season = add(season, s))
              allRatesSeasons.push(season)
            })
            context.commit('setXMatcAllRatesSeasons', allRatesSeasons)
          } else {
            envs = await querySeasonsMatch(splatoonTitle, matchType, matchRate)
            context.commit('setSeasonEnvironmentsXMatch', { envs: envs, matchRate: matchRate })
            context.commit('setRateSeasonLoaded', { loaded: true, matchRate: matchRate })
          }
        } else {
          envs = await querySeasonsMatch(splatoonTitle, matchType)
          context.commit('setSeasonEnvironments', { envs: envs, matchType: matchType })
          context.commit('setMatchSeasonLoaded', { loaded: true, matchType: matchType })
        }
      }
      return envs
    },
    async fetchDailyEnvironemts(context: { state: State, commit: Commit, getters: any }, payload: { startDate: number, endDate: number, matchType?: EnvironmentMatchType, matchRate?: EnvironmentXMatchRate }): Promise<BattleEnvironment[]> {
      const matchType = payload.matchType || context.state.currentMatchType
      const matchRate = payload.matchRate || context.state.currentMatchRate

      const requestTimeRanges: any[] = []
      
      const existEnvs = context.getters['findDailyEnvironments'](payload.startDate, payload.endDate, matchType, matchRate) as BattleEnvironment[]
      if (existEnvs.length === 0) {
        requestTimeRanges.push([payload.startDate, payload.endDate])
      } else {
        // missing part in front
        const endInFront = existEnvs[0].startTimestamp
        if (payload.startDate < endInFront) {
          requestTimeRanges.push([payload.startDate, endInFront])
        }
        // missing part at back
        const startAtBack = existEnvs[existEnvs.length - 1].endTimestamp
        if (startAtBack < payload.endDate) {
          requestTimeRanges.push([startAtBack, payload.endDate])
        }
      }

      if (requestTimeRanges.length === 0) {
        return existEnvs
      }
      
      let newEnvs: BattleEnvironment[] = []
      for (const range of requestTimeRanges) {
        if (matchType === 'all') {
          const envs = await queryDaily(splatoonTitle, range[0], range[1])
          context.commit('addDailyEnvironments', { envs: envs, matchType: matchType })
          newEnvs = newEnvs.concat(envs)
        } else {
          if (matchType === 'x_match') {
            if (matchRate === 'all') {
              // ignore already loaded rates
              let xMatchDailies = context.getters['findDailyEnvironments'](range[0], range[1], 'x_match', 'all', false) as BattleEnvironment[]
              const ignoreRates = Array.from(new Set(xMatchDailies.map(env => env.matchRate).filter(rate => rate !== undefined && rate !== 'all')))
              const envs = await queryDailyXMatch(splatoonTitle, range[0], range[1], ignoreRates as XMatchRate[]) as BattleEnvironment[]
              const rateEnvs: any = {}
              // gather envs per match rate
              envs.forEach(env => {
                if (rateEnvs[env.matchRate] === undefined) {
                  rateEnvs[env.matchRate] = []
                }
                rateEnvs[env.matchRate].push(env)
              })
              Object.keys(rateEnvs).forEach(rate => {
                context.commit('addDailyEnvironmentsXMatch', { envs: rateEnvs[rate], matchType: rate })
              })
              newEnvs = newEnvs.concat(envs)
              
            } else {
              const envs = await queryDailyMatch(splatoonTitle, range[0], range[1], matchType, matchRate)
              context.commit('addDailyEnvironmentsXMatch', { envs: envs, matchRate: matchRate })
              newEnvs = newEnvs.concat(envs)
            }
          } else {
            const envs = await queryDailyMatch(splatoonTitle, range[0], range[1], matchType)
            context.commit('addDailyEnvironments', { envs: envs, matchType: matchType })
            newEnvs = newEnvs.concat(envs)
          }
        }
      }
      
      if (matchType === 'x_match' && matchRate === 'all') {
        // update all rate cache
        const xMatchDailies= context.getters['findDailyEnvironments'](payload.startDate, payload.endDate, 'x_match', 'all', false) as BattleEnvironment[]
        const dailyStartToEnvs: {[key:number]: BattleEnvironment[]} = {}
        // gather all rates per day
        xMatchDailies.forEach(env => {
          if (dailyStartToEnvs[env.startTimestamp] === undefined) {
            dailyStartToEnvs[env.startTimestamp] = []
          }
          dailyStartToEnvs[env.startTimestamp].push(env)
        })
        // sum up all rates per day
        const allRatesDailies: BattleEnvironment[] = []
        Object.values(dailyStartToEnvs).forEach(rateDailies => {
          let daily = rateDailies[0]
          rateDailies.slice(1).forEach(s => daily = add(daily, s))
          allRatesDailies.push(daily)
        })
        context.commit('setXMatcAllRatesDailies', allRatesDailies)
      }

      return existEnvs.concat(newEnvs)
    }
  }
}
