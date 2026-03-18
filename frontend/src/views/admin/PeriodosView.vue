<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Períodos Académicos</h1>
        <p class="text-body-2 text-medium-emphasis">
          Administra los períodos académicos del sistema
        </p>
      </div>
      <v-btn color="primary" @click="openCreateDialog">
        <v-icon icon="mdi-plus" class="mr-2" />
        Nuevo Período
      </v-btn>
    </div>

    <!-- Active Period Card -->
    <v-card v-if="periodoActivo" class="mb-6" color="success" variant="tonal">
      <v-card-text class="d-flex align-center">
        <v-icon icon="mdi-calendar-check" size="48" class="mr-4" />
        <div>
          <div class="text-h6 font-weight-bold">{{ periodoActivo.nombre }}</div>
          <div class="text-body-2">
            Período activo: {{ formatDate(periodoActivo.fecha_inicio) }} - {{ formatDate(periodoActivo.fecha_fin) }}
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- Periods Table -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="periodos"
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

        <template v-slot:item.fecha_inicio="{ item }">
          {{ formatDate(item.fecha_inicio) }}
        </template>

        <template v-slot:item.fecha_fin="{ item }">
          {{ formatDate(item.fecha_fin) }}
        </template>

        <template v-slot:item.activo="{ item }">
          <v-chip
            :color="item.activo ? 'success' : 'default'"
            :variant="item.activo ? 'flat' : 'tonal'"
            size="small"
          >
            {{ item.activo ? 'Activo' : 'Inactivo' }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn
            v-if="!item.activo"
            icon
            size="small"
            variant="text"
            color="success"
            @click="activarPeriodo(item)"
          >
            <v-icon icon="mdi-check" />
            <v-tooltip activator="parent" location="top">Activar</v-tooltip>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Create Dialog -->
    <v-dialog v-model="formDialog" max-width="500" persistent>
      <v-card>
        <v-card-title>Nuevo Período</v-card-title>
        <v-divider />
        <v-card-text>
          <v-form ref="formRef">
            <v-text-field
              v-model="form.clave"
              label="Clave"
              variant="outlined"
              :rules="[rules.required]"
              placeholder="Ej: 2026-1"
              class="mb-4"
            />
            <v-text-field
              v-model="form.nombre"
              label="Nombre"
              variant="outlined"
              :rules="[rules.required]"
              placeholder="Ej: Enero - Junio 2026"
              class="mb-4"
            />
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="form.fecha_inicio"
                  label="Fecha inicio"
                  variant="outlined"
                  type="date"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="form.fecha_fin"
                  label="Fecha fin"
                  variant="outlined"
                  type="date"
                  :rules="[rules.required]"
                />
              </v-col>
            </v-row>
            <v-switch
              v-model="form.activo"
              label="Activar inmediatamente"
              color="success"
              hide-details
            />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="formDialog = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="saving" @click="submitForm">
            Crear
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import adminService from '@/services/admin'

const showMessage = inject('showMessage')

const loading = ref(false)
const saving = ref(false)
const periodos = ref([])
const formDialog = ref(false)
const formRef = ref(null)

const form = ref({
  clave: '',
  nombre: '',
  fecha_inicio: '',
  fecha_fin: '',
  activo: false
})

const headers = [
  { title: 'Clave', key: 'clave', width: '100px' },
  { title: 'Nombre', key: 'nombre', sortable: true },
  { title: 'Inicio', key: 'fecha_inicio', width: '120px' },
  { title: 'Fin', key: 'fecha_fin', width: '120px' },
  { title: 'Estado', key: 'activo', align: 'center', width: '100px' },
  { title: '', key: 'actions', sortable: false, width: '60px' }
]

const rules = {
  required: v => !!v || 'Campo requerido'
}

const periodoActivo = computed(() => {
  return periodos.value.find(p => p.activo)
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const fetchPeriodos = async () => {
  loading.value = true
  try {
    const response = await adminService.getPeriodos()
    periodos.value = response.results || response
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  form.value = {
    clave: '',
    nombre: '',
    fecha_inicio: '',
    fecha_fin: '',
    activo: false
  }
  formDialog.value = true
}

const submitForm = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  saving.value = true
  try {
    await adminService.createPeriodo(form.value)
    showMessage?.('Período creado', 'success')
    formDialog.value = false
    fetchPeriodos()
  } catch (error) {
    console.error('Error:', error)
    showMessage?.('Error al crear período', 'error')
  } finally {
    saving.value = false
  }
}

const activarPeriodo = async (periodo) => {
  try {
    await adminService.activarPeriodo(periodo.id)
    showMessage?.('Período activado', 'success')
    fetchPeriodos()
  } catch (error) {
    console.error('Error:', error)
    showMessage?.('Error al activar período', 'error')
  }
}

onMounted(() => {
  fetchPeriodos()
})
</script>
