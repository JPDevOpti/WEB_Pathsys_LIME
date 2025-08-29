<template>
  <div class="pdf-header">
    <div class="header-content">
      <div class="logo-section">
        <div class="logo-placeholder">
          <span class="logo-text">LOGO</span>
        </div>
      </div>
      <div class="title-section">
        <h1 class="report-title">INFORME ANATOMOPATOLÓGICO</h1>
        <p class="institution-name">INSTITUCIÓN DE SALUD</p>
      </div>
      <div class="date-section">
        <p class="report-date">{{ formatDate(new Date()) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  formatDate?: (date: Date) => string
}>()

// Función por defecto para formatear fechas
const formatDate = (date: Date): string => {
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}
</script>

<style scoped>
.pdf-header {
  width: 100%;
  margin-bottom: 20px;
  border-bottom: 2px solid #333;
  padding-bottom: 10px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  flex: 0 0 100px;
}

.logo-placeholder {
  width: 80px;
  height: 60px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 12px;
  color: #666;
  font-weight: bold;
}

.title-section {
  flex: 1;
  text-align: center;
}

.report-title {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
  color: #333;
}

.institution-name {
  font-size: 14px;
  margin: 5px 0 0 0;
  color: #666;
}

.date-section {
  flex: 0 0 100px;
  text-align: right;
}

.report-date {
  font-size: 12px;
  margin: 0;
  color: #666;
}
</style>
