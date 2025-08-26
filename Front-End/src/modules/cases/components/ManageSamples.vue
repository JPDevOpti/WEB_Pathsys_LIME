<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-medium text-gray-700">Submuestras</h3>
      <AddButton @click="addSubSample">Agregar Submuestra</AddButton>
    </div>

    <div v-if="subSamples.length === 0" class="text-gray-500 text-sm">
      No hay submuestras registradas.
    </div>

    <div v-for="(sub, index) in subSamples" :key="index" class="p-4 border rounded-md space-y-3">
      <div class="flex items-center justify-between">
        <h4 class="font-medium">Submuestra #{{ sub.numero }}</h4>
        <RemoveButton color="danger" @click="removeSubSample(index)">Quitar</RemoveButton>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <FormInputField
          v-model="sub.regionCuerpo"
          label="Región del cuerpo"
          placeholder="Ej. Mama izquierda"
        />
        <FormInputField
          v-model.number="sub.cantidadPruebas"
          type="number"
          min="0"
          label="Cantidad de pruebas"
          placeholder="0"
        />
      </div>

      <div class="space-y-2">
        <label class="text-sm font-medium text-gray-700">Pruebas</label>
        <div class="flex flex-wrap gap-2">
          <FormInputField
            v-for="(t, ti) in sub.pruebas"
            :key="ti"
            v-model="t.nombre"
            placeholder="Nombre de prueba"
            class="w-full md:w-64"
          />
          <AddButton @click="addTest(index)">Agregar Prueba</AddButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { FormInputField } from '@/shared/components/ui/forms'
import { AddButton, RemoveButton } from '@/shared/components/ui/buttons'

// ============================================================================
// ESTADO
// ============================================================================

interface TestItem { nombre: string }
interface SubSampleItem { numero: number; regionCuerpo: string; cantidadPruebas: number; pruebas: TestItem[] }

const subSamples = reactive<SubSampleItem[]>([])

// ============================================================================
// FUNCIONES
// ============================================================================

const addSubSample = () => {
  subSamples.push({ numero: subSamples.length + 1, regionCuerpo: '', cantidadPruebas: 0, pruebas: [] })
}

const removeSubSample = (idx: number) => {
  subSamples.splice(idx, 1)
  // Reindexar números
  subSamples.forEach((s, i) => { s.numero = i + 1 })
}

const addTest = (subIndex: number) => {
  subSamples[subIndex].pruebas.push({ nombre: '' })
}
</script>