import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Views
import LoginView from '@/views/LoginView.vue'

const routes = [
    {
        path: '/login',
        name: 'login',
        component: LoginView,
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        redirect: '/dashboard'
    },
    {
        path: '/dashboard',
        name: 'dashboard',
        component: () => import('@/views/coordinador/DashboardView.vue'),
        meta: { requiresAuth: true, roles: ['coordinador', 'jefe'] }
    },
    // Tutor routes
    {
        path: '/mis-alumnos',
        name: 'mis-alumnos',
        component: () => import('@/views/tutor/AlumnosView.vue'),
        meta: { requiresAuth: true, roles: ['tutor'] }
    },
    {
        path: '/mis-reportes',
        name: 'mis-reportes',
        component: () => import('@/views/tutor/ReportesView.vue'),
        meta: { requiresAuth: true, roles: ['tutor'] }
    },
    // Coordinator routes
    {
        path: '/alumnos',
        name: 'alumnos',
        component: () => import('@/views/coordinador/AlumnosGestionView.vue'),
        meta: { requiresAuth: true, roles: ['coordinador', 'jefe'] }
    },
    {
        path: '/asignaciones',
        name: 'asignaciones',
        component: () => import('@/views/coordinador/AsignacionesView.vue'),
        meta: { requiresAuth: true, roles: ['coordinador', 'jefe'] }
    },
    {
        path: '/reportes',
        name: 'reportes',
        component: () => import('@/views/coordinador/ReportesGestionView.vue'),
        meta: { requiresAuth: true, roles: ['coordinador', 'jefe'] }
    },
    // Admin routes
    {
        path: '/programas',
        name: 'programas',
        component: () => import('@/views/admin/ProgramasView.vue'),
        meta: { requiresAuth: true, roles: ['jefe'] }
    },
    {
        path: '/periodos',
        name: 'periodos',
        component: () => import('@/views/admin/PeriodosView.vue'),
        meta: { requiresAuth: true, roles: ['coordinador', 'jefe'] }
    },
    // Catch all
    {
        path: '/:pathMatch(.*)*',
        redirect: '/login'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next('/login')
    } else if (to.path === '/login' && authStore.isAuthenticated) {
        // Redirect authenticated users to their default page
        const defaultRoute = authStore.user?.rol === 'tutor' ? '/mis-alumnos' : '/dashboard'
        next(defaultRoute)
    } else if (to.meta.roles && !to.meta.roles.includes(authStore.user?.rol)) {
        // Redirect if user doesn't have permission
        const defaultRoute = authStore.user?.rol === 'tutor' ? '/mis-alumnos' : '/dashboard'
        next(defaultRoute)
    } else {
        next()
    }
})

export default router
