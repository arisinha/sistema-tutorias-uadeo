<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Asignación de Tutores</h1>
        <p class="text-body-2 text-medium-emphasis">
          Asigna alumnos a tutores
        </p>
      </div>
      <v-chip color="warning" variant="tonal" size="large">
        <v-icon icon="mdi-account-alert" class="mr-2" />
        {{ alumnosSinTutor.length }} sin asignar
      </v-chip>
    </div>

    <v-row>
      <!-- Left: Students without tutor -->
      <v-col cols="12" lg="7">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <v-icon icon="mdi-account-group" color="warning" class="mr-2" />
              Alumnos sin Tutor
            </div>
            <v-text-field
              v-model="searchAlumnos"
              label="Buscar"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              style="max-width: 250px"
              clearable
            />
          </v-card-title>
          <v-divider />

          <v-data-table
            v-model="selectedAlumnos"
            :headers="alumnosHeaders"
            :items="filteredAlumnosSinTutor"
            :loading="loading"
            :items-per-page="10"
            item-value="id"
            return-object
            show-select
            hover
            class="elevation-0"
          >
            <template v-slot:item.nombre_completo="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" color="primary" class="mr-2">
                  <span class="text-caption">{{ getInitials(item.nombre_completo) }}</span>
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ item.nombre_completo }}</div>
                  <div class="text-caption text-medium-emphasis">{{ item.matricula }}</div>
                </div>
              </div>
            </template>

            <template v-slot:item.semestre="{ item }">
              <v-chip size="x-small" variant="tonal" color="info">
                {{ item.semestre }}°
              </v-chip>
            </template>
          </v-data-table>
        </v-card>
      </v-col>

      <!-- Right: Tutors and assignment -->
      <v-col cols="12" lg="5">
        <!-- Assign Panel -->
        <v-card class="mb-6" color="primary" variant="tonal">
          <v-card-text>
            <div class="text-subtitle-1 font-weight-bold mb-3">
              Asignar a Tutor
            </div>
            <v-select
              v-model="selectedTutor"
              label="Seleccionar tutor"
              :items="tutores"
              item-title="tutor_nombre"
              item-value="tutor_id"
              variant="outlined"
              density="comfortable"
              hide-details
              class="mb-4"
            >
              <template v-slot:item="{ props, item }">
                <v-list-item v-bind="props">
                  <template v-slot:append>
                    <v-chip size="x-small" color="info" variant="flat">
                      {{ item.raw.alumnos_asignados }} alumnos
                    </v-chip>
                  </template>
                </v-list-item>
              </template>
            </v-select>

            <v-btn
              color="primary"
              :disabled="!selectedTutor || selectedAlumnos.length === 0"
              :loading="assigning"
              block
              @click="asignarTutor"
            >
              <v-icon icon="mdi-account-arrow-right" class="mr-2" />
              Asignar {{ selectedAlumnos.length }} alumno(s)
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Tutor Stats -->
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-chart-bar" color="primary" class="mr-2" />
            Carga por Tutor
          </v-card-title>
          <v-divider />

          <v-list density="compact">
            <v-list-item
              v-for="tutor in tutores"
              :key="tutor.tutor_id"
              :class="{ 'bg-primary-lighten-5': selectedTutor === tutor.tutor_id }"
            >
              <template v-slot:prepend>
                <v-avatar size="36" color="primary" variant="tonal">
                  <span class="text-caption">{{ getInitials(tutor.tutor_nombre) }}</span>
                </v-avatar>
              </template>

              <v-list-item-title>{{ tutor.tutor_nombre }}</v-list-item-title>
              
              <template v-slot:append>
                <div class="d-flex gap-2">
                  <v-chip size="x-small" color="primary" variant="tonal">
                    {{ tutor.alumnos_asignados }} alumnos
                  </v-chip>
                </div>
              </template>
            </v-list-item>
          </v-list>

          <v-card-text v-if="tutores.length === 0" class="text-center text-medium-emphasis">
            No hay tutores registrados
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import alumnosService from '@/services/alumnos'
import dashboardService from '@/services/dashboard'

const showMessage = inject('showMessage')

const loading = ref(false)
const assigning = ref(false)
const alumnos = ref([])
const tutores = ref([])
const selectedAlumnos = ref([])
const selectedTutor = ref(null)
const searchAlumnos = ref('')

const alumnosHeaders = [
  { title: 'Alumno', key: 'nombre_completo', sortable: true },
  { title: 'Sem.', key: 'semestre', align: 'center', width: '70px' }
]

const alumnosSinTutor = computed(() => {
  return alumnos.value.filter(a => !a.tutor)
})

const filteredAlumnosSinTutor = computed(() => {
  if (!searchAlumnos.value) return alumnosSinTutor.value
  const search = searchAlumnos.value.toLowerCase()
  return alumnosSinTutor.value.filter(a =>
    a.nombre_completo?.toLowerCase().includes(search) ||
    a.matricula?.toLowerCase().includes(search)
  )
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
    const [alumnosRes, tutoresRes] = await Promise.all([
      alumnosService.getAll({ sin_tutor: 'true' }),
      dashboardService.getEstadisticasTutores()
    ])
    alumnos.value = alumnosRes.results || alumnosRes
    tutores.value = tutoresRes || []
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    loading.value = false
  }
}

const asignarTutor = async () => {
  if (!selectedTutor.value || selectedAlumnos.value.length === 0) return

  assigning.value = true
  try {
    // Vuetify 3 v-data-table stores selected items as raw values (IDs) or objects
    const alumnoIds = selectedAlumnos.value.map(a => typeof a === 'object' ? a.id : a)
    await alumnosService.asignarTutor(alumnoIds, selectedTutor.value)
    showMessage?.(`${alumnoIds.length} alumnos asignados correctamente`, 'success')
    selectedAlumnos.value = []
    selectedTutor.value = null
    fetchData()
  } catch (error) {
    console.error('Error assigning tutor:', error)
    showMessage?.('Error al asignar tutor', 'error')
  } finally {
    assigning.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
