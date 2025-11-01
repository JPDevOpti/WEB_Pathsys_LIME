<template>
  <Transition name="fade">
    <div
      v-if="visible"
      :class="['fixed right-0 bottom-0 top-16 z-[10000] flex items-center justify-center p-4 bg-black/45', overlayLeftClass]"
    >
      <div class="w-full max-w-2xl rounded-3xl bg-white shadow-2xl border border-amber-200 overflow-hidden">
        <div class="flex items-center gap-5 px-8 py-6 bg-amber-50 border-b border-amber-200">
          <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-100 text-amber-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1">
            <h2 class="text-2xl font-semibold text-amber-800">Falta tu firma digital</h2>
          </div>
          <button
            type="button"
            class="text-amber-500 hover:text-amber-700 transition-colors"
            @click="emit('close')"
            title="Cerrar"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="px-8 py-6 bg-white space-y-5">
          <div class="rounded-2xl border border-dashed border-gray-300 bg-gray-50/80 p-4 text-sm text-gray-800">
            Para firmar informes necesitas cargar tu firma digital. Sube un archivo de tu firma desde la sección “Mi perfil” para habilitar la firma de resultados.          </div>

          <div class="flex flex-wrap items-center justify-end gap-4">
            <RouterLink to="/profile/my-profile" class="inline-flex" @click="emit('close')">
              <BaseButton
                variant="outline"
                size="md"
                class="!bg-white !border-blue-600 !text-blue-700 hover:!bg-blue-50 hover:!text-blue-900"
              >
                Ir a mi perfil
              </BaseButton>
            </RouterLink>
            <button
              type="button"
              class="text-sm font-medium text-amber-600 hover:text-amber-700 underline"
              @click="emit('close')"
            >
              Lo haré luego
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { BaseButton } from '@/shared/components'
import { useSidebar } from '@/shared/composables/SidebarControl'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const visible = computed(() => props.visible)
let overlayLeftClass = computed(() => 'left-0 lg:left-20')
try {
  const { isExpanded, isMobileOpen, isHovered } = useSidebar()
  overlayLeftClass = computed(() => {
    const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
    return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
  })
} catch (error) {
  console.warn('[SignatureNotice] Sidebar provider not found, using default overlay positioning')
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>