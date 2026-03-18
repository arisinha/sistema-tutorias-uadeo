import api from './api'

export default {
    login(username, password) {
        return api.post('/auth/login/', { username, password })
    },

    logout() {
        return api.post('/auth/logout/')
    },

    getProfile() {
        return api.get('/auth/perfil/')
    },

    updateProfile(data) {
        return api.patch('/auth/perfil/', data)
    },

    getUsuarios(params = {}) {
        return api.get('/auth/usuarios/', { params })
    },

    getTutores() {
        return api.get('/auth/usuarios/tutores/')
    },

    createUsuario(data) {
        return api.post('/auth/usuarios/', data)
    },

    updateUsuario(id, data) {
        return api.patch(`/auth/usuarios/${id}/`, data)
    }
}
