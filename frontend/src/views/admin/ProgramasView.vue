<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Programas Educativos</h1>
        <p class="text-body-2 text-medium-emphasis">
          Administra los programas educativos del sistema
        </p>
      </div>
      <v-btn color="primary" @click="openCreateDialog">
        <v-icon icon="mdi-plus" class="mr-2" />
        Nuevo Programa
      </v-btn>
    </div>

    <!-- Programs Table -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="programas"
        :loading="loading"
        :items-per-page="15"
        hover
        class="elevation-0"
      >
        <template v-slot:item.clave="{ item }">
          <v-chip size="small" color="primary" variant="tonal">
            {{ item.clave }}
          </v-chip>
        </template>

        <template v-slot:item.unidad_nombre="{ item }">
          <span class="text-body-2">{{ item.unidad_nombre }}</span>
        </template>

        <template v-slot:item.duracion_semestres="{ item }">
          <v-chip size="small" variant="tonal">
            {{ item.duracion_semestres }} semestres
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
          <v-btn icon size="small" variant="text" color="primary" @click="editPrograma(item)">
            <v-icon icon="mdi-pencil" />
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Create/Edit Dialog -->
    <v-dialog v-model="formDialog" max-width="500" persistent>
      <v-card>
        <v-card-title>
          {{ isEditing ? 'Editar Programa' : 'Nuevo Programa' }}
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form ref="formRef">
            <v-text-field
              v-model="form.clave"
              label="Clave"
              variant="outlined"
              :rules="[rules.required]"
              :disabled="isEditing"
              class="mb-4"
            />
            <v-text-field
              v-model="form.nombre"
              label="Nombre del programa"
              variant="outlined"
              :rules="[rules.required]"
              class="mb-4"
            />
            <v-select
              v-model="form.unidad"
              label="Unidad Académica"
              :items="unidades"
              item-title="nombre"
              item-value="id"
              variant="outlined"
              :rules="[rules.required]"
              class="mb-4"
            />
            <v-text-field
              v-model.number="form.duracion_semestres"
              label="Duración (semestres)"
              variant="outlined"
              type="number"
              min="1"
              max="15"
              :rules="[rules.required]"
              class="mb-4"
            />
            <v-switch
              v-model="form.activo"
              label="Activo"
              color="success"
              hide-details
            />
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
  </v-container>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import adminService from '@/services/admin'

const showMessage = inject('showMessage')

const loading = ref(false)
const saving = ref(false)
const programas = ref([])
const unidades = ref([])
const formDialog = ref(false)
const isEditing = ref(false)
const formRef = ref(null)

const form = ref({
  clave: '',
  nombre: '',
  unidad: null,
  duracion_semestres: 9,
  activo: true
})

const headers = [
  { title: 'Clave', key: 'clave', width: '100px' },
  { title: 'Nombre', key: 'nombre', sortable: true },
  { title: 'Unidad Académica', key: 'unidad_nombre' },
  { title: 'Duración', key: 'duracion_semestres', align: 'center', width: '130px' },
  { title: 'Activo', key: 'activo', align: 'center', width: '80px' },
  { title: '', key: 'actions', sortable: false, width: '60px' }
]

const rules = {
  required: v => !!v || v === 0 || 'Campo requerido'
}

const fetchProgramas = async () => {
  loading.value = true
  try {
    const response = await adminService.getProgramas()
    programas.value = response.results || response
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

const fetchUnidades = async () => {
  try {
    const response = await adminService.getUnidades()
    unidades.value = response.results || response
  } catch (error) {
    console.error('Error:', error)
  }
}

const openCreateDialog = () => {
  isEditing.value = false
  form.value = {
    clave: '',
    nombre: '',
    unidad: null,
    duracion_semestres: 9,
    activo: true
  }
  formDialog.value = true
}

const editPrograma = (programa) => {
  isEditing.value = true
  form.value = { ...programa }
  formDialog.value = true
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
      await adminService.updatePrograma(form.value.id, form.value)
      showMessage?.('Programa actualizado', 'success')
    } else {
      await adminService.createPrograma(form.value)
      showMessage?.('Programa creado', 'success')
    }
    closeFormDialog()
    fetchProgramas()
  } catch (error) {
    console.error('Error:', error)
    showMessage?.('Error al guardar', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchProgramas()
  fetchUnidades()
})
</script>
