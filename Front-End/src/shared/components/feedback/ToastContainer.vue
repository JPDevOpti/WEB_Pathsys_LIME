<template>
  <div class="fixed bottom-4 right-4 z-[10000] flex flex-col gap-3 w-full max-w-sm">
    <TransitionGroup name="toast-slide">
      <div v-for="t in toasts" :key="t.id" :class="['rounded-lg shadow-lg border-l-4 p-4 bg-white']">
        <div class="flex items-start gap-3">
          <div :class="iconBgClass(t)">
            <component :is="iconByType(t)" class="w-5 h-5" />
          </div>
          <div class="flex-1 min-w-0">
            <h4 :class="titleClass(t)">{{ titleByAction(t) }}</h4>
            <p class="text-sm text-gray-600 break-words">{{ t.message }}</p>
          </div>
          <button class="text-gray-400 hover:text-gray-600" @click="remove(t.id)">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToasts } from '@/shared/composables/useToasts'
import { SuccessIcon, ErrorIcon, WarningIcon, InfoIcon } from '@/assets/icons'

const { toasts, remove } = useToasts()

function iconByType(t: any) {
  return t.type === 'success' ? SuccessIcon : t.type === 'error' ? ErrorIcon : t.type === 'warning' ? WarningIcon : InfoIcon
}
function iconBgClass(t: any) {
  return t.type === 'success' ? 'bg-green-100 text-green-600 rounded-full p-2' : t.type === 'error' ? 'bg-red-100 text-red-600 rounded-full p-2' : t.type === 'warning' ? 'bg-amber-100 text-amber-600 rounded-full p-2' : 'bg-blue-100 text-blue-600 rounded-full p-2'
}
function titleClass(t: any) {
  return t.type === 'success' ? 'text-green-800 font-semibold' : t.type === 'error' ? 'text-red-800 font-semibold' : t.type === 'warning' ? 'text-amber-800 font-semibold' : 'text-blue-800 font-semibold'
}
function titleByAction(t: any) {
  if (t.action === 'create') return 'Creado exitosamente'
  if (t.action === 'update') return 'Actualizado correctamente'
  if (t.action === 'delete') return 'Eliminado correctamente'
  return t.title || 'Notificación'
}
</script>

<style scoped>
.toast-slide-enter-active, .toast-slide-leave-active { transition: all .25s ease; }
.toast-slide-enter-from { opacity: 0; transform: translateX(16px); }
.toast-slide-leave-to { opacity: 0; transform: translateX(16px); }
</style>


