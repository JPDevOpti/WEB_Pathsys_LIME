<template>
  <form class="space-y-4" @submit.prevent="onAssign">
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <FormInputField
        v-model="searchQuery"
        label="Buscar patólogo"
        placeholder="Nombre o documento"
      />

      <FormSelect
        v-model="selectedPathologist"
        :options="pathologistOptions"
        label="Patólogo"
        placeholder="Seleccione un patólogo"
        required
      />
    </div>

    <FormTextarea
      v-model="observaciones"
      label="Observaciones"
      placeholder="Notas de la asignación"
      rows="3"
    />

    <div class="flex flex-wrap items-center gap-3">
      <SaveButton label="Asignar" />
      <ActionButton color="danger" @click="onUnassign" type="button">Desasignar</ActionButton>
      <ClearButton label="Limpiar" type="button" @click="onClear" />
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/ui/forms'
import { SaveButton, ClearButton, ActionButton } from '@/shared/components/ui/buttons'

// ============================================================================
// ESTADO
// ============================================================================

const searchQuery = ref('')
const selectedPathologist = ref('')
const observaciones = ref('')

const pathologistOptions = [
  { value: 'p1', label: 'Dra. Ana Gómez (AG)' },
  { value: 'p2', label: 'Dr. Carlos Pérez (CP)' },
  { value: 'p3', label: 'Dra. Laura Ríos (LR)' },
]

// ============================================================================
// FUNCIONES
// ============================================================================

const onAssign = () => {
  // Lógica de asignación
}

const onUnassign = () => {
  // Lógica de desasignación
}

const onClear = () => {
  searchQuery.value = ''
  selectedPathologist.value = ''
  observaciones.value = ''
}
</script>