<template>
  <v-chip
    :color="statusConfig.color"
    :text="statusConfig.label"
    size="small"
    label
  >
    <template v-slot:prepend>
      <v-icon :icon="statusConfig.icon" size="small" class="mr-1" />
    </template>
  </v-chip>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const statusConfig = computed(() => {
  const configs = {
    pendiente: {
      color: 'warning',
      label: 'Pendiente',
      icon: 'mdi-clock-outline'
    },
    procesando: {
      color: 'info',
      label: 'Procesando',
      icon: 'mdi-loading mdi-spin'
    },
    procesado: {
      color: 'success',
      label: 'Procesado',
      icon: 'mdi-check-circle'
    },
    error: {
      color: 'error',
      label: 'Error',
      icon: 'mdi-alert-circle'
    }
  }
  
  return configs[props.status] || configs.pendiente
})
</script>
