<template>
  <transition name="fade-scale">
    <div 
      v-if="modelValue" 
      :class="['fixed right-0 bottom-0 z-[10000] flex items-center justify-center p-4 bg-black/40 top-16', overlayLeftClass]"
      @click.self="onCancel"
    >
      <div class="w-full max-w-md bg-white rounded-xl shadow-xl overflow-hidden">
        <!-- Header -->
        <div class="px-4 py-3 border-b border-gray-100 flex items-start gap-3">
          <div class="flex-shrink-0 mt-0.5">
            <DocsIcon class="w-5 h-5 text-blue-500" />
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
        <div class="px-4 py-4">
          <FormTextareaUnlimited
            v-model="notesText"
            :label="textareaLabel"
            :placeholder="textareaPlaceholder"
            :rows="4"
            :help-text="helpText"
          />
        </div>
        
        <!-- Footer -->
        <div class="px-4 py-3 bg-gray-50 border-t border-gray-100 flex flex-col sm:flex-row-reverse gap-2">
          <button
            type="button"
            class="inline-flex justify-center items-center gap-2 px-4 py-2 rounded-md text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
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
import { watch, onMounted, computed, ref } from 'vue'
import { useSidebar } from '@/shared/composables/SidebarControl'
import { DocsIcon } from '@/assets/icons'
import { FormTextareaUnlimited } from '@/shared/components/forms'

interface Props {
  modelValue: boolean
  title?: string
  subtitle?: string
  textareaLabel?: string
  textareaPlaceholder?: string
  helpText?: string
  confirmText?: string
  cancelText?: string
  loadingConfirm?: boolean
  closeOnEsc?: boolean
  initialValue?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Notas adicionales',
  subtitle: 'Agregar información complementaria al caso',
  textareaLabel: 'Notas',
  textareaPlaceholder: 'Escriba aquí las notas adicionales...',
  helpText: 'Esta información será agregada al caso como notas complementarias',
  confirmText: 'Guardar notas',
  cancelText: 'Cancelar',
  loadingConfirm: false,
  closeOnEsc: true,
  initialValue: ''
})

const { isExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const notesText = ref(props.initialValue)

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'confirm', notes: string): void
  (e: 'cancel'): void
}>()

function onCancel() {
  notesText.value = props.initialValue
  emit('cancel')
  emit('update:modelValue', false)
}

function onConfirm() {
  emit('confirm', notesText.value)
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
    notesText.value = props.initialValue
  }
})

watch(() => props.initialValue, (newValue) => {
  notesText.value = newValue
})
</script>

<style scoped>
.fade-scale-enter-active { transition: all 0.18s ease-out; }
.fade-scale-leave-active { transition: all 0.12s ease-in; }
.fade-scale-enter-from, .fade-scale-leave-to { opacity: 0; transform: scale(.95); }
</style>
