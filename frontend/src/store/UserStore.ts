import type { Commit } from 'vuex'

interface State {
  userId?: string
}

const initialState: State = {
//  userId: 'UC3dMKGxwpf_SDPkq0HWFhPQ'
  //userId: undefined 
  userId: 'splatoon3_environment',
}

export default {
  namespaced: true,
  state: initialState,
  getters: {
    getUserId: (state: State): string | undefined => {
      return state.userId
    },
    isLoggedIn: (state: State): boolean => {
      return state.userId !== undefined
    }
  },
  mutations: {
  },
  actions: {
  }
}
