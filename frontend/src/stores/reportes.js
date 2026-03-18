import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import reportesService from '@/services/reportes'

export const useReportesStore = defineStore('reportes', () => {
    // State
    const reportes = ref([])
    const reporteActual = ref(null)
    const loading = ref(false)
    const uploading = ref(false)
    const error = ref(null)
    const filters = ref({
        tipo: null,
        estado: null,
        periodo: null,
        tutor: null
    })

    // Getters
    const totalReportes = computed(() => reportes.value.length)
    const reportesPendientes = computed(() =>
        reportes.value.filter(r => ['pendiente', 'procesando'].includes(r.estado)).length
    )
    const reportesError = computed(() =>
        reportes.value.filter(r => r.estado === 'error').length
    )

    // Actions
    async function fetchReportes(params = {}) {
        loading.value = true
        error.value = null

        try {
            const queryParams = { ...filters.value, ...params }
            const response = await reportesService.getAll(queryParams)
            reportes.value = response.results || response
            return response
        } catch (err) {
            error.value = err.response?.data?.error || 'Error al cargar reportes'
            throw err
        } finally {
            loading.value = false
        }
    }

    async function fetchReporte(id) {
        loading.value = true
        try {
            const response = await reportesService.getById(id)
            reporteActual.value = response
            return response
        } catch (err) {
            error.value = err.response?.data?.error || 'Error al cargar reporte'
            throw err
        } finally {
            loading.value = false
        }
    }

    async function subirReporte(file, tipoReporte, periodoId) {
        uploading.value = true
        error.value = null

        try {
            const response = await reportesService.subir(file, tipoReporte, periodoId)
            await fetchReportes()
            return response
        } catch (err) {
            error.value = err.response?.data?.error || 'Error al subir reporte'
            throw err
        } finally {
            uploading.value = false
        }
    }

    async function reprocesarReporte(id) {
        loading.value = true
        try {
            const response = await reportesService.reprocesar(id)
            await fetchReportes()
            return response
        } catch (err) {
            error.value = err.response?.data?.error || 'Error al reprocesar'
            throw err
        } finally {
            loading.value = false
        }
    }

    function descargarPlantilla(tipo) {
        return reportesService.descargarPlantilla(tipo)
    }

    function setFilters(newFilters) {
        filters.value = { ...filters.value, ...newFilters }
    }

    function clearFilters() {
        filters.value = {
            tipo: null,
            estado: null,
            periodo: null,
            tutor: null
        }
    }

    return {
        // State
        reportes,
        reporteActual,
        loading,
        uploading,
        error,
        filters,
        // Getters
        totalReportes,
        reportesPendientes,
        reportesError,
        // Actions
        fetchReportes,
        fetchReporte,
        subirReporte,
        reprocesarReporte,
        descargarPlantilla,
        setFilters,
        clearFilters
    }
})
