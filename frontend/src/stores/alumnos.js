import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import alumnosService from '@/services/alumnos'

export const useAlumnosStore = defineStore('alumnos', () => {
    // State
    const alumnos = ref([])
    const alumnoActual = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const pagination = ref({
        page: 1,
        pageSize: 20,
        total: 0
    })
    const filters = ref({
        buscar: '',
        programa: null,
        semestre: null,
        tutor: null,
        sinTutor: false,
        requiereIndividual: false
    })

    // Getters
    const totalAlumnos = computed(() => pagination.value.total)
    const hasFilters = computed(() => {
        return filters.value.buscar ||
            filters.value.programa ||
            filters.value.semestre ||
            filters.value.tutor ||
            filters.value.sinTutor ||
            filters.value.requiereIndividual
    })

    // Actions
    async function fetchAlumnos(params = {}) {
        loading.value = true
        error.value = null

        try {
            const queryParams = {
                page: pagination.value.page,
                ...filters.value,
                ...params
            }

            const response = await alumnosService.getAll(queryParams)
            alumnos.value = response.results || response
            pagination.value.total = response.count || response.length
            return response
        } catch (err) {
            error.value = err.response?.data?.error || 'Error al cargar alumnos'
            throw err
        } finally {
            loading.value = false
        }
    }

    async function fetchAlumno(id) {
        loading.value = true
        try {
            const response = await alumnosService.getById(id)
            alumnoActual.value = response
            return response
        } catch (err) {
            error.value = err.response?.data?.error || 'Error al cargar alumno'
            throw err
        } finally {
            loading.value = false
        }
    }

    async function asignarTutor(alumnoIds, tutorId) {
        loading.value = true
        try {
            const response = await alumnosService.asignarTutor(alumnoIds, tutorId)
            await fetchAlumnos()
            return response
        } catch (err) {
            error.value = err.response?.data?.error || 'Error al asignar tutor'
            throw err
        } finally {
            loading.value = false
        }
    }

    async function importarExcel(file, programaId) {
        loading.value = true
        try {
            const response = await alumnosService.importarExcel(file, programaId)
            await fetchAlumnos()
            return response
        } catch (err) {
            error.value = err.response?.data?.error || 'Error al importar archivo'
            throw err
        } finally {
            loading.value = false
        }
    }

    function setFilters(newFilters) {
        filters.value = { ...filters.value, ...newFilters }
        pagination.value.page = 1
    }

    function clearFilters() {
        filters.value = {
            buscar: '',
            programa: null,
            semestre: null,
            tutor: null,
            sinTutor: false,
            requiereIndividual: false
        }
        pagination.value.page = 1
    }

    return {
        // State
        alumnos,
        alumnoActual,
        loading,
        error,
        pagination,
        filters,
        // Getters
        totalAlumnos,
        hasFilters,
        // Actions
        fetchAlumnos,
        fetchAlumno,
        asignarTutor,
        importarExcel,
        setFilters,
        clearFilters
    }
})
