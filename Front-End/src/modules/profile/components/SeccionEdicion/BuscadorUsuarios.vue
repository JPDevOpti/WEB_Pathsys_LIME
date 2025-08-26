<template>
  <div class="space-y-4">
    <h4 class="text-base font-semibold text-gray-800 mb-1">{{ searchTitle }}</h4>
    <FormInput 
      v-model="localBusqueda" 
      :placeholder="searchPlaceholder" 
      :disabled="estaBuscando"
      @keyup.enter="handleSearch"
    />
    <div v-if="error" class="text-sm text-red-600">{{ error }}</div>
    
    <!-- Botones como footer -->
    <div class="flex justify-end space-x-3 pt-2 border-t border-gray-200">
      <ClearButton @click="$emit('limpiar')" :disabled="estaBuscando" />
      <SearchButton 
        @click="handleSearch" 
        :disabled="estaBuscando || !localBusqueda.trim()"
        :loading="estaBuscando"
        text="Buscar"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { FormInput } from '@/shared/components/ui/forms'
import { SearchButton, ClearButton } from '@/shared/components/ui/buttons'

const props = defineProps<{ busqueda: string; tipoBusqueda: string; estaBuscando: boolean; error: string }>()
const emit = defineEmits<{
  (e: 'buscar', payload: { query: string; tipo: string; includeInactive: boolean }): void
  (e: 'limpiar'): void
}>()

const localBusqueda = ref(props.busqueda)
const selectedTipo = ref(props.tipoBusqueda)

// Títulos y placeholders dinámicos según el tipo
const searchTitle = computed(() => {
  const titles: Record<string, string> = {
    auxiliar: 'Buscar Auxiliar Administrativo',
    patologo: 'Buscar Patólogo',
    residente: 'Buscar Residente',
    entidad: 'Buscar Entidad',
    pruebas: 'Buscar Prueba Médica'
  }
  return titles[selectedTipo.value] || 'Buscar registros'
})

const searchPlaceholder = computed(() => {
  const placeholders: Record<string, string> = {
    auxiliar: 'Nombre del auxiliar, código o email...',
    patologo: 'Nombre del patólogo, código, registro médico o email...',
    residente: 'Nombre del residente, código, registro médico o email...',
    entidad: 'Nombre de la entidad, código o NIT...',
    pruebas: 'Nombre de la prueba o código (ej: 80901-1, Biopsia)...'
  }
  return placeholders[selectedTipo.value] || 'Buscar...'
})

// Función para manejar la búsqueda - SIEMPRE incluir inactivos en edición
const handleSearch = () => {
  if (localBusqueda.value.trim() && !props.estaBuscando) {
    emit('buscar', { 
      query: localBusqueda.value.trim(), 
      tipo: selectedTipo.value,
      includeInactive: true // Siempre true para la sección de edición
    })
  }
}

// Watchers para sincronizar props
watch(() => props.busqueda, v => localBusqueda.value = v)
watch(() => props.tipoBusqueda, v => selectedTipo.value = v)
</script>


