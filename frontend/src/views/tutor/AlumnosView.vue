<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Mis Alumnos</h1>
        <p class="text-body-2 text-medium-emphasis">
          Alumnos asignados a tu tutoría
        </p>
      </div>
      <v-chip color="primary" variant="tonal" size="large">
        <v-icon icon="mdi-account-group" class="mr-2" />
        {{ alumnos.length }} alumnos
      </v-chip>
    </div>

    <!-- Filters -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="filtros.buscar"
              label="Buscar alumno"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filtros.semestre"
              label="Semestre"
              :items="semestres"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filtros.requiereIndividual"
              label="Tipo de atención"
              :items="tiposAtencion"
              item-title="text"
              item-value="value"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="2" class="d-flex align-center">
            <v-btn color="primary" variant="tonal" @click="fetchAlumnos" block>
              <v-icon icon="mdi-refresh" class="mr-2" />
              Actualizar
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Students Table -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="filteredAlumnos"
        :loading="loading"
        :items-per-page="15"
        hover
        class="elevation-0"
      >
        <template v-slot:item.nombre_completo="{ item }">
          <div class="d-flex align-center py-2">
            <v-avatar size="36" color="primary" class="mr-3">
              <span class="text-body-2">{{ getInitials(item.nombre_completo) }}</span>
            </v-avatar>
            <div>
              <div class="font-weight-medium">{{ item.nombre_completo }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.matricula }}</div>
            </div>
          </div>
        </template>

        <template v-slot:item.semestre="{ item }">
          <v-chip size="small" variant="tonal" color="info">
            {{ item.semestre }}° semestre
          </v-chip>
        </template>

        <template v-slot:item.requiere_tutoria_individual="{ item }">
          <v-chip 
            size="small" 
            :color="item.requiere_tutoria_individual ? 'warning' : 'success'"
            variant="tonal"
          >
            <v-icon 
              :icon="item.requiere_tutoria_individual ? 'mdi-alert' : 'mdi-account-group'" 
              size="small" 
              class="mr-1" 
            />
            {{ item.requiere_tutoria_individual ? 'Individual' : 'Grupal' }}
          </v-chip>
        </template>

        <template v-slot:item.activo="{ item }">
          <v-icon 
            :icon="item.activo ? 'mdi-check-circle' : 'mdi-close-circle'" 
            :color="item.activo ? 'success' : 'error'"
            size="small"
          />
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            size="small"
            variant="text"
            color="primary"
            @click="showDetails(item)"
          >
            <v-icon icon="mdi-eye" />
            <v-tooltip activator="parent" location="top">Ver detalles</v-tooltip>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="600">
      <v-card v-if="selectedAlumno">
        <v-card-title class="d-flex align-center">
          <v-avatar size="48" color="primary" class="mr-4">
            <span class="text-h6">{{ getInitials(selectedAlumno.nombre_completo) }}</span>
          </v-avatar>
          <div>
            <div>{{ selectedAlumno.nombre_completo }}</div>
            <div class="text-body-2 text-medium-emphasis">{{ selectedAlumno.matricula }}</div>
          </div>
        </v-card-title>

        <v-divider />

        <v-card-text>
          <v-list density="compact">
            <v-list-item>
              <template v-slot:prepend>
                <v-icon icon="mdi-email" color="primary" />
              </template>
              <v-list-item-title>{{ selectedAlumno.email || 'No registrado' }}</v-list-item-title>
              <v-list-item-subtitle>Correo electrónico</v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <template v-slot:prepend>
                <v-icon icon="mdi-phone" color="primary" />
              </template>
              <v-list-item-title>{{ selectedAlumno.telefono || 'No registrado' }}</v-list-item-title>
              <v-list-item-subtitle>Teléfono</v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <template v-slot:prepend>
                <v-icon icon="mdi-school" color="primary" />
              </template>
              <v-list-item-title>{{ selectedAlumno.programa_nombre }}</v-list-item-title>
              <v-list-item-subtitle>Programa educativo</v-list-item-subtitle>
            </v-list-item>

            <v-list-item>
              <template v-slot:prepend>
                <v-icon icon="mdi-calendar" color="primary" />
              </template>
              <v-list-item-title>{{ selectedAlumno.semestre }}° semestre</v-list-item-title>
              <v-list-item-subtitle>Semestre actual</v-list-item-subtitle>
            </v-list-item>
          </v-list>

          <v-alert
            v-if="selectedAlumno.requiere_tutoria_individual"
            type="warning"
            variant="tonal"
            class="mt-4"
          >
            <div class="font-weight-medium">Requiere tutoría individual</div>
            <div class="text-body-2 mt-1">
              {{ selectedAlumno.motivo_tutoria_individual || 'Sin motivo especificado' }}
            </div>
          </v-alert>
        </v-card-text>

        <v-divider />

        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="detailsDialog = false">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import alumnosService from '@/services/alumnos'

const loading = ref(false)
const alumnos = ref([])
const detailsDialog = ref(false)
const selectedAlumno = ref(null)

const filtros = ref({
  buscar: '',
  semestre: null,
  requiereIndividual: null
})

const headers = [
  { title: 'Alumno', key: 'nombre_completo', sortable: true },
  { title: 'Semestre', key: 'semestre', align: 'center', width: '140px' },
  { title: 'Atención', key: 'requiere_tutoria_individual', align: 'center', width: '140px' },
  { title: 'Activo', key: 'activo', align: 'center', width: '80px' },
  { title: '', key: 'actions', sortable: false, width: '60px' }
]

const semestres = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

const tiposAtencion = [
  { text: 'Tutoría Individual', value: true },
  { text: 'Tutoría Grupal', value: false }
]

const filteredAlumnos = computed(() => {
  let result = alumnos.value

  if (filtros.value.buscar) {
    const search = filtros.value.buscar.toLowerCase()
    result = result.filter(a =>
      a.nombre_completo?.toLowerCase().includes(search) ||
      a.matricula?.toLowerCase().includes(search)
    )
  }

  if (filtros.value.semestre) {
    result = result.filter(a => a.semestre === filtros.value.semestre)
  }

  if (filtros.value.requiereIndividual !== null) {
    result = result.filter(a => a.requiere_tutoria_individual === filtros.value.requiereIndividual)
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

const fetchAlumnos = async () => {
  loading.value = true
  try {
    const response = await alumnosService.getAll()
    alumnos.value = response.results || response
  } catch (error) {
    console.error('Error fetching alumnos:', error)
  } finally {
    loading.value = false
  }
}

const showDetails = async (alumno) => {
  try {
    const details = await alumnosService.getById(alumno.id)
    selectedAlumno.value = details
    detailsDialog.value = true
  } catch (error) {
    console.error('Error fetching alumno details:', error)
    selectedAlumno.value = alumno
    detailsDialog.value = true
  }
}

onMounted(() => {
  fetchAlumnos()
})
</script>
