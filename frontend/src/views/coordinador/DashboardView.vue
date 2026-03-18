<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Dashboard</h1>
        <p class="text-body-2 text-medium-emphasis">
          Resumen del período académico actual
        </p>
      </div>
      <v-btn color="primary" variant="tonal" @click="refreshData">
        <v-icon icon="mdi-refresh" class="mr-2" />
        Actualizar
      </v-btn>
    </div>
    
    <!-- Stats Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <StatCard
          title="Total Alumnos"
          :value="stats.total_alumnos"
          icon="mdi-account-group"
          color="primary"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <StatCard
          title="Tutores Activos"
          :value="stats.total_tutores"
          icon="mdi-account-tie"
          color="secondary"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <StatCard
          title="Reportes Procesados"
          :value="stats.reportes_procesados"
          icon="mdi-file-check"
          color="success"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <StatCard
          title="Alumnos en Riesgo"
          :value="stats.alumnos_requieren_individual"
          icon="mdi-alert"
          color="warning"
        />
      </v-col>
    </v-row>
    
    <v-row>
      <!-- At-risk students -->
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-account-alert" color="warning" class="mr-2" />
            Alumnos que Requieren Atención
          </v-card-title>
          <v-divider />
          
          <v-list v-if="alumnosRiesgo.length" lines="two">
            <v-list-item
              v-for="alumno in alumnosRiesgo.slice(0, 5)"
              :key="alumno.id"
            >
              <template v-slot:prepend>
                <v-avatar color="warning" size="40">
                  <span class="text-body-2">{{ getInitials(alumno.nombre_completo) }}</span>
                </v-avatar>
              </template>
              
              <v-list-item-title>{{ alumno.nombre_completo }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ alumno.matricula }} • {{ alumno.programa }} • Sem. {{ alumno.semestre }}
              </v-list-item-subtitle>
              
              <template v-slot:append>
                <v-chip size="x-small" color="warning" variant="tonal">
                  {{ alumno.motivo }}
                </v-chip>
              </template>
            </v-list-item>
          </v-list>
          
          <v-card-text v-else class="text-center text-medium-emphasis py-8">
            <v-icon icon="mdi-check-circle" size="48" color="success" class="mb-2" />
            <div>No hay alumnos en riesgo actualmente</div>
          </v-card-text>
          
          <v-divider v-if="alumnosRiesgo.length > 5" />
          <v-card-actions v-if="alumnosRiesgo.length > 5">
            <v-btn color="primary" variant="text" to="/alumnos?requiere_individual=true">
              Ver todos ({{ alumnosRiesgo.length }})
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      
      <!-- Tutors stats -->
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-chart-bar" color="primary" class="mr-2" />
            Estadísticas por Tutor
          </v-card-title>
          <v-divider />
          
          <v-table v-if="tutoresStats.length" density="comfortable">
            <thead>
              <tr>
                <th>Tutor</th>
                <th class="text-center">Alumnos</th>
                <th class="text-center">Reportes</th>
                <th class="text-center">Pendientes</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tutor in tutoresStats.slice(0, 5)" :key="tutor.tutor_id">
                <td>{{ tutor.tutor_nombre }}</td>
                <td class="text-center">
                  <v-chip size="small" color="primary" variant="tonal">
                    {{ tutor.alumnos_asignados }}
                  </v-chip>
                </td>
                <td class="text-center">
                  <v-chip size="small" color="success" variant="tonal">
                    {{ tutor.reportes_subidos }}
                  </v-chip>
                </td>
                <td class="text-center">
                  <v-chip 
                    size="small" 
                    :color="tutor.reportes_pendientes > 0 ? 'warning' : 'default'"
                    variant="tonal"
                  >
                    {{ tutor.reportes_pendientes }}
                  </v-chip>
                </td>
              </tr>
            </tbody>
          </v-table>
          
          <v-card-text v-else class="text-center text-medium-emphasis py-8">
            <v-icon icon="mdi-account-group" size="48" class="mb-2" />
            <div>No hay tutores registrados</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Assignment Overview -->
    <v-row class="mt-2">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-account-arrow-right" color="info" class="mr-2" />
            Resumen de Asignaciones
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4" class="text-center">
                <div class="text-h3 font-weight-bold text-success">
                  {{ stats.alumnos_con_tutor }}
                </div>
                <div class="text-body-2 text-medium-emphasis">
                  Alumnos con tutor asignado
                </div>
              </v-col>
              <v-col cols="12" md="4" class="text-center">
                <div class="text-h3 font-weight-bold text-warning">
                  {{ stats.alumnos_sin_tutor }}
                </div>
                <div class="text-body-2 text-medium-emphasis">
                  Alumnos sin tutor
                </div>
              </v-col>
              <v-col cols="12" md="4" class="text-center">
                <div class="text-h3 font-weight-bold text-info">
                  {{ assignmentPercentage }}%
                </div>
                <div class="text-body-2 text-medium-emphasis">
                  Cobertura de asignación
                </div>
              </v-col>
            </v-row>
            
            <v-progress-linear
              :model-value="assignmentPercentage"
              height="12"
              rounded
              color="success"
              class="mt-4"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import StatCard from '@/components/StatCard.vue'
import dashboardService from '@/services/dashboard'

const loading = ref(false)
const stats = ref({
  total_alumnos: 0,
  total_tutores: 0,
  alumnos_con_tutor: 0,
  alumnos_sin_tutor: 0,
  alumnos_requieren_individual: 0,
  total_reportes: 0,
  reportes_pendientes: 0,
  reportes_procesados: 0,
  reportes_error: 0
})
const alumnosRiesgo = ref([])
const tutoresStats = ref([])

const assignmentPercentage = computed(() => {
  if (stats.value.total_alumnos === 0) return 0
  return Math.round((stats.value.alumnos_con_tutor / stats.value.total_alumnos) * 100)
})

const getInitials = (name) => {
  if (!name) return '?'
  const parts = name.split(' ')
  return parts.length > 1 
    ? `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    : name.substring(0, 2).toUpperCase()
}

const fetchData = async () => {
  loading.value = true
  try {
    const [dashboardData, riesgoData, tutoresData] = await Promise.all([
      dashboardService.getDashboard(),
      dashboardService.getAlumnosRiesgo(),
      dashboardService.getEstadisticasTutores()
    ])
    
    stats.value = dashboardData
    alumnosRiesgo.value = riesgoData
    tutoresStats.value = tutoresData
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>
