export default context => ({
  async mgmt_add_club(options) {
    const { token, ...options1 } = options
    console.log('add club', options1, token)
    const resp = await context.$axios.post('/api/v1/club', options1, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async mgmt_delete_club(options) {
    const { id, token } = options
    const resp = await context.$axios.delete(`/api/v1/club/${id}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async mgmt_get_club(options) {
    const { id, token } = options
    const resp = await context.$axios.get(`/api/v1/club/${id}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async clb_get_club(options) {
    const { id, token } = options
    const resp = await context.$axios.get(`/api/v1/c/club/${id}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async anon_get_club(options) {
    const { id } = options
    const resp = await context.$axios.get(`/api/v1/a/club/${id}`, {
    })
    return resp
  },
  async mgmt_get_clubs(options) {
    const { logintoken } = options
    const resp = await context.$axios.get('/api/v1/clubs', {
      headers: {
        Authorization: 'Bearer ' + logintoken
      }
    })
    return resp
  },
  async clb_get_clubs(options) {
    const { token } = options
    console.log('api get_old_clubs', token)
    const resp = await context.$axios.get('/api/v1/c/clubs', {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async anon_get_clubs(options) {
    const resp = await context.$axios.get('/api/v1/a/clubs')
    return resp
  },
  async mgmt_update_club(options) {
    const { id, token, ...options1 } = options
    const resp = await context.$axios.put(`/api/v1/club/${id}`, options1, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async clb_update_club(options) {
    const { id, token, ...options1 } = options
    const resp = await context.$axios.put(`/api/v1/c/club/${id}`, options1, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  },
  async verify_club_access(options) {
    const { idclub, token, role } = options
    const resp = await context.$axios.get(`/api/v1/c/clubs/${idclub}/access/${role}`, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    return resp
  }

})
