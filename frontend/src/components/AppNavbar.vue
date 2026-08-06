<template>
  <div>
    <v-app-bar color="primary" density="comfortable" elevation="2">
      <v-app-bar-nav-icon @click="drawer = !drawer" class="d-lg-none" />
      
      <v-app-bar-title class="text-h6 font-weight-bold">
        <v-icon icon="mdi-school" class="mr-2" />
        Sistema de Tutorías
      </v-app-bar-title>
      
      <v-spacer />
      
      <!-- Desktop navigation -->
      <div class="d-none d-lg-flex align-center">
        <template v-for="item in menuItems" :key="item.to">
          <v-btn
            v-if="item.show"
            :to="item.to"
            variant="text"
            class="mx-1"
          >
            <v-icon :icon="item.icon" class="mr-1" size="small" />
            {{ item.title }}
          </v-btn>
        </template>
      </div>
      
      <v-divider vertical class="mx-3 d-none d-lg-flex" />
      
      <!-- Theme toggle -->
      <v-btn icon variant="text" @click="toggleTheme">
        <v-icon :icon="isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'" />
      </v-btn>
      
      <!-- User menu -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn variant="text" v-bind="props" class="ml-2">
            <v-avatar size="32" color="secondary" class="mr-2">
              <span class="text-body-2">{{ userInitials }}</span>
            </v-avatar>
            <span class="d-none d-md-inline">{{ authStore.userName }}</span>
            <v-icon icon="mdi-chevron-down" size="small" />
          </v-btn>
        </template>
        
        <v-list density="compact" min-width="200">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              {{ authStore.userName }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ roleLabel }}
            </v-list-item-subtitle>
          </v-list-item>
          
          <v-divider class="my-2" />
          
          <v-list-item @click="logout" prepend-icon="mdi-logout" title="Cerrar Sesión" />
        </v-list>
      </v-menu>
      
      <!-- Logout button -->
      <v-btn variant="text" @click="logout" class="ml-2">
        <v-icon icon="mdi-logout" class="mr-1" />
        <span class="d-none d-md-inline">Salir</span>
      </v-btn>
    </v-app-bar>
    
    <!-- Mobile navigation drawer -->
    <v-navigation-drawer v-model="drawer" temporary class="d-lg-none">
      <v-list nav density="compact">
        <template v-for="item in menuItems" :key="item.to">
          <v-list-item
            v-if="item.show"
            :to="item.to"
            :prepend-icon="item.icon"
            :title="item.title"
            @click="drawer = false"
          />
        </template>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const theme = useTheme()
const authStore = useAuthStore()

const drawer = ref(false)

const isDark = computed(() => theme.global.current.value.dark)

const toggleTheme = () => {
  theme.global.name.value = isDark.value ? 'customTheme' : 'darkTheme'
}

const userInitials = computed(() => {
  const name = authStore.userName
  if (!name) return '?'
  const parts = name.split(' ')
  return parts.length > 1 
    ? `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    : name.substring(0, 2).toUpperCase()
})

const roleLabel = computed(() => {
  const roles = {
    tutor: 'Tutor',
    coordinador: 'Coordinador',
    jefe: 'Jefe de Departamento'
  }
  return roles[authStore.userRole] || authStore.userRole
})

const menuItems = computed(() => [
  // Tutor menu
  { 
    title: 'Mis Alumnos', 
    to: '/mis-alumnos', 
    icon: 'mdi-account-group',
    show: authStore.esTutor
  },
  { 
    title: 'Mis Reportes', 
    to: '/mis-reportes', 
    icon: 'mdi-file-document',
    show: authStore.esTutor
  },
  // Coordinator menu
  { 
    title: 'Dashboard', 
    to: '/dashboard', 
    icon: 'mdi-view-dashboard',
    show: authStore.esCoordinador || authStore.esJefe
  },
  { 
    title: 'Alumnos', 
    to: '/alumnos', 
    icon: 'mdi-account-school',
    show: authStore.esCoordinador || authStore.esJefe
  },
  { 
    title: 'Asignaciones', 
    to: '/asignaciones', 
    icon: 'mdi-account-arrow-right',
    show: authStore.esCoordinador || authStore.esJefe
  },
  { 
    title: 'Reportes', 
    to: '/reportes', 
    icon: 'mdi-file-chart',
    show: authStore.esCoordinador || authStore.esJefe
  },
  // Admin menu
  { 
    title: 'Usuarios', 
    to: '/usuarios', 
    icon: 'mdi-account-cog',
    show: authStore.esJefe
  },
  { 
    title: 'Programas', 
    to: '/programas', 
    icon: 'mdi-book-education',
    show: authStore.esJefe
  },
  { 
    title: 'Periodos', 
    to: '/periodos', 
    icon: 'mdi-calendar',
    show: authStore.esCoordinador || authStore.esJefe
  },
])

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
