<template>
  <v-card
    class="file-uploader pa-6"
    :class="{ 'drag-over': isDragging }"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
    variant="outlined"
  >
    <div class="text-center">
      <v-icon
        :icon="selectedFile ? 'mdi-file-check' : 'mdi-cloud-upload'"
        :color="selectedFile ? 'success' : 'primary'"
        size="64"
        class="mb-4"
      />
      
      <div v-if="selectedFile" class="mb-4">
        <div class="text-h6 text-success">{{ selectedFile.name }}</div>
        <div class="text-caption text-medium-emphasis">
          {{ formatSize(selectedFile.size) }}
        </div>
        <v-btn
          variant="text"
          color="error"
          size="small"
          @click="clearFile"
          class="mt-2"
        >
          <v-icon icon="mdi-close" class="mr-1" />
          Quitar archivo
        </v-btn>
      </div>
      
      <div v-else>
        <div class="text-body-1 mb-2">
          Arrastra tu archivo aquí o
        </div>
        <v-btn
          color="primary"
          variant="tonal"
          @click="triggerFileInput"
        >
          <v-icon icon="mdi-folder-open" class="mr-2" />
          Seleccionar archivo
        </v-btn>
        <div class="text-caption text-medium-emphasis mt-3">
          {{ acceptText }}
        </div>
      </div>
      
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        class="d-none"
        @change="handleFileChange"
      />
    </div>
    
    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mt-4"
    />
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  accept: {
    type: String,
    default: '.xlsx,.xls'
  },
  maxSize: {
    type: Number,
    default: 10 * 1024 * 1024 // 10 MB
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['file-selected', 'error'])

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)

const acceptText = computed(() => {
  const types = props.accept.split(',').join(', ')
  const maxMB = (props.maxSize / (1024 * 1024)).toFixed(0)
  return `Formatos aceptados: ${types} (máx. ${maxMB} MB)`
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = (event) => {
  const file = event.target.files?.[0]
  if (file) validateAndSetFile(file)
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) validateAndSetFile(file)
}

const validateAndSetFile = (file) => {
  // Validate extension
  const ext = '.' + file.name.split('.').pop().toLowerCase()
  const acceptedExts = props.accept.split(',')
  if (!acceptedExts.includes(ext)) {
    emit('error', `Formato no válido. Use: ${props.accept}`)
    return
  }
  
  // Validate size
  if (file.size > props.maxSize) {
    const maxMB = (props.maxSize / (1024 * 1024)).toFixed(0)
    emit('error', `El archivo excede el tamaño máximo de ${maxMB} MB`)
    return
  }
  
  selectedFile.value = file
  emit('file-selected', file)
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
  emit('file-selected', null)
}

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

defineExpose({ clearFile })
</script>

<style scoped>
.file-uploader {
  border: 2px dashed rgba(var(--v-theme-primary), 0.3);
  transition: all 0.3s ease;
  cursor: pointer;
}

.file-uploader:hover,
.file-uploader.drag-over {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.05);
}
</style>
