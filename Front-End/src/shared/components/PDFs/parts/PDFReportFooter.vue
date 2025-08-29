<template>
  <div class="pdf-footer">
    <div class="footer-text">Los informes de resultados, las placas y bloques de estudios anatomopatológicos se archivan por 15 años</div>
    <div class="footer-line"></div>
    <div class="footer-page">Página {{ currentPage || 1 }} de {{ totalPages || 1 }}</div>
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
  margin-top: 20px;
  text-align: center;
}

.footer-text {
  font-size: 12px;
  margin-bottom: 8px;
  text-align: center;
}

.footer-line {
  border-top: 1px solid #000;
  margin: 8px 0;
}

.footer-page {
  text-align: right;
  font-weight: 700;
  font-size: 12px;
  margin-top: 4px;
}
</style>
