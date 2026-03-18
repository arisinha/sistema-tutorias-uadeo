<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Gestión de Alumnos</h1>
        <p class="text-body-2 text-medium-emphasis">
          Administra y supervisa todos los alumnos del programa
        </p>
      </div>
      <div class="d-flex gap-2">
        <v-btn color="secondary" variant="tonal" @click="importDialog = true">
          <v-icon icon="mdi-file-import" class="mr-2" />
          Importar Excel
        </v-btn>
        <v-btn color="primary" @click="openCreateDialog">
          <v-icon icon="mdi-plus" class="mr-2" />
          Nuevo Alumno
        </v-btn>
      </div>
    </div>

    <!-- Filters -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
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
          <v-col cols="12" md="2">
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
          <v-col cols="12" md="2">
            <v-select
              v-model="filtros.tutor"
              label="Tutor"
              :items="tutores"
              item-title="nombre"
              item-value="id"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-model="filtros.sinTutor"
              label="Asignación"
              :items="opcionesAsignacion"
              item-title="text"
              item-value="value"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="12" md="3" class="d-flex align-center gap-2">
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
        :items-per-page="20"
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
            {{ item.semestre }}°
          </v-chip>
        </template>

        <template v-slot:item.tutor_nombre="{ item }">
          <v-chip 
            v-if="item.tutor_nombre"
            size="small" 
            variant="tonal"
            color="success"
          >
            {{ item.tutor_nombre }}
          </v-chip>
          <v-chip 
            v-else
            size="small" 
            variant="tonal"
            color="warning"
          >
            Sin asignar
          </v-chip>
        </template>

        <template v-slot:item.requiere_tutoria_individual="{ item }">
          <v-icon 
            :icon="item.requiere_tutoria_individual ? 'mdi-alert' : 'mdi-check'" 
            :color="item.requiere_tutoria_individual ? 'warning' : 'success'"
            size="small"
          />
        </template>

        <template v-slot:item.activo="{ item }">
          <v-icon 
            :icon="item.activo ? 'mdi-check-circle' : 'mdi-close-circle'" 
            :color="item.activo ? 'success' : 'error'"
            size="small"
          />
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" variant="text" color="primary" @click="editAlumno(item)">
            <v-icon icon="mdi-pencil" />
          </v-btn>
          <v-btn icon size="small" variant="text" color="error" @click="confirmDelete(item)">
            <v-icon icon="mdi-delete" />
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Create/Edit Dialog -->
    <v-dialog v-model="formDialog" max-width="700" persistent>
      <v-card>
        <v-card-title>
          {{ isEditing ? 'Editar Alumno' : 'Nuevo Alumno' }}
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form ref="formRef">
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.matricula"
                  label="Matrícula"
                  variant="outlined"
                  :rules="[rules.required]"
                  :disabled="isEditing"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.nombre"
                  label="Nombre(s)"
                  variant="outlined"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.apellido_paterno"
                  label="Apellido Paterno"
                  variant="outlined"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.apellido_materno"
                  label="Apellido Materno"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.email"
                  label="Correo electrónico"
                  variant="outlined"
                  type="email"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="form.telefono"
                  label="Teléfono"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="form.programa_educativo"
                  label="Programa Educativo"
                  :items="programas"
                  item-title="nombre"
                  item-value="id"
                  variant="outlined"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="form.semestre"
                  label="Semestre"
                  :items="semestres"
                  variant="outlined"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="form.tutor"
                  label="Tutor"
                  :items="tutores"
                  item-title="nombre"
                  item-value="id"
                  variant="outlined"
                  clearable
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="form.requiere_tutoria_individual"
                  label="Requiere tutoría individual"
                  color="warning"
                  hide-details
                />
              </v-col>
              <v-col cols="12" v-if="form.requiere_tutoria_individual">
                <v-textarea
                  v-model="form.motivo_tutoria_individual"
                  label="Motivo"
                  variant="outlined"
                  rows="2"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeFormDialog">Cancelar</v-btn>
          <v-btn color="primary" :loading="saving" @click="submitForm">
            {{ isEditing ? 'Guardar' : 'Crear' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Import Dialog -->
    <v-dialog v-model="importDialog" max-width="500">
      <v-card>
        <v-card-title>Importar Alumnos</v-card-title>
        <v-divider />
        <v-card-text>
          <v-select
            v-model="importForm.programa"
            label="Programa Educativo"
            :items="programas"
            item-title="nombre"
            item-value="id"
            variant="outlined"
            class="mb-4"
          />
          <v-file-input
            v-model="importForm.archivo"
            label="Archivo Excel"
            accept=".xlsx,.xls"
            variant="outlined"
            prepend-icon="mdi-file-excel"
          />
          <v-btn
            color="secondary"
            variant="tonal"
            size="small"
            @click="downloadTemplate"
            class="mt-2"
          >
            <v-icon icon="mdi-download" class="mr-2" />
            Descargar plantilla
          </v-btn>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="importDialog = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="importing" @click="submitImport">
            Importar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirm Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title>Confirmar eliminación</v-card-title>
        <v-card-text>
          ¿Estás seguro de eliminar a <strong>{{ alumnoToDelete?.nombre_completo }}</strong>?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn color="error" :loading="deleting" @click="deleteAlumno">Eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import alumnosService from '@/services/alumnos'
import adminService from '@/services/admin'
import dashboardService from '@/services/dashboard'

const showMessage = inject('showMessage')

const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const deleting = ref(false)

const alumnos = ref([])
const tutores = ref([])
const programas = ref([])

const formDialog = ref(false)
const importDialog = ref(false)
const deleteDialog = ref(false)
const isEditing = ref(false)
const formRef = ref(null)
const alumnoToDelete = ref(null)

const filtros = ref({
  buscar: '',
  semestre: null,
  tutor: null,
  sinTutor: null
})

const form = ref({
  matricula: '',
  nombre: '',
  apellido_paterno: '',
  apellido_materno: '',
  email: '',
  telefono: '',
  programa_educativo: null,
  semestre: null,
  tutor: null,
  requiere_tutoria_individual: false,
  motivo_tutoria_individual: ''
})

const importForm = ref({
  programa: null,
  archivo: null
})

const headers = [
  { title: 'Alumno', key: 'nombre_completo', sortable: true },
  { title: 'Sem.', key: 'semestre', align: 'center', width: '80px' },
  { title: 'Tutor', key: 'tutor_nombre', width: '180px' },
  { title: 'Ind.', key: 'requiere_tutoria_individual', align: 'center', width: '60px' },
  { title: 'Act.', key: 'activo', align: 'center', width: '60px' },
  { title: '', key: 'actions', sortable: false, width: '100px' }
]

const semestres = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

const opcionesAsignacion = [
  { text: 'Sin tutor', value: 'sin' },
  { text: 'Con tutor', value: 'con' }
]

const rules = {
  required: v => !!v || 'Campo requerido'
}

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

  if (filtros.value.tutor) {
    result = result.filter(a => a.tutor === filtros.value.tutor)
  }

  if (filtros.value.sinTutor === 'sin') {
    result = result.filter(a => !a.tutor)
  } else if (filtros.value.sinTutor === 'con') {
    result = result.filter(a => a.tutor)
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
    // Fetch all pages
    let allAlumnos = []
    let page = 1
    let hasMore = true

    while (hasMore) {
      const response = await alumnosService.getAll({ page })
      if (response.results) {
        allAlumnos = allAlumnos.concat(response.results)
        hasMore = !!response.next
        page++
      } else {
        allAlumnos = response
        hasMore = false
      }
    }

    alumnos.value = allAlumnos
  } catch (error) {
    console.error('Error fetching alumnos:', error)
  } finally {
    loading.value = false
  }
}

const fetchTutores = async () => {
  try {
    const response = await dashboardService.getEstadisticasTutores()
    tutores.value = (response || []).map(t => ({
      id: t.tutor_id,
      nombre: t.tutor_nombre
    }))
  } catch (error) {
    console.error('Error fetching tutores:', error)
  }
}

const fetchProgramas = async () => {
  try {
    const response = await adminService.getProgramas()
    programas.value = response.results || response
  } catch (error) {
    console.error('Error fetching programas:', error)
  }
}

const openCreateDialog = () => {
  isEditing.value = false
  form.value = {
    matricula: '',
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    email: '',
    telefono: '',
    programa_educativo: null,
    semestre: null,
    tutor: null,
    requiere_tutoria_individual: false,
    motivo_tutoria_individual: ''
  }
  formDialog.value = true
}

const editAlumno = async (alumno) => {
  isEditing.value = true
  try {
    const details = await alumnosService.getById(alumno.id)
    form.value = { ...details }
    formDialog.value = true
  } catch (error) {
    console.error('Error:', error)
    form.value = { ...alumno }
    formDialog.value = true
  }
}

const closeFormDialog = () => {
  formDialog.value = false
}

const submitForm = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  saving.value = true
  try {
    if (isEditing.value) {
      await alumnosService.update(form.value.id, form.value)
      showMessage?.('Alumno actualizado', 'success')
    } else {
      await alumnosService.create(form.value)
      showMessage?.('Alumno creado', 'success')
    }
    closeFormDialog()
    fetchAlumnos()
  } catch (error) {
    console.error('Error:', error)
    showMessage?.('Error al guardar', 'error')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (alumno) => {
  alumnoToDelete.value = alumno
  deleteDialog.value = true
}

const deleteAlumno = async () => {
  deleting.value = true
  try {
    await alumnosService.delete(alumnoToDelete.value.id)
    showMessage?.('Alumno eliminado', 'success')
    deleteDialog.value = false
    fetchAlumnos()
  } catch (error) {
    console.error('Error:', error)
    showMessage?.('Error al eliminar', 'error')
  } finally {
    deleting.value = false
  }
}

const downloadTemplate = async () => {
  try {
    const blob = await alumnosService.descargarPlantilla()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'plantilla_alumnos.xlsx'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error:', error)
  }
}

const submitImport = async () => {
  if (!importForm.value.archivo || !importForm.value.programa) return

  importing.value = true
  try {
    const file = importForm.value.archivo[0]
    await alumnosService.importarExcel(file, importForm.value.programa)
    showMessage?.('Importación completada', 'success')
    importDialog.value = false
    fetchAlumnos()
  } catch (error) {
    console.error('Error:', error)
    showMessage?.('Error en importación', 'error')
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  fetchAlumnos()
  fetchTutores()
  fetchProgramas()
})
</script>
