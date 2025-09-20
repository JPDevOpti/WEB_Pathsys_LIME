<template>
  <div class="sample-info-card">
    <div class="card-header">
      <h3 class="card-title">
        <i class="fas fa-vial text-blue-500"></i>
        Información de la Muestra
      </h3>
    </div>
    
    <div class="card-content">
      <div class="info-grid">
        <div class="info-item" v-if="sample?.sample_code">
          <label>Código de Muestra:</label>
          <span>{{ sample.sample_code }}</span>
        </div>
        
        <div class="info-item" v-if="sample?.sample_type">
          <label>Tipo de Muestra:</label>
          <span>{{ sample.sample_type }}</span>
        </div>
        
        <div class="info-item" v-if="sample?.collection_date">
          <label>Fecha de Recolección:</label>
          <span>{{ formatDate(sample.collection_date) }}</span>
        </div>
        
        <div class="info-item" v-if="sample?.observations">
          <label>Observaciones:</label>
          <span>{{ sample.observations }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Sample {
  sample_code?: string
  sample_type?: string
  collection_date?: string
  observations?: string
}

interface Props {
  sample?: Sample | null
}

const props = defineProps<Props>()

const sample = computed(() => props.sample)

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('es-CO')
}
</script>

<style scoped>
.sample-info-card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-4;
}

.card-header {
  @apply mb-4 pb-3 border-b border-gray-200;
}

.card-title {
  @apply text-lg font-semibold text-gray-800 flex items-center gap-2;
}

.info-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
}

.info-item {
  @apply flex flex-col gap-1;
}

.info-item label {
  @apply text-sm font-medium text-gray-600;
}

.info-item span {
  @apply text-sm text-gray-800;
}
</style>
