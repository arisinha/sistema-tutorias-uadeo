<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Gestión de Reportes</h1>
        <p class="text-body-2 text-medium-emphasis">
          Supervisa los reportes de todos los tutores
        </p>
      </div>
      <v-btn color="primary" variant="tonal" @click="fetchReportes">
        <v-icon icon="mdi-refresh" class="mr-2" />
        Actualizar
      </v-btn>
    </div>

    <!-- Stats Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card color="primary" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-h4 font-weight-bold">{{ stats.total }}</div>
            <div class="text-body-2">Total Reportes</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card color="success" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-h4 font-weight-bold">{{ stats.procesados }}</div>
            <div class="text-body-2">Procesados</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card color="warning" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-h4 font-weight-bold">{{ stats.pendientes }}</div>
            <div class="text-body-2">Pendientes</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card color="error" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-h4 font-weight-bold">{{ stats.errores }}</div>
            <div class="text-body-2">Con Errores</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-select
              v-model="filtros.tutor"
              label="Tutor"
              :items="tutores"
              item-title="tutor_nombre"
              item-value="tutor_id"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filtros.tipo"
              label="Tipo"
              :items="tiposReporte"
              item-title="text"
              item-value="value"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filtros.estado"
              label="Estado"
              :items="estadosReporte"
              item-title="text"
              item-value="value"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filtros.periodo"
              label="Período"
              :items="periodos"
              item-title="nombre"
              item-value="id"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Reports Table -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="filteredReportes"
        :loading="loading"
        :items-per-page="20"
        hover
        class="elevation-0"
      >
        <template v-slot:item.tutor_nombre="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" color="primary" class="mr-2">
              <span class="text-caption">{{ getInitials(item.tutor_nombre) }}</span>
            </v-avatar>
            {{ item.tutor_nombre }}
          </div>
        </template>

        <template v-slot:item.tipo_reporte="{ item }">
          <v-chip
            size="small"
            :color="item.tipo_reporte?.startsWith('ind_') ? 'info' : 'secondary'"
            variant="tonal"
          >
            {{ getTipoDisplay(item.tipo_reporte) }}
          </v-chip>
        </template>

        <template v-slot:item.estado="{ item }">
          <v-chip
            size="small"
            :color="getEstadoColor(item.estado)"
            variant="tonal"
          >
            <v-icon :icon="getEstadoIcon(item.estado)" size="small" class="mr-1" />
            {{ getEstadoDisplay(item.estado) }}
          </v-chip>
        </template>

        <template v-slot:item.fecha_subida="{ item }">
          {{ formatDate(item.fecha_subida) }}
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" variant="text" color="primary" @click="downloadReport(item)">
            <v-icon icon="mdi-download" />
            <v-tooltip activator="parent" location="top">Descargar</v-tooltip>
          </v-btn>
          <v-btn
            v-if="item.estado === 'error'"
            icon
            size="small"
            variant="text"
            color="warning"
            @click="reprocesar(item)"
          >
            <v-icon icon="mdi-refresh" />
            <v-tooltip activator="parent" location="top">Reprocesar</v-tooltip>
          </v-btn>
          <v-btn icon size="small" variant="text" color="error" @click="confirmDelete(item)">
            <v-icon icon="mdi-delete" />
            <v-tooltip activator="parent" location="top">Eliminar</v-tooltip>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Delete Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title>Confirmar eliminación</v-card-title>
        <v-card-text>
          ¿Estás seguro de eliminar este reporte?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn color="error" :loading="deleting" @click="deleteReport">Eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import reportesService from '@/services/reportes'
import adminService from '@/services/admin'
import dashboardService from '@/services/dashboard'

const showMessage = inject('showMessage')

const loading = ref(false)
const deleting = ref(false)
const reportes = ref([])
const tutores = ref([])
const periodos = ref([])
const deleteDialog = ref(false)
const reporteToDelete = ref(null)

const filtros = ref({
  tutor: null,
  tipo: null,
  estado: null,
  periodo: null
})

const headers = [
  { title: 'Tutor', key: 'tutor_nombre', sortable: true },
  { title: 'Tipo', key: 'tipo_reporte' },
  { title: 'Período', key: 'periodo_nombre' },
  { title: 'Estado', key: 'estado', align: 'center' },
  { title: 'Fecha', key: 'fecha_subida', sortable: true },
  { title: '', key: 'actions', sortable: false, width: '120px' }
]

const tiposReporte = [
  { text: 'Individual - Inicial', value: 'ind_inicial' },
  { text: 'Individual - Medio', value: 'ind_medio' },
  { text: 'Individual - Final', value: 'ind_final' },
  { text: 'Grupal - Inicial', value: 'grup_inicial' },
  { text: 'Grupal - Medio', value: 'grup_medio' },
  { text: 'Grupal - Final', value: 'grup_final' }
]

const estadosReporte = [
  { text: 'Pendiente', value: 'pendiente' },
  { text: 'Procesando', value: 'procesando' },
  { text: 'Procesado', value: 'procesado' },
  { text: 'Error', value: 'error' }
]

const stats = computed(() => {
  const all = reportes.value
  return {
    total: all.length,
    procesados: all.filter(r => r.estado === 'procesado').length,
    pendientes: all.filter(r => r.estado === 'pendiente' || r.estado === 'procesando').length,
    errores: all.filter(r => r.estado === 'error').length
  }
})

const filteredReportes = computed(() => {
  let result = reportes.value

  if (filtros.value.tutor) {
    result = result.filter(r => r.tutor === filtros.value.tutor)
  }
  if (filtros.value.tipo) {
    result = result.filter(r => r.tipo_reporte === filtros.value.tipo)
  }
  if (filtros.value.estado) {
    result = result.filter(r => r.estado === filtros.value.estado)
  }
  if (filtros.value.periodo) {
    result = result.filter(r => r.periodo === filtros.value.periodo)
  }

  return result
})

const getInitials = (name) => {
  if (!name) return '?'
  const parts = name.split(' ')
  return parts.length > 1
    ? `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    : name.substring(0, 2).toUpperCase()
}

const getTipoDisplay = (tipo) => {
  return tiposReporte.find(t => t.value === tipo)?.text || tipo
}

const getEstadoDisplay = (estado) => {
  return estadosReporte.find(e => e.value === estado)?.text || estado
}

const getEstadoColor = (estado) => {
  const colors = {
    pendiente: 'warning',
    procesando: 'info',
    procesado: 'success',
    error: 'error'
  }
  return colors[estado] || 'default'
}

const getEstadoIcon = (estado) => {
  const icons = {
    pendiente: 'mdi-clock-outline',
    procesando: 'mdi-cog',
    procesado: 'mdi-check-circle',
    error: 'mdi-alert-circle'
  }
  return icons[estado] || 'mdi-help-circle'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const fetchReportes = async () => {
  loading.value = true
  try {
    const response = await reportesService.getAll()
    reportes.value = response.results || response
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

const fetchTutores = async () => {
  try {
    const response = await dashboardService.getEstadisticasTutores()
    tutores.value = response || []
  } catch (error) {
    console.error('Error:', error)
  }
}

const fetchPeriodos = async () => {
  try {
    const response = await adminService.getPeriodos()
    periodos.value = response.results || response
  } catch (error) {
    console.error('Error:', error)
  }
}

const downloadReport = (reporte) => {
  reportesService.descargarArchivo(reporte.id)
}

const reprocesar = async (reporte) => {
  try {
    await reportesService.reprocesar(reporte.id)
    showMessage?.('Reprocesamiento iniciado', 'success')
    fetchReportes()
  } catch (error) {
    console.error('Error:', error)
    showMessage?.('Error al reprocesar', 'error')
  }
}

const confirmDelete = (reporte) => {
  reporteToDelete.value = reporte
  deleteDialog.value = true
}

const deleteReport = async () => {
  deleting.value = true
  try {
    await reportesService.delete(reporteToDelete.value.id)
    showMessage?.('Reporte eliminado', 'success')
    deleteDialog.value = false
    fetchReportes()
  } catch (error) {
    console.error('Error:', error)
    showMessage?.('Error al eliminar', 'error')
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchReportes()
  fetchTutores()
  fetchPeriodos()
})
</script>
