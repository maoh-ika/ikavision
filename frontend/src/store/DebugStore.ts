interface State {
  errors: string[]
}

const initialState: State = {
  errors: []
}

export default {
  namespaced: true,
  state: initialState,
  getters: {
    get(state: State): string[] {
      return state.errors
    }
  },
  mutations: {
    addError(state: State, error: { msg: string, sender: string }): void {
      const err = `[${Date.now()}][${error.sender}] ${error.msg}`
      state.errors = [...state.errors, err]
    }
  }
}
