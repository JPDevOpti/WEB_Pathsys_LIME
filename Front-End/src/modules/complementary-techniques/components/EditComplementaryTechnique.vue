<template>
  <div class="space-y-4">
    <p class="text-gray-600">Editar técnica complementaria</p>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormInputField v-model="local.date" label="Fecha" type="date" :required="true" />
      <FormInputField v-model="local.patientDocument" label="Documento del paciente" :required="true" />
      <FormInputField v-model="local.caseNumber" label="N° Caso" :required="true" />
      <FormInputField v-model="local.patientName" label="Nombre del paciente" :required="true" />
      <FormInputField v-model="local.institution" label="Institución" :required="true" />
      <FormInputField v-model="local.elaboratedBy" label="Elaboró" />
      <FormInputField v-model="local.deliveredBy" label="Entrega" />
      <FormInputField v-model="local.receivedBy" label="Recibe" />
      <FormInputField v-model.number="local.receivedSlidesCount" label="Número de placas recibe" type="number" />
      <FormInputField v-model="local.deliveryDate" label="Fecha entrega" type="date" />
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormTextarea v-model="local.lowComplexityIHQ" label="IHQ baja complejidad" :rows="2" />
      <FormInputField v-model.number="local.lowComplexitySlidesCount" label="# Placas (baja complejidad)" type="number" />
      <FormTextarea v-model="local.highComplexityIHQ" label="IHQ alta complejidad" :rows="2" />
      <FormInputField v-model.number="local.highComplexitySlidesCount" label="# Placas (alta complejidad)" type="number" />
      <FormTextarea v-model="local.specialIHQ" label="IHQ especiales" :rows="2" />
      <FormInputField v-model.number="local.specialIHQSlidesCount" label="# Placas (especiales)" type="number" />
      <FormTextarea v-model="local.histochemical" label="Histoquímicas" :rows="2" />
      <FormInputField v-model.number="local.histochemicalSlidesCount" label="# Placas (histoquímicas)" type="number" />
      <FormSelect v-model="local.receiptStatus" label="Recibo" :options="receiptStatusOptions" />
      <FormTextarea v-model="local.notes" label="Observaciones" :rows="2" />
    </div>
    <div class="flex justify-end">
      <SaveButton text="Guardar cambios" @click="onSave" />
    </div>
  </div>
</template>

<script setup lang="ts">
// Imports
import { reactive, watch } from 'vue'
import { FormInputField, FormTextarea, FormSelect } from '@/shared/components/ui/forms'
import { SaveButton } from '@/shared/components/ui/buttons'
import type { ComplementaryTechnique } from '../types/special-cases.types'

// Props and emits for edit component
const props = defineProps<{ modelValue: ComplementaryTechnique }>()
const emit = defineEmits<{ (e: 'update:modelValue', payload: ComplementaryTechnique): void, (e: 'saved', payload: ComplementaryTechnique): void }>()

// Local copy to edit without mutating parent directly
const local = reactive<ComplementaryTechnique>({ ...props.modelValue })

watch(() => props.modelValue, (val) => {
  Object.assign(local, val)
})

// Select options
const receiptStatusOptions = [
  { value: 'FACTURAR', label: 'FACTURAR' },
  { value: 'PENDIENTE', label: 'PENDIENTE' },
  { value: 'ANULADO', label: 'ANULADO' }
]

// Save handler
const onSave = () => {
  emit('update:modelValue', { ...local })
  emit('saved', { ...local })
}
</script>


