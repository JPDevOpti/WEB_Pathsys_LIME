<template>
  <div class="space-y-4">
    <p class="text-gray-600">Editor de técnica complementaria (migrado a Special Cases).</p>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormInputField label="Código" placeholder="C2025-00001" />
      <FormInputField label="Nombre de la técnica" placeholder="Ej: Inmunohistoquímica CD20" />
    </div>
    <FormTextarea label="Descripción" rows="3" />
    <div class="flex justify-end">
      <SaveButton text="Guardar cambios" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { FormInputField, FormTextarea } from '@/shared/components/forms'
import { SaveButton } from '@/shared/components/buttons'
</script>


