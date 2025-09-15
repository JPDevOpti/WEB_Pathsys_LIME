<template>
  <div class="flex items-center justify-center py-8">
    <div class="flex flex-col items-center space-y-3">
      <div class="relative">
        <div 
          class="w-8 h-8 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"
          :class="sizeClass"
        ></div>
        <div 
          v-if="showPulse" 
          class="absolute inset-0 w-8 h-8 border-4 border-blue-100 rounded-full animate-ping"
          :class="sizeClass"
        ></div>
      </div>
      <p class="text-sm text-gray-500" :class="textClass">
        {{ message }}
      </p>
      <div v-if="showProgress" class="w-32 bg-gray-200 rounded-full h-1">
        <div 
          class="bg-blue-500 h-1 rounded-full transition-all duration-300 ease-out"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  message?: string
  size?: 'sm' | 'md' | 'lg'
  showPulse?: boolean
  showProgress?: boolean
  progress?: number
}

const props = withDefaults(defineProps<Props>(), {
  message: 'Cargando...',
  size: 'md',
  showPulse: false,
  showProgress: false,
  progress: 0
})

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'w-4 h-4'
    case 'lg':
      return 'w-12 h-12'
    default:
      return 'w-8 h-8'
  }
})

const textClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'text-xs'
    case 'lg':
      return 'text-base'
    default:
      return 'text-sm'
  }
})
</script>
