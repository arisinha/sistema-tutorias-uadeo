<template>
  <v-card class="stat-card card-hover" :color="color" variant="tonal">
    <v-card-text class="d-flex align-center pa-4">
      <div class="flex-grow-1">
        <div class="text-body-2 text-medium-emphasis mb-1">{{ title }}</div>
        <div class="text-h4 font-weight-bold">{{ formattedValue }}</div>
        <div v-if="subtitle" class="text-caption text-medium-emphasis mt-1">
          {{ subtitle }}
        </div>
      </div>
      <v-avatar :color="color" size="56" class="elevation-2">
        <v-icon :icon="icon" size="28" color="white" />
      </v-avatar>
    </v-card-text>
    
    <v-divider v-if="$slots.footer" />
    
    <v-card-actions v-if="$slots.footer" class="pa-3">
      <slot name="footer" />
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  icon: {
    type: String,
    default: 'mdi-chart-bar'
  },
  color: {
    type: String,
    default: 'primary'
  },
  subtitle: {
    type: String,
    default: ''
  }
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString('es-MX')
  }
  return props.value
})
</script>

<style scoped>
.stat-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
</style>
