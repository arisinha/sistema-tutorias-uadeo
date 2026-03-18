<template>
  <v-container fluid class="login-container fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        <v-card class="login-card pa-6" elevation="12">
          <!-- Header -->
          <div class="text-center mb-8">
            <v-avatar size="80" color="primary" class="mb-4 elevation-4">
              <v-icon icon="mdi-school" size="40" color="white" />
            </v-avatar>
            <h1 class="text-h4 font-weight-bold text-gradient mb-2">
              Sistema de Tutorías
            </h1>
            <p class="text-body-2 text-medium-emphasis">
              Ingresa tus credenciales para acceder
            </p>
          </div>
          
          <!-- Login Form -->
          <v-form @submit.prevent="handleLogin" ref="formRef">
            <v-text-field
              v-model="form.username"
              label="Usuario"
              prepend-inner-icon="mdi-account"
              :rules="[rules.required]"
              :disabled="loading"
              autofocus
              class="mb-2"
            />
            
            <v-text-field
              v-model="form.password"
              label="Contraseña"
              prepend-inner-icon="mdi-lock"
              :type="showPassword ? 'text' : 'password'"
              :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append-inner="showPassword = !showPassword"
              :rules="[rules.required]"
              :disabled="loading"
              class="mb-4"
            />
            
            <v-alert
              v-if="authStore.error"
              type="error"
              variant="tonal"
              density="compact"
              class="mb-4"
            >
              {{ authStore.error }}
            </v-alert>
            
            <v-btn
              type="submit"
              color="primary"
              size="large"
              block
              :loading="loading"
            >
              <v-icon icon="mdi-login" class="mr-2" />
              Iniciar Sesión
            </v-btn>
          </v-form>
          
          <!-- Footer -->
          <div class="text-center mt-6">
            <p class="text-caption text-medium-emphasis">
              © {{ currentYear }} Sistema de Tutorías Universitarias
            </p>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const form = ref({
  username: '',
  password: ''
})
const showPassword = ref(false)
const loading = ref(false)

const currentYear = computed(() => new Date().getFullYear())

const rules = {
  required: v => !!v || 'Campo requerido'
}

const handleLogin = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return
  
  loading.value = true
  authStore.clearError()
  
  try {
    await authStore.login(form.value.username, form.value.password)
    const defaultRoute = authStore.esTutor ? '/mis-alumnos' : '/dashboard'
    router.push(defaultRoute)
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  authStore.clearError()
})
</script>

<style scoped>
.login-container {
  background: linear-gradient(135deg, #1565C0 0%, #00897B 100%);
  min-height: 100vh;
}

.login-card {
  backdrop-filter: blur(10px);
  border-radius: 16px !important;
}

.text-gradient {
  background: linear-gradient(135deg, #1565C0 0%, #00897B 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
