<template>
  <Backdrop @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-3xl mx-auto my-8 p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Previsualización</h3>
        <button class="text-gray-500 hover:text-gray-700" @click="$emit('close')">Cerrar</button>
      </div>
      <div class="prose max-w-none" v-html="html" />
    </div>
  </Backdrop>
</template>

<script setup lang="ts">
import { Backdrop } from '@/shared/components/layout'

defineProps<{ html: string }>()
defineEmits<{ (e: 'close'): void }>()
</script>


