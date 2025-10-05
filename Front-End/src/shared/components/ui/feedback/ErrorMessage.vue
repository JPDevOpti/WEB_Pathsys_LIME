<template>
  <div class="flex items-center justify-center">
    <div class="text-center">
      <svg class="mx-auto h-10 w-10 text-error-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
      <p class="mt-2 text-sm text-gray-600">{{ message }}</p>
      <button 
        v-if="retryAction"
        @click="retryAction"
        class="mt-3 px-3 py-1.5 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors text-sm"
      >
        Reintentar
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message: string
  retryAction?: () => void
}

defineProps<Props>()
</script> 