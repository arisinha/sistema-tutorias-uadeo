import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
    // State
    const user = ref(JSON.parse(localStorage.getItem('user')) || null)
    const loading = ref(false)
    const error = ref(null)

    // Getters
    const isAuthenticated = computed(() => !!user.value)
    const userRole = computed(() => user.value?.rol || null)
    const userName = computed(() => user.value?.nombre_completo || user.value?.username || '')

    const esTutor = computed(() => user.value?.rol === 'tutor')
    const esCoordinador = computed(() => user.value?.rol === 'coordinador')
    const esJefe = computed(() => user.value?.rol === 'jefe')

    // Actions
    async function login(username, password) {
        loading.value = true
        error.value = null

        try {
            const response = await authService.login(username, password)
            user.value = response.user
            localStorage.setItem('user', JSON.stringify(response.user))
            return response
        } catch (err) {
            error.value = err.response?.data?.error || 'Error al iniciar sesión'
            throw err
        } finally {
            loading.value = false
        }
    }

    async function logout() {
        try {
            await authService.logout()
        } catch (err) {
            console.error('Error en logout:', err)
        } finally {
            user.value = null
            localStorage.removeItem('user')
        }
    }

    async function fetchProfile() {
        try {
            const profile = await authService.getProfile()
            user.value = profile
            localStorage.setItem('user', JSON.stringify(profile))
            return profile
        } catch (err) {
            logout()
            throw err
        }
    }

    function clearError() {
        error.value = null
    }

    return {
        // State
        user,
        loading,
        error,
        // Getters
        isAuthenticated,
        userRole,
        userName,
        esTutor,
        esCoordinador,
        esJefe,
        // Actions
        login,
        logout,
        fetchProfile,
        clearError
    }
})
