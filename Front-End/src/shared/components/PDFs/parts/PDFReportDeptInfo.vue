<template>
  <div class="dept-info">
    <div class="info-grid">
      <div class="info-item">
        <span class="label">Código del Caso:</span>
        <span class="value">{{ caseItem?.caseDetails?.caso_code || caseItem?.sampleId || 'N/A' }}</span>
      </div>
      <div class="info-item">
        <span class="label">Fecha de Recepción:</span>
        <span class="value">{{ formatDate(caseItem?.caseDetails?.fecha_ingreso) || 'N/A' }}</span>
      </div>
      <div class="info-item">
        <span class="label">Número de Recibido:</span>
        <span class="value">{{ recibidoNumero || 'N/A' }}</span>
      </div>
      <div class="info-item">
        <span class="label">Servicio:</span>
        <span class="value">{{ caseItem?.caseDetails?.servicio || 'N/A' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface CaseItem {
  caseDetails?: {
    caso_code?: string
    fecha_ingreso?: string
    servicio?: string
  }
  sampleId?: string
}

defineProps<{
  caseItem?: CaseItem
  formatDate?: (date: string) => string
  recibidoNumero?: string
}>()

// Función por defecto para formatear fechas
const formatDate = (dateString?: string): string => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch {
    return 'N/A'
  }
}
</script>

<style scoped>
.dept-info {
  margin: 15px 0;
  padding: 10px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-weight: bold;
  color: #333;
  font-size: 12px;
}

.value {
  color: #666;
  font-size: 12px;
  text-align: right;
}
</style>
