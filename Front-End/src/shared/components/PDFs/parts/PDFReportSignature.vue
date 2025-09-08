<template>
  <div class="report-footer">
    <div class="signature-section">
      <div class="signature-container">
        <div class="signature-content">
          <!-- Espacio para la firma (ARRIBA). Si no hay firma, queda vacío sin marcador. -->
          <div class="signature-space">
            <template v-if="caseItem?.caseDetails?.patologo_asignado?.firma">
              <img :src="caseItem.caseDetails.patologo_asignado.firma" alt="firma" class="signature-image" />
            </template>
            <template v-else>
              <span class="no-signature-text">SIN FIRMA</span>
            </template>
          </div>
          <!-- Línea de firma -->
          <div class="signature-line"></div>
          <!-- Nombre del patólogo (ABAJO de la línea) -->
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

// Logs de depuración eliminados
</script>

<style scoped>
.report-footer {
  margin-top: 0rem;
  height: 160px;
  padding-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.signature-section {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.signature-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 400px;
  height: 130px;
}

.signature-line {
  border-top: 2px solid #000;
  width: 100%;
  margin: 2px 0;
}

.signature-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  height: 100%;
  justify-content: space-between;
}

.signature-space {
  width: 350px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.signature-image {
  max-width: 350px;
  max-height: 100px;
  width: 350px;
  height: 100px;
  object-fit: contain;
  background: transparent !important;
  mix-blend-mode: multiply;
}

.no-signature-text {
  font-size: 10px;
  letter-spacing: 1px;
  color: #888;
  font-style: italic;
}

/* Sin placeholder visual cuando no hay firma */

.signature-text {
  font-size: 12px;
  text-align: center;
  font-weight: 500;
  flex-shrink: 0;
  margin-top: 0;
}

@media print {
  .signature-image {
    background: transparent !important;
    mix-blend-mode: multiply !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}
</style>
