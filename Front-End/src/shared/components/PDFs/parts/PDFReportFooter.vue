<template>
  <div class="pdf-footer">
    <div class="footer-content">
      <div class="footer-text">Los informes de resultados, las placas y bloques de estudios anatomopatológicos se archivan por 15 años</div>
      <div class="footer-separator"></div>
      <div class="footer-pagination">Página {{ currentPage || 1 }} de {{ totalPages || 1 }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  currentPage?: number
  totalPages?: number
}>()
</script>

<style scoped>
.pdf-footer {
  width: 100%;
  margin-top: auto;
  padding-top: 1rem;
}

.footer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.footer-text {
  font-size: 12px;
  text-align: center;
  color: #374151;
  line-height: 1.3;
}

.footer-separator {
  border-top: 1px solid #374151;
  width: 100%;
  margin: 0.25rem 0;
}

.footer-pagination {
  text-align: right;
  font-weight: 600;
  font-size: 12px;
  color: #111827;
  width: 100%;
}
</style>
