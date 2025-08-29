<template>
  <div class="report-footer">
    <div class="signature-section">
      <div class="signature-container">
        <div class="signature-line"></div>
        <div class="signature-content">
          <img 
            v-if="caseItem?.caseDetails?.patologo_asignado?.firma" 
            :src="caseItem.caseDetails.patologo_asignado.firma" 
            alt="Firma del Patólogo" 
            class="signature-image"
          />
          <div class="signature-text">Médico Patólogo: {{ caseItem?.caseDetails?.patologo_asignado?.nombre || '—' }}</div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
interface CaseItem {
  caseDetails?: {
    patologo_asignado?: {
      nombre?: string
      firma?: string
    }
  }
}

defineProps<{
  caseItem?: CaseItem
}>()
</script>

<style scoped>
.report-footer {
  margin-top: 2rem;
}

.signature-section {
  margin-bottom: 1rem;
}

.signature-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 300px;
  margin: 0 auto;
}

.signature-line {
  border-top: 1px solid #000;
  width: 100%;
  margin-bottom: 8px;
}

.signature-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.signature-image {
  max-width: 120px;
  max-height: 60px;
  object-fit: contain;
  background: transparent !important;
  mix-blend-mode: multiply;
}

.signature-text {
  font-size: 12px;
  text-align: center;
  font-weight: 500;
}

@media print {
  .signature-image {
    background: transparent !important;
    mix-blend-mode: multiply !important;
    -webkit-print-color-adjust: exact !important;
    color-adjust: exact !important;
  }
}
</style>
