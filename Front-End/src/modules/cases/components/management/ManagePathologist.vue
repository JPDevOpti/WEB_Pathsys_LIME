<template>
  <div class="space-y-6">
    <!-- Título con icono -->
    <div class="flex items-center">
      <DocsIcon class="w-5 h-5 mr-2 text-blue-600" />
      <h2 class="text-lg font-semibold text-gray-800">Gestión de Patólogo</h2>
    </div>

    <form class="space-y-4" @submit.prevent="onAssign">
    <!-- Campos de búsqueda y selección de patólogo -->
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <FormInputField v-model="searchQuery" label="Buscar patólogo" placeholder="Nombre o documento" />
      <FormSelect v-model="selectedPathologist" :options="pathologistOptions" label="Patólogo" placeholder="Seleccione un patólogo" required />
    </div>

    <!-- Campo de observaciones para la asignación -->
    <FormTextarea v-model="observaciones" label="Observaciones" placeholder="Notas de la asignación" :rows="3" />

    <!-- Botones de acción del formulario -->
    <div class="flex flex-wrap items-center gap-3">
      <SaveButton label="Asignar" />
      <ActionButton color="danger" @click="onUnassign" type="button">Desasignar</ActionButton>
      <ClearButton label="Limpiar" type="button" @click="onClear" />
    </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton, ActionButton } from '@/shared/components/buttons'
import { DocsIcon } from '@/assets/icons'

// Estado del formulario
const searchQuery = ref('')
const selectedPathologist = ref('')
const observaciones = ref('')

// Opciones de patólogos disponibles
const pathologistOptions = [
  { value: 'p1', label: 'Dra. Ana Gómez (AG)' },
  { value: 'p2', label: 'Dr. Carlos Pérez (CP)' },
  { value: 'p3', label: 'Dra. Laura Ríos (LR)' }
]

// Asignar patólogo al caso
const onAssign = () => {
  // Lógica de asignación
}

// Desasignar patólogo del caso
const onUnassign = () => {
  // Lógica de desasignación
}

// Limpiar formulario
const onClear = () => {
  searchQuery.value = ''
  selectedPathologist.value = ''
  observaciones.value = ''
}
</script>