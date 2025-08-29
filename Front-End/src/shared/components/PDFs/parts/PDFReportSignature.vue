<template>
  <div class="signature-block">
    <div class="signature-content">
      <div class="signature-line"></div>
      <div class="signature-info">
        <p class="signature-name">{{ signatureName }}</p>
        <p class="signature-title">{{ signatureTitle }}</p>
        <p class="signature-date">{{ signatureDate }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface CaseItem {
  caseDetails?: {
    patologo_asignado?: {
      nombre?: string
    }
    resultado?: {
      patologo_firma?: string
      fecha_firma?: string
    }
  }
}

const props = defineProps<{
  caseItem?: CaseItem
}>()

const signatureName = computed(() => {
  return props.caseItem?.caseDetails?.resultado?.patologo_firma ||
         props.caseItem?.caseDetails?.patologo_asignado?.nombre ||
         'Dr. Patólogo'
})

const signatureTitle = computed(() => {
  return 'Patólogo Anatomopatólogo'
})

const signatureDate = computed(() => {
  const fechaFirma = props.caseItem?.caseDetails?.resultado?.fecha_firma
  if (fechaFirma) {
    try {
      const date = new Date(fechaFirma)
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    } catch {
      return 'Fecha de firma'
    }
  }
  return 'Fecha de firma'
})
</script>

<style scoped>
.signature-block {
  margin: 30px 0;
  display: flex;
  justify-content: flex-end;
}

.signature-content {
  text-align: center;
  min-width: 200px;
}

.signature-line {
  width: 150px;
  height: 1px;
  background-color: #333;
  margin: 0 auto 10px auto;
}

.signature-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.signature-name {
  font-weight: bold;
  font-size: 12px;
  margin: 0;
  color: #333;
}

.signature-title {
  font-size: 10px;
  margin: 0;
  color: #666;
}

.signature-date {
  font-size: 10px;
  margin: 0;
  color: #666;
}
</style>
