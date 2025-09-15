<template>
  <div class="space-y-4">
    <!-- Header con título y botón de agregar -->
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-medium text-gray-700">Submuestras</h3>
      <AddButton @click="addSubSample">Agregar Submuestra</AddButton>
    </div>

    <!-- Mensaje cuando no hay submuestras -->
    <div v-if="subSamples.length === 0" class="text-gray-500 text-sm">No hay submuestras registradas.</div>

    <!-- Lista de submuestras -->
    <div v-for="(sub, index) in subSamples" :key="index" class="p-4 border rounded-md space-y-3">
      <!-- Header de la submuestra con botón de eliminar -->
      <div class="flex items-center justify-between">
        <h4 class="font-medium">Submuestra #{{ sub.numero }}</h4>
        <RemoveButton color="danger" @click="removeSubSample(index)">Quitar</RemoveButton>
      </div>

      <!-- Campos de región del cuerpo y cantidad de pruebas -->
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <FormInputField v-model="sub.regionCuerpo" label="Región del cuerpo" placeholder="Ej. Mama izquierda" />
        <FormInputField v-model.number="sub.cantidadPruebas" type="number" min="0" label="Cantidad de pruebas" placeholder="0" />
      </div>

      <!-- Sección de pruebas de la submuestra -->
      <div class="space-y-2">
        <label class="text-sm font-medium text-gray-700">Pruebas</label>
        <div class="flex flex-wrap gap-2">
          <FormInputField v-for="(t, ti) in sub.pruebas" :key="ti" v-model="t.nombre" placeholder="Nombre de prueba" class="w-full md:w-64" />
          <AddButton @click="addTest(index)">Agregar Prueba</AddButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { FormInputField } from '@/shared/components/forms'
import { AddButton, RemoveButton } from '@/shared/components/buttons'

// Interfaces para tipado de datos
interface TestItem { nombre: string }
interface SubSampleItem { numero: number; regionCuerpo: string; cantidadPruebas: number; pruebas: TestItem[] }

// Estado reactivo para las submuestras
const subSamples = reactive<SubSampleItem[]>([])

// Agregar nueva submuestra
const addSubSample = () => {
  subSamples.push({ numero: subSamples.length + 1, regionCuerpo: '', cantidadPruebas: 0, pruebas: [] })
}

// Eliminar submuestra y reindexar
const removeSubSample = (idx: number) => {
  subSamples.splice(idx, 1)
  subSamples.forEach((s, i) => { s.numero = i + 1 })
}

// Agregar nueva prueba a una submuestra específica
const addTest = (subIndex: number) => {
  subSamples[subIndex].pruebas.push({ nombre: '' })
}
</script>