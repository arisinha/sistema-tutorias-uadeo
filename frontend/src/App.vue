<template>
  <v-app>
    <AppNavbar v-if="authStore.isAuthenticated" />
    
    <v-main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </v-main>
    
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">
          Cerrar
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, provide } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppNavbar from '@/components/AppNavbar.vue'

const authStore = useAuthStore()

// Global snackbar
const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

const showMessage = (message, color = 'success') => {
  snackbar.value = { show: true, message, color }
}

provide('showMessage', showMessage)
</script>

<style>
.v-main {
  background: rgb(var(--v-theme-background));
  min-height: 100vh;
}
</style>
