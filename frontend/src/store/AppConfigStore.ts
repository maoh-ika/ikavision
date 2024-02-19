import type { Commit } from 'vuex'
import type { BattleViewerConfig, ViewComponent } from '@/modules/BattleViewer'
import type { SearchCondition } from '@/modules/BattleSearch'

interface State {
  viewerConfig: BattleViewerConfig
  searchConditions: SearchCondition[]
}

const initialState: State = {
  viewerConfig: {
    size: [
      {
        threshold: 768,
        width: 320,
        height: 360
      },
      {
        threshold: 9999999,
        width: 620,
        height: 360 
      },
    ],
    components: [
      {
        component: 'BattleMoviePlayer',
      },
      {
        component: 'InkTankLevelChart',
      },
      {
        component: 'PlayerNumberBalanceChart',
      },
      {
        component: 'BattleScoreChart',
      },
      {
        component: 'DeathChart',
      },
      {
        component: 'SpecialWeaponChart',
      }
    ],
    movieSyncEnabled: true,
    playOnlyBattlePart: true
  },
  searchConditions: []
}

export default {
  namespaced: true,
  state: initialState,
  getters: {
    getConfig: (state: State): BattleViewerConfig => {
      return state.viewerConfig
    },
    getMovieSyncEnabled: (state: State): boolean => {
      return state.viewerConfig.movieSyncEnabled
    },
    getPlayOnlyBattlePart: (state: State): boolean => {
      return state.viewerConfig.playOnlyBattlePart
    },
    getSearchConditions: (state: State): SearchCondition[] => {
      return state.searchConditions
    }
  },
  mutations: {
    setMovieSyncEnabled: (state: State, enabled: boolean) => {
      if (state.viewerConfig.movieSyncEnabled !== enabled) {
        state.viewerConfig.movieSyncEnabled = enabled
      }
    },
    setPlayOnlyBattlePart: (state: State, enabled: boolean) => {
      if (state.viewerConfig.playOnlyBattlePart !== enabled) {
        state.viewerConfig.playOnlyBattlePart = enabled
      } 
    },
    setSearchConditions: (state: State, conditions: SearchCondition[]) => {
      return state.searchConditions = conditions
    }
  },
  actions: {
  }
}
