<template>
  <div class="space-y-1">
    <label class="block text-sm font-medium text-gray-700">Tipo de usuario</label>
    <FormSelect
      :model-value="tipoSeleccionado"
      :options="options"
      placeholder="Selecciona un tipo"
      @update:modelValue="$emit('tipo-seleccionado', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import { FormSelect } from '@/shared/components/forms'

defineProps<{ tipoSeleccionado: string }>()

const options = [
  { value: 'auxiliar', label: 'Auxiliar administrativo' },
  { value: 'patologo', label: 'Patólogo' },
  { value: 'entidad', label: 'Entidad' },
  { value: 'pruebas', label: 'Pruebas' }
]
</script>


