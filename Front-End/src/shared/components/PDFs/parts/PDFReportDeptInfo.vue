<template>
  <div class="patient-info text-xs space-y-0.5 mb-4">
    <div><strong>Documento de identidad:</strong> {{ caseItem?.patient?.document || caseItem?.caseDetails?.paciente?.cedula || '—' }}</div>
    <div><strong>Paciente:</strong> {{ caseItem?.patient?.fullName || caseItem?.caseDetails?.paciente?.nombre || '—' }}</div>
    <div>
      <strong>Edad:</strong> {{ caseItem?.caseDetails?.paciente?.edad ?? '—' }}
      <span class="ml-4"><strong>Sexo:</strong> {{ caseItem?.caseDetails?.paciente?.sexo || '—' }}</span>
    </div>
    <div>
      <strong>Institución:</strong> {{ caseItem?.caseDetails?.entidad_info?.nombre || caseItem?.patient?.entity || '—' }}
      <span class="ml-4"><strong>Servicio:</strong> {{ caseItem?.caseDetails?.servicio || '—' }}</span>
      <span class="ml-4"><strong>Recibido N°:</strong> {{ recibidoNumero || '—' }}</span>
    </div>
    <div><strong>Médico Solicitante:</strong> {{ caseItem?.caseDetails?.medico_solicitante?.nombre || '—' }}</div>
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
.patient-info { margin-bottom: 1rem; }
.patient-info > div { margin-bottom: 0.125rem; }
.patient-info strong { font-weight: 600; }
</style>
