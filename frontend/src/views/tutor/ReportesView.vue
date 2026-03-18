<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Mis Reportes</h1>
        <p class="text-body-2 text-medium-emphasis">
          Gestiona tus reportes de tutoría
        </p>
      </div>
      <v-btn color="primary" @click="uploadDialog = true">
        <v-icon icon="mdi-upload" class="mr-2" />
        Subir Reporte
      </v-btn>
    </div>

    <!-- Filters -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="filtros.tipo"
              label="Tipo de reporte"
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
          <v-col cols="12" md="2" class="d-flex align-center">
            <v-btn color="primary" variant="tonal" @click="fetchReportes" block>
              <v-icon icon="mdi-refresh" class="mr-2" />
              Actualizar
            </v-btn>
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
        :items-per-page="15"
        hover
        class="elevation-0"
      >
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
          <v-btn
            icon
            size="small"
            variant="text"
            color="primary"
            @click="downloadReport(item)"
          >
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
        </template>
      </v-data-table>
    </v-card>

    <!-- Upload Dialog -->
    <v-dialog v-model="uploadDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-file-upload" color="primary" class="mr-2" />
          Subir Nuevo Reporte
        </v-card-title>

        <v-divider />

        <v-card-text>
          <v-form ref="uploadFormRef">
            <v-select
              v-model="uploadForm.tipo_reporte"
              label="Tipo de reporte"
              :items="tiposReporte"
              item-title="text"
              item-value="value"
              variant="outlined"
              :rules="[rules.required]"
              class="mb-4"
            >
              <template v-slot:append-inner>
                <v-btn
                  v-if="uploadForm.tipo_reporte"
                  icon
                  size="x-small"
                  variant="text"
                  @click.stop="downloadTemplate(uploadForm.tipo_reporte)"
                >
                  <v-icon icon="mdi-download" size="small" />
                  <v-tooltip activator="parent" location="top">
                    Descargar plantilla
                  </v-tooltip>
                </v-btn>
              </template>
            </v-select>

            <v-select
              v-model="uploadForm.periodo"
              label="Período académico"
              :items="periodos"
              item-title="nombre"
              item-value="id"
              variant="outlined"
              :rules="[rules.required]"
              class="mb-4"
            />

            <v-file-input
              v-model="uploadForm.archivo"
              label="Archivo Excel"
              accept=".xlsx,.xls"
              variant="outlined"
              prepend-icon="mdi-file-excel"
              :rules="[rules.required, rules.excel]"
              show-size
            />

            <v-alert
              type="info"
              variant="tonal"
              density="compact"
              class="mt-4"
            >
              <div class="text-body-2">
                <strong>Instrucciones:</strong>
                <ol class="mt-2 mb-0">
                  <li>Descarga la plantilla del tipo de reporte</li>
                  <li>Completa los datos siguiendo el formato</li>
                  <li>Sube el archivo Excel completado</li>
                </ol>
              </div>
            </v-alert>
          </v-form>
        </v-card-text>

        <v-divider />

        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeUploadDialog">
            Cancelar
          </v-btn>
          <v-btn color="primary" :loading="uploading" @click="submitUpload">
            <v-icon icon="mdi-upload" class="mr-2" />
            Subir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import reportesService from '@/services/reportes'
import adminService from '@/services/admin'

const showMessage = inject('showMessage')

const loading = ref(false)
const uploading = ref(false)
const reportes = ref([])
const periodos = ref([])
const uploadDialog = ref(false)
const uploadFormRef = ref(null)

const filtros = ref({
  tipo: null,
  estado: null,
  periodo: null
})

const uploadForm = ref({
  tipo_reporte: null,
  periodo: null,
  archivo: null
})

const headers = [
  { title: 'Tipo', key: 'tipo_reporte', width: '200px' },
  { title: 'Período', key: 'periodo_nombre', sortable: true },
  { title: 'Estado', key: 'estado', align: 'center', width: '150px' },
  { title: 'Fecha', key: 'fecha_subida', sortable: true, width: '150px' },
  { title: '', key: 'actions', sortable: false, width: '100px' }
]

const tiposReporte = [
  { text: 'Tutoría Individual - Inicial', value: 'ind_inicial' },
  { text: 'Tutoría Individual - Medio Semestre', value: 'ind_medio' },
  { text: 'Tutoría Individual - Final', value: 'ind_final' },
  { text: 'Tutoría Grupal - Inicial', value: 'grup_inicial' },
  { text: 'Tutoría Grupal - Medio Semestre', value: 'grup_medio' },
  { text: 'Tutoría Grupal - Final', value: 'grup_final' }
]

const estadosReporte = [
  { text: 'Pendiente', value: 'pendiente' },
  { text: 'Procesando', value: 'procesando' },
  { text: 'Procesado', value: 'procesado' },
  { text: 'Error', value: 'error' }
]

const rules = {
  required: v => !!v || 'Campo requerido',
  excel: v => !v || v[0]?.name?.match(/\.(xlsx|xls)$/) || 'Debe ser archivo Excel'
}

const filteredReportes = computed(() => {
  let result = reportes.value

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
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchReportes = async () => {
  loading.value = true
  try {
    const response = await reportesService.getAll()
    reportes.value = response.results || response
  } catch (error) {
    console.error('Error fetching reportes:', error)
  } finally {
    loading.value = false
  }
}

const fetchPeriodos = async () => {
  try {
    const response = await adminService.getPeriodos()
    periodos.value = response.results || response
  } catch (error) {
    console.error('Error fetching periodos:', error)
  }
}

const downloadReport = (reporte) => {
  reportesService.descargarArchivo(reporte.id)
}

const downloadTemplate = (tipo) => {
  reportesService.descargarPlantilla(tipo)
}

const reprocesar = async (reporte) => {
  try {
    await reportesService.reprocesar(reporte.id)
    showMessage?.('Reprocesamiento iniciado', 'success')
    fetchReportes()
  } catch (error) {
    console.error('Error reprocesando:', error)
    showMessage?.('Error al reprocesar reporte', 'error')
  }
}

const closeUploadDialog = () => {
  uploadDialog.value = false
  uploadForm.value = {
    tipo_reporte: null,
    periodo: null,
    archivo: null
  }
}

const submitUpload = async () => {
  const { valid } = await uploadFormRef.value.validate()
  if (!valid) return

  uploading.value = true
  try {
    const file = uploadForm.value.archivo[0]
    await reportesService.subir(file, uploadForm.value.tipo_reporte, uploadForm.value.periodo)
    showMessage?.('Reporte subido exitosamente', 'success')
    closeUploadDialog()
    fetchReportes()
  } catch (error) {
    console.error('Error uploading report:', error)
    showMessage?.('Error al subir reporte', 'error')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchReportes()
  fetchPeriodos()
})
</script>
