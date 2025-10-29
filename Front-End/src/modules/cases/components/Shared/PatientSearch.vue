<template>
  <div class="bg-gray-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-gray-200">
    <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
      <SearchPatientIcon class="w-4 h-4 mr-2 text-gray-500" />
      Buscar paciente
    </h3>

    <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
      <div class="sm:w-64">
        <FormSelect
          :model-value="identificationType"
          placeholder="Tipo de identificación"
          :required="true"
          :options="identificationTypeOptions"
          @update:model-value="onUpdateIdentificationType"
        />
      </div>

      <div class="flex-1">
        <FormInputField
          :model-value="identificationNumber"
          placeholder="Número de identificación"
          :required="true"
          :max-length="20"
          inputmode="numeric"
          :only-numbers="true"
          @input="onUpdateIdentificationNumber"
        />
      </div>

      <div class="flex gap-2 sm:gap-3">
        <SearchButton 
          v-if="!patientVerified" 
          text="Buscar" 
          loading-text="Buscando..." 
          @click="$emit('search')" 
          size="md" 
        />
        <ClearButton 
          v-if="patientVerified" 
          text="Limpiar" 
          @click="$emit('clear')" 
        />
      </div>
    </div>

    <div v-if="errorMessage" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
      <p class="text-sm text-red-600">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineEmits } from 'vue'
import { FormInputField, FormSelect } from '@/shared/components/ui/forms'
import { SearchButton, ClearButton } from '@/shared/components/ui/buttons'
import { SearchPatientIcon } from '@/assets/icons'

defineProps({
  identificationType: { type: [String, Number], default: '' },
  identificationNumber: { type: String, default: '' },
  errorMessage: { type: String, default: '' },
  patientVerified: { type: Boolean, default: false },
  identificationTypeOptions: {
    type: Array as () => { value: string | number; label: string }[],
    default: () => [
      { value: 1, label: 'Cédula de Ciudadanía' },
      { value: 2, label: 'Cédula de Extranjería' },
      { value: 3, label: 'Tarjeta de Identidad' },
      { value: 4, label: 'Pasaporte' },
      { value: 5, label: 'Registro Civil' },
      { value: 6, label: 'Documento Extranjero' },
      { value: 7, label: 'NIT' },
      { value: 8, label: 'Carnet Diplomático' },
      { value: 9, label: 'Salvoconducto' }
    ]
  }
})

const emit = defineEmits<{
  (e: 'update:identificationType', v: string | number): void
  (e: 'update:identificationNumber', v: string): void
  (e: 'search'): void
  (e: 'clear'): void
}>()

const onUpdateIdentificationType = (v: string | number) => emit('update:identificationType', v)
const onUpdateIdentificationNumber = (v: string) => emit('update:identificationNumber', v)
</script>