<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Gestión de Usuarios</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Administración de tutores y coordinadores
        </p>
      </div>
      <v-btn color="primary" prepend-icon="mdi-account-plus" @click="openDialog()">
        Nuevo Usuario
      </v-btn>
    </div>

    <!-- Filtros -->
    <v-card class="mb-6" variant="outlined">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              prepend-inner-icon="mdi-magnify"
              label="Buscar por nombre o matrícula"
              hide-details
              density="compact"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="roleFilter"
              :items="roles"
              label="Filtrar por rol"
              hide-details
              density="compact"
              clearable
            ></v-select>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Tabla de Usuarios -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="filteredUsuarios"
        :loading="loading"
        hover
      >
        <template v-slot:item.rol="{ item }">
          <v-chip
            :color="getRoleColor(item.rol)"
            size="small"
            class="text-uppercase font-weight-bold"
          >
            {{ item.rol }}
          </v-chip>
        </template>

        <template v-slot:item.is_active="{ item }">
          <v-chip
            :color="item.is_active ? 'success' : 'error'"
            size="small"
          >
            {{ item.is_active ? 'Activo' : 'Inactivo' }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn
            icon="mdi-pencil"
            variant="text"
            size="small"
            color="primary"
            @click="openDialog(item)"
          ></v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Dialog Create/Edit -->
    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title class="text-h5 pb-4 pt-6 px-6 bg-primary text-white">
          {{ editedItem.id ? 'Editar Usuario' : 'Nuevo Usuario' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="form" v-model="valid" @submit.prevent="save">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedItem.username"
                  label="Usuario (Matrícula/No. Empleado)"
                  :rules="[v => !!v || 'Campo requerido']"
                  :disabled="!!editedItem.id"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedItem.email"
                  label="Correo Electrónico"
                  type="email"
                  :rules="[v => !!v || 'Campo requerido', v => /.+@.+\..+/.test(v) || 'Email inválido']"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedItem.first_name"
                  label="Nombre(s)"
                  :rules="[v => !!v || 'Campo requerido']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedItem.last_name"
                  label="Apellidos"
                  :rules="[v => !!v || 'Campo requerido']"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <v-select
                  v-model="editedItem.rol"
                  :items="roles"
                  label="Rol en el sistema"
                  :rules="[v => !!v || 'Campo requerido']"
                ></v-select>
              </v-col>
              
              <v-col cols="12" v-if="!editedItem.id">
                <v-text-field
                  v-model="editedItem.password"
                  label="Contraseña Temporal"
                  type="password"
                  :rules="[v => !!v || 'Campo requerido', v => v.length >= 8 || 'Mínimo 8 caracteres']"
                  hint="El usuario deberá cambiarla al iniciar sesión"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="12" v-if="editedItem.id">
                <v-switch
                  v-model="editedItem.is_active"
                  label="Usuario Activo"
                  color="primary"
                ></v-switch>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions class="pa-4 bg-grey-lighten-4">
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="closeDialog">
            Cancelar
          </v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="save">
            Guardar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import authService from '@/services/auth'

const showMessage = inject('showMessage')

// Data
const usuarios = ref([])
const loading = ref(true)
const search = ref('')
const roleFilter = ref(null)
const dialog = ref(false)
const valid = ref(false)
const saving = ref(false)
const form = ref(null)

const roles = [
  { title: 'Tutor', value: 'tutor' },
  { title: 'Coordinador', value: 'coordinador' },
  { title: 'Jefe de Departamento', value: 'jefe' }
]

const headers = [
  { title: 'Usuario', key: 'username', sortable: true },
  { title: 'Nombre', key: 'first_name', sortable: true },
  { title: 'Apellidos', key: 'last_name', sortable: true },
  { title: 'Rol', key: 'rol', sortable: true },
  { title: 'Estado', key: 'is_active', sortable: true },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' }
]

const defaultItem = {
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  rol: 'tutor',
  password: '',
  is_active: true
}

const editedItem = ref({ ...defaultItem })

// Computed
const filteredUsuarios = computed(() => {
  let result = usuarios.value

  if (search.value) {
    const s = search.value.toLowerCase()
    result = result.filter(u => 
      u.username.toLowerCase().includes(s) || 
      (u.first_name + ' ' + u.last_name).toLowerCase().includes(s)
    )
  }

  if (roleFilter.value) {
    result = result.filter(u => u.rol === roleFilter.value)
  }

  return result
})

// Methods
const loadUsuarios = async () => {
  loading.value = true
  try {
    usuarios.value = await authService.getUsuarios()
  } catch (error) {
    showMessage('Error al cargar usuarios', 'error')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const getRoleColor = (rol) => {
  const colors = {
    tutor: 'info',
    coordinador: 'secondary',
    jefe: 'primary'
  }
  return colors[rol] || 'grey'
}

const openDialog = (item = null) => {
  if (item) {
    editedItem.value = { ...item }
  } else {
    editedItem.value = { ...defaultItem }
  }
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
  setTimeout(() => {
    editedItem.value = { ...defaultItem }
    if (form.value) form.value.resetValidation()
  }, 300)
}

const save = async () => {
  if (!form.value.isValid) {
    const validation = await form.value.validate()
    if (!validation.valid) return
  }

  saving.value = true
  try {
    if (editedItem.value.id) {
      // Update
      const { password, ...updateData } = editedItem.value
      await authService.updateUsuario(editedItem.value.id, updateData)
      showMessage('Usuario actualizado exitosamente')
    } else {
      // Create
      await authService.createUsuario(editedItem.value)
      showMessage('Usuario creado exitosamente')
    }
    closeDialog()
    await loadUsuarios()
  } catch (error) {
    const msg = error.response?.data?.error || 'Error al guardar el usuario'
    showMessage(msg, 'error')
    console.error(error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadUsuarios()
})
</script>
