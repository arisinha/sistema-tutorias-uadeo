import api from './api'

export default {
    getAll(params = {}) {
        return api.get('/reportes/', { params })
    },

    getById(id) {
        return api.get(`/reportes/${id}/`)
    },

    subir(file, tipoReporte, periodoId) {
        const formData = new FormData()
        formData.append('archivo', file)
        formData.append('tipo_reporte', tipoReporte)
        formData.append('periodo', periodoId)

        return api.post('/reportes/subir/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    },

    reprocesar(id) {
        return api.post(`/reportes/${id}/reprocesar/`)
    },

    descargarPlantilla(tipo) {
        window.open(`/api/reportes/plantilla/?tipo=${tipo}`, '_blank')
    },

    descargarArchivo(id) {
        window.open(`/api/reportes/${id}/descargar/`, '_blank')
    },

    delete(id) {
        return api.delete(`/reportes/${id}/`)
    }
}
