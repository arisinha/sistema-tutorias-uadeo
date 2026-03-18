import api from './api'

export default {
    getDashboard() {
        return api.get('/coordinacion/dashboard/')
    },

    getEstadisticasTutores() {
        return api.get('/coordinacion/estadisticas-tutores/')
    },

    getAlumnosRiesgo() {
        return api.get('/coordinacion/alumnos-riesgo/')
    },

    getResumenReportes() {
        return api.get('/coordinacion/resumen-reportes/')
    }
}
