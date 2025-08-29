<template>
  <div class="patient-block">
    <h3 class="section-title">INFORMACIÓN DEL PACIENTE</h3>
    <div class="patient-info">
      <div class="info-row">
        <div class="info-item">
          <span class="label">Nombre:</span>
          <span class="value">{{ patientName }}</span>
        </div>
        <div class="info-item">
          <span class="label">Documento:</span>
          <span class="value">{{ patientDocument }}</span>
        </div>
      </div>
      <div class="info-row">
        <div class="info-item">
          <span class="label">Edad:</span>
          <span class="value">{{ patientAge }}</span>
        </div>
        <div class="info-item">
          <span class="label">Sexo:</span>
          <span class="value">{{ patientSex }}</span>
        </div>
      </div>
      <div class="info-row">
        <div class="info-item">
          <span class="label">Entidad:</span>
          <span class="value">{{ patientEntity }}</span>
        </div>
        <div class="info-item">
          <span class="label">Tipo de Atención:</span>
          <span class="value">{{ patientAttentionType }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface CaseItem {
  patient?: {
    nombre?: string
    paciente_code?: string
    edad?: number
    sexo?: string
    entidad_info?: {
      nombre?: string
    }
    tipo_atencion?: string
  }
  caseDetails?: {
    paciente?: {
      nombre?: string
      paciente_code?: string
      edad?: number
      sexo?: string
      entidad_info?: {
        nombre?: string
      }
      tipo_atencion?: string
    }
  }
  recibidoNumero?: string
}

const props = defineProps<{
  caseItem?: CaseItem
  recibidoNumero?: string
}>()

const patientName = computed(() => {
  return props.caseItem?.patient?.nombre || 
         props.caseItem?.caseDetails?.paciente?.nombre || 
         'N/A'
})

const patientDocument = computed(() => {
  return props.caseItem?.patient?.paciente_code || 
         props.caseItem?.caseDetails?.paciente?.paciente_code || 
         'N/A'
})

const patientAge = computed(() => {
  const age = props.caseItem?.patient?.edad || 
              props.caseItem?.caseDetails?.paciente?.edad
  return age ? `${age} años` : 'N/A'
})

const patientSex = computed(() => {
  return props.caseItem?.patient?.sexo || 
         props.caseItem?.caseDetails?.paciente?.sexo || 
         'N/A'
})

const patientEntity = computed(() => {
  return props.caseItem?.patient?.entidad_info?.nombre || 
         props.caseItem?.caseDetails?.paciente?.entidad_info?.nombre || 
         'N/A'
})

const patientAttentionType = computed(() => {
  return props.caseItem?.patient?.tipo_atencion || 
         props.caseItem?.caseDetails?.paciente?.tipo_atencion || 
         'N/A'
})
</script>

<style scoped>
.patient-block {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fafafa;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  margin: 0 0 15px 0;
  color: #333;
  border-bottom: 1px solid #ccc;
  padding-bottom: 5px;
}

.patient-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
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
