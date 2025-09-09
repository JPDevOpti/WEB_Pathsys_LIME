<template>
  <div class="fixed bottom-4 right-4 z-[10000] flex flex-col gap-3 w-full max-w-sm">
    <TransitionGroup name="toast-slide">
      <div v-for="t in toasts" :key="t.id" :class="['rounded-lg shadow-lg border-l-4 p-4 bg-white', borderClassByAction(t)]">
        <div class="flex items-start gap-3">
          <div :class="iconBgClassByAction(t)">
            <component :is="iconByAction(t)" class="w-5 h-5" />
          </div>
          <div class="flex-1 min-w-0">
            <h4 :class="titleClassByAction(t)">{{ titleByAction(t) }}</h4>
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
import { SuccessIcon, ErrorIcon, WarningIcon, InfoIcon, TrashIconLg, RefreshIcon, CheckIcon } from '@/assets/icons'

const { toasts, remove } = useToasts()

function iconByAction(t: any) {
  if (t.action === 'delete') return ErrorIcon
  if (t.action === 'update') return RefreshIcon
  if (t.action === 'create') return CheckIcon
  return t.type === 'success' ? SuccessIcon : t.type === 'error' ? ErrorIcon : t.type === 'warning' ? WarningIcon : InfoIcon
}
function iconBgClassByAction(t: any) {
  if (t.action === 'delete') return 'bg-red-100 text-red-600 rounded-full p-2'
  if (t.action === 'update') return 'bg-blue-100 text-blue-600 rounded-full p-2'
  if (t.action === 'create') return 'bg-green-100 text-green-600 rounded-full p-2'
  return t.type === 'success' ? 'bg-green-100 text-green-600 rounded-full p-2' : t.type === 'error' ? 'bg-red-100 text-red-600 rounded-full p-2' : t.type === 'warning' ? 'bg-amber-100 text-amber-600 rounded-full p-2' : 'bg-blue-100 text-blue-600 rounded-full p-2'
}
function titleClassByAction(t: any) {
  if (t.action === 'delete') return 'text-red-800 font-semibold'
  if (t.action === 'update') return 'text-blue-800 font-semibold'
  if (t.action === 'create') return 'text-green-800 font-semibold'
  return t.type === 'success' ? 'text-green-800 font-semibold' : t.type === 'error' ? 'text-red-800 font-semibold' : t.type === 'warning' ? 'text-amber-800 font-semibold' : 'text-blue-800 font-semibold'
}
function titleByAction(t: any) {
  if (t.action === 'create') return 'Creado exitosamente'
  if (t.action === 'update') return 'Actualizado correctamente'
  if (t.action === 'delete') return 'Eliminado correctamente'
  return t.title || 'Notificación'
}
function borderClassByAction(t: any) {
  if (t.action === 'delete') return 'border-red-500'
  if (t.action === 'update') return 'border-blue-500'
  if (t.action === 'create') return 'border-green-500'
  return t.type === 'success' ? 'border-green-500' : t.type === 'error' ? 'border-red-500' : t.type === 'warning' ? 'border-amber-500' : 'border-blue-500'
}
</script>

<style scoped>
.toast-slide-enter-active, .toast-slide-leave-active { transition: all .25s ease; }
.toast-slide-enter-from { opacity: 0; transform: translateX(16px); }
.toast-slide-leave-to { opacity: 0; transform: translateX(16px); }
</style>


