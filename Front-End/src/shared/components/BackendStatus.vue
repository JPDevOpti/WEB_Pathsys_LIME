<template>
  <div class="flex items-center space-x-2">
    <!-- Indicador de estado -->
    <div class="flex items-center">
      <div 
        class="w-2 h-2 rounded-full mr-2"
        :class="statusClass"
      ></div>
      <span class="text-sm font-medium" :class="textClass">
        {{ statusText }}
      </span>
    </div>
    
    <!-- Botón de reconexión -->
    <button 
      v-if="!isConnected"
      @click="$emit('reconnect')"
      class="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
    >
      Reintentar
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  isConnected: boolean
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false
})

const emit = defineEmits<{
  reconnect: []
}>()

const statusClass = computed(() => {
  if (props.isLoading) return 'bg-yellow-400 animate-pulse'
  return props.isConnected ? 'bg-green-400' : 'bg-red-400'
})

const textClass = computed(() => {
  if (props.isLoading) return 'text-yellow-700'
  return props.isConnected ? 'text-green-700' : 'text-red-700'
})

const statusText = computed(() => {
  if (props.isLoading) return 'Conectando...'
  return props.isConnected ? 'Conectado' : 'Desconectado'
})
</script>
