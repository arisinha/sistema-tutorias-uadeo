import api from './api'

export default {
    getAll(params = {}) {
        return api.get('/alumnos/', { params })
    },

    getById(id) {
        return api.get(`/alumnos/${id}/`)
    },

    create(data) {
        return api.post('/alumnos/', data)
    },

    update(id, data) {
        return api.patch(`/alumnos/${id}/`, data)
    },

    delete(id) {
        return api.delete(`/alumnos/${id}/`)
    },

    asignarTutor(alumnoIds, tutorId) {
        return api.post('/alumnos/asignar_tutor/', {
            alumno_ids: alumnoIds,
            tutor_id: tutorId
        })
    },

    importarExcel(file, programaId) {
        const formData = new FormData()
        formData.append('archivo', file)
        formData.append('programa_educativo', programaId)

        return api.post('/alumnos/importar_excel/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    },

    descargarPlantilla() {
        return api.get('/alumnos/plantilla/', {
            responseType: 'blob'
        })
    },

    getSugerenciasTutoria() {
        return api.get('/alumnos/sugerencias_tutoria/')
    }
}
