<template>
  <div class="pdf-footer">
    <div class="footer-content">
      <div class="footer-info">
        <p class="footer-text">Este informe ha sido generado electrónicamente por el sistema PathSys</p>
        <p class="footer-text">Fecha de generación: {{ generationDate }}</p>
      </div>
      <div class="footer-page">
        <p class="page-info">Página {{ currentPage }} de {{ totalPages }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  currentPage?: number
  totalPages?: number
  generationDate?: string
}>()

const generationDate = computed(() => {
  return props.generationDate || new Date().toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})
</script>

<style scoped>
.pdf-footer {
  margin-top: 30px;
  padding-top: 10px;
  border-top: 1px solid #ddd;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
  color: #666;
}

.footer-info {
  flex: 1;
}

.footer-text {
  margin: 2px 0;
  font-size: 10px;
}

.footer-page {
  text-align: right;
}

.page-info {
  margin: 0;
  font-size: 10px;
}
</style>
