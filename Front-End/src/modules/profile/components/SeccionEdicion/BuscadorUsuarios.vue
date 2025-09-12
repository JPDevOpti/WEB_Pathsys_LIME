<template>
  <div class="space-y-4">
    <h4 class="text-base font-semibold text-gray-800 mb-1" :id="titleId">{{ searchTitle }}</h4>
    <FormInput
      v-model="localBusqueda"
      :id="inputId"
      :aria-labelledby="titleId"
      :aria-describedby="error ? errorId : undefined"
      :placeholder="searchPlaceholder"
      :disabled="estaBuscando"
      @keyup.enter="handleSearch"
    />
    <div v-if="error" :id="errorId" role="alert" class="text-sm text-red-600">{{ error }}</div>
    
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
import { FormInput } from '@/shared/components/forms'
import { SearchButton, ClearButton } from '@/shared/components/buttons'

// Tipos estrictos para evitar valores arbitrarios y errores de conexión con el backend
type TipoBusqueda = 'auxiliar' | 'facturacion' | 'patologo' | 'residente' | 'entidad' | 'pruebas'

interface BuscarEventPayload {
  query: string
  tipo: TipoBusqueda
  includeInactive: boolean
}

const props = defineProps<{ busqueda: string; tipoBusqueda: TipoBusqueda; estaBuscando: boolean; error: string }>()
const emit = defineEmits<{
  (e: 'buscar', payload: BuscarEventPayload): void
  (e: 'limpiar'): void
}>()

const localBusqueda = ref(props.busqueda)
// IDs únicos (en componentes repetidos en la página evitar colisiones)
const uid = Math.random().toString(36).slice(2, 9)
const inputId = `buscador-${uid}`
const titleId = `buscador-title-${uid}`
const errorId = `buscador-error-${uid}`

// Metadatos centralizados por tipo para evitar desalineaciones
const SEARCH_META: Record<TipoBusqueda, { title: string; placeholder: string }> = {
  auxiliar: {
    title: 'Buscar Auxiliar Administrativo',
    placeholder: 'Nombre del auxiliar, código o email...'
  },
  patologo: {
    title: 'Buscar Patólogo',
    placeholder: 'Nombre del patólogo, código, registro médico o email...'
  },
  residente: {
    title: 'Buscar Residente',
    placeholder: 'Nombre del residente, código, registro médico o email...'
  },
  entidad: {
    title: 'Buscar Entidad',
    placeholder: 'Nombre de la entidad, código o NIT...'
  },
  pruebas: {
    title: 'Buscar Prueba Médica',
    placeholder: 'Nombre de la prueba o código (80901-1, Biopsia)...'
  }
}

const tipoActual = computed(() => props.tipoBusqueda)

// Título y placeholder derivados
const searchTitle = computed(() => SEARCH_META[tipoActual.value]?.title || 'Buscar registros')
const searchPlaceholder = computed(() => SEARCH_META[tipoActual.value]?.placeholder || 'Buscar...')

// Evitar emitir búsquedas duplicadas con la misma query y tipo consecutivos
const lastPayload = ref<{ query: string; tipo: TipoBusqueda } | null>(null)

// Función para manejar la búsqueda - SIEMPRE incluir inactivos en edición
const handleSearch = () => {
  const query = localBusqueda.value.trim()
  if (!query || props.estaBuscando) return

  const payload: BuscarEventPayload = {
    query,
    tipo: tipoActual.value,
    includeInactive: true // Requisito de sección edición
  }

  if (lastPayload.value && lastPayload.value.query === payload.query && lastPayload.value.tipo === payload.tipo) {
    return // Evitar llamada redundante que generaría petición HTTP innecesaria
  }
  lastPayload.value = { query: payload.query, tipo: payload.tipo }
  emit('buscar', payload)
}

// Sincronizar cambios externos de la búsqueda (prop -> estado local editable)
watch(() => props.busqueda, v => { if (v !== localBusqueda.value) localBusqueda.value = v })
</script>


