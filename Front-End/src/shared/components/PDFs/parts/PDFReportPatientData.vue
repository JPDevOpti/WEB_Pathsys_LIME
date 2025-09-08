<template>
  <div class="patient-data">
    <div class="patient-info-grid">
      <div class="patient-row">
        <span class="label">Documento de identidad:</span>
        <span class="value">{{ caseItem?.patient?.document || caseItem?.caseDetails?.paciente?.cedula || '—' }}</span>
      </div>
      <div class="patient-row">
        <span class="label">Paciente:</span>
        <span class="value">{{ caseItem?.patient?.fullName || caseItem?.caseDetails?.paciente?.nombre || '—' }}</span>
      </div>
      <div class="patient-row">
        <span class="label">Edad:</span>
        <span class="value">{{ caseItem?.caseDetails?.paciente?.edad ?? '—' }}</span>
        <span class="label ml-8">Sexo:</span>
        <span class="value">{{ caseItem?.caseDetails?.paciente?.sexo || '—' }}</span>
      </div>
      <div class="patient-row">
        <span class="label">Institución:</span>
        <span class="value">{{ caseItem?.caseDetails?.entidad_info?.nombre || caseItem?.patient?.entity || '—' }}</span>
      </div>
      <div class="patient-row">
        <span class="label">Servicio:</span>
        <span class="value">{{ caseItem?.caseDetails?.servicio || '—' }}</span>
        <span class="label ml-8">Recibido N°:</span>
        <span class="value">{{ recibidoNumero || '—' }}</span>
      </div>
      <div class="patient-row">
        <span class="label">Médico Solicitante:</span>
        <span class="value">{{ caseItem?.caseDetails?.medico_solicitante?.nombre || '—' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface CaseItem {
  patient?: {
    document?: string
    fullName?: string
    entity?: string
  }
  caseDetails?: {
    paciente?: {
      cedula?: string
      nombre?: string
      edad?: number
      sexo?: string
    }
    entidad_info?: { nombre?: string }
    servicio?: string
    medico_solicitante?: { nombre?: string }
  }
}

defineProps<{
  caseItem?: CaseItem
  recibidoNumero?: string
}>()
</script>

<style scoped>
.patient-data {
  margin-bottom: 1rem;
  font-size: 12px;
  line-height: 1.4;
}

.patient-info-grid {
  display: grid;
  grid-template-rows: repeat(6, auto);
  grid-row-gap: 0.15rem;
}

.patient-row {
  display: flex;
  align-items: baseline;
  min-height: 1.2rem;
}

.label {
  font-weight: 600;
  color: #374151;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.value {
  color: #111827;
  flex-grow: 1;
}

.ml-8 {
  margin-left: 2rem;
}
</style>
