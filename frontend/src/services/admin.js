import api from './api'

export default {
    // Unidades
    getUnidades(params = {}) {
        return api.get('/administracion/unidades/', { params })
    },

    // Programas
    getProgramas(params = {}) {
        return api.get('/administracion/programas/', { params })
    },

    createPrograma(data) {
        return api.post('/administracion/programas/', data)
    },

    updatePrograma(id, data) {
        return api.patch(`/administracion/programas/${id}/`, data)
    },

    // Periodos
    getPeriodos(params = {}) {
        return api.get('/administracion/periodos/', { params })
    },

    getPeriodoActivo() {
        return api.get('/administracion/periodos/activo/')
    },

    createPeriodo(data) {
        return api.post('/administracion/periodos/', data)
    },

    activarPeriodo(id) {
        return api.post(`/administracion/periodos/${id}/activar/`)
    }
}
