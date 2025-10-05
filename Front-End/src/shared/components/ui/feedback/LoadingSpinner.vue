<template>
  <div class="flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600 mx-auto"></div>
      <span v-if="text" class="ml-2 text-gray-600 text-sm mt-2 block">{{ text }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  text?: string
}

const props = withDefaults(defineProps<Props>(), {
  text: 'Cargando...'
})
</script> 