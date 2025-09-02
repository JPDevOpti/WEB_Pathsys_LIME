<template>
  <transition name="fade-scale">
    <div v-if="modelValue" class="fixed inset-0 z-[10000] flex items-end sm:items-center justify-center p-4 bg-black/40" @click.self="onCancel">
      <div class="w-full max-w-sm bg-white rounded-xl shadow-xl overflow-hidden">
        <!-- Header -->
        <div class="px-4 py-3 border-b border-gray-100 flex items-start gap-3">
          <div v-if="icon" class="flex-shrink-0 mt-0.5">
            <component :is="icon" class="w-5 h-5 text-red-500" />
          </div>
          <div class="flex-1">
            <h3 class="text-sm font-semibold text-gray-900">{{ title }}</h3>
            <p v-if="subtitle" class="text-xs text-gray-500 mt-0.5">{{ subtitle }}</p>
          </div>
          <button @click="onCancel" class="text-gray-400 hover:text-gray-600" aria-label="Cerrar">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <!-- Body -->
        <div class="px-4 py-4 text-sm text-gray-600 whitespace-pre-line">
          <slot>
            {{ message }}
          </slot>
        </div>
        <!-- Footer -->
        <div class="px-4 py-3 bg-gray-50 border-t border-gray-100 flex flex-col sm:flex-row-reverse gap-2">
          <button
            type="button"
            class="inline-flex justify-center items-center gap-2 px-4 py-2 rounded-md text-sm font-medium bg-red-600 text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
            @click="onConfirm"
            :disabled="loadingConfirm"
          >
            <svg v-if="loadingConfirm" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 100 8v4a8 8 0 01-8-8z" /></svg>
            {{ confirmText }}
          </button>
          <button
            type="button"
            class="inline-flex justify-center items-center px-4 py-2 rounded-md text-sm font-medium border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            @click="onCancel"
          >
            {{ cancelText }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { watch, onMounted } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  subtitle?: string
  message?: string
  confirmText?: string
  cancelText?: string
  loadingConfirm?: boolean
  icon?: any
  closeOnEsc?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confirmar acción',
  subtitle: '',
  message: '¿Estás seguro que deseas continuar?',
  confirmText: 'Confirmar',
  cancelText: 'Cancelar',
  loadingConfirm: false,
  closeOnEsc: true
})

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

function onCancel() {
  emit('cancel')
  emit('update:modelValue', false)
}

function onConfirm() {
  emit('confirm')
}

function onKey(e: KeyboardEvent) {
  if (!props.modelValue) return
  if (e.key === 'Escape' && props.closeOnEsc) {
    onCancel()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
})

watch(() => props.modelValue, (val) => {
  if (val) {
    // Focus management or scroll lock could be added here
  }
})
</script>

<style scoped>
.fade-scale-enter-active { transition: all 0.18s ease-out; }
.fade-scale-leave-active { transition: all 0.12s ease-in; }
.fade-scale-enter-from, .fade-scale-leave-to { opacity: 0; transform: scale(.95); }
</style>
