export const state = () => ({
  token: '',
  user: '',
  email: '',
  statamicport: 0,
  previewport: 0

})

export const mutations = {
  updateUser (state, o) {
    state.token = o.token
    state.user = o.user
    state.email = o.email
  },
  updatePorts (state, o) {
    state.statamicport = o.statamicport
    state.previewport = o.previewport
  }
}
