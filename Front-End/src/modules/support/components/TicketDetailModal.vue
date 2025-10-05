<template>
  <transition 
    enter-active-class="transition ease-out duration-300" 
    enter-from-class="opacity-0 transform scale-95" 
    enter-to-class="opacity-100 transform scale-100" 
    leave-active-class="transition ease-in duration-200" 
    leave-from-class="opacity-100 transform scale-100" 
    leave-to-class="opacity-0 transform scale-95"
  >
    <div
      v-if="ticket"
      :class="[
        'fixed right-0 bottom-0 z-[9999] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/40',
        'top-16',
        overlayLeftClass
      ]"
      @click.self="$emit('close')"
    >
      <div class="relative bg-white w-full max-w-4xl rounded-t-2xl sm:rounded-2xl shadow-2xl h-[85vh] sm:h-auto sm:max-h-[90vh] overflow-y-auto overflow-x-hidden">
        <!-- Header -->
        <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900">{{ ticket.title }}</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <!-- Content -->
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Columna izquierda: información + descripción -->
            <div class="md:col-span-2 space-y-6">
              <!-- Información del ticket -->
              <div class="grid grid-cols-2 gap-4 bg-gray-50 rounded-xl p-4">
                <div>
                  <p class="text-sm text-gray-500">Código del Ticket</p>
                  <p class="text-base font-medium text-gray-900">{{ ticket.ticket_code }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Estado</p>
                  <span :class="getStatusBadgeClass(ticket.status)" class="text-xs font-medium px-2 py-1 rounded-full">
                    {{ getStatusLabel(ticket.status) }}
                  </span>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Categoría</p>
                  <p class="text-base font-medium text-gray-900">{{ getCategoryLabel(ticket.category) }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Fecha de Creación</p>
                  <p class="text-base font-medium text-gray-900">{{ formatDate(ticket.ticket_date) }}</p>
                </div>
              </div>

              <!-- Descripción -->
              <div class="bg-gray-50 rounded-xl p-4">
                <h5 class="text-sm font-medium text-gray-700 mb-3">Descripción</h5>
                <div class="bg-white border border-gray-200 rounded-lg p-3">
                  <p class="text-sm text-gray-800 whitespace-pre-wrap">{{ ticket.description }}</p>
                </div>
              </div>
            </div>

            <!-- Columna derecha: imagen -->
            <div class="space-y-4">
              <div class="bg-gray-50 rounded-xl p-4 h-full">
                <h5 class="text-sm font-medium text-gray-700 mb-3">Imagen</h5>
                <div v-if="ticket.image" class="cursor-pointer group" @click="openImageModal(getImageSrc(ticket.image))">
                  <img
                    :src="getImageSrc(ticket.image)"
                    alt="Imagen del ticket"
                    class="w-full h-56 object-cover rounded-lg border border-gray-200 group-hover:border-blue-300 transition-colors"
                  />
                  <p class="mt-2 text-xs text-gray-500">Click para ver en grande</p>
                </div>
                <div v-else class="w-full h-56 rounded-lg border border-dashed border-gray-200 flex items-center justify-center text-xs text-gray-400">
                  Sin imagen adjunta
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="sticky bottom-0 bg-white border-t border-gray-200 px-4 sm:px-6 py-3 sm:py-4 rounded-b-2xl">
          <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
            <div class="flex justify-center sm:justify-start">
              <!-- Espacio para futuras acciones -->
            </div>
            <div class="flex gap-2 justify-center sm:justify-end">
              <ActionButton variant="secondary" text="Cerrar" @action="$emit('close')" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>

  <!-- Modal para ver imagen completa -->
  <div v-if="selectedImage" :class="['fixed right-0 bottom-0 z-[10000] flex items-center justify-center p-4 bg-black/75', 'top-0', overlayLeftClass]" @click="selectedImage = null">
    <div class="max-w-4xl max-h-full flex items-center justify-center">
      <img :src="selectedImage" alt="Imagen ampliada" class="max-w-full max-h-full object-contain" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ActionButton } from '@/shared/components/ui/buttons'
import { useSidebar } from '@/shared/composables/SidebarControl'
import type { SupportTicket } from '../types/support.types'

// Props
defineProps<{
  ticket: SupportTicket | null
}>()

// Emits
defineEmits<{
  close: []
}>()

// Estado local
const selectedImage = ref<string | null>(null)

// Ajuste responsivo del sidebar
const { isExpanded, isMobileOpen, isHovered } = useSidebar()

const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

// Funciones utilitarias
const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusLabel = (status: string) => {
  const labels = {
    'open': 'Abierto',
    'in-progress': 'En Progreso',
    'resolved': 'Resuelto',
    'closed': 'Cerrado'
  }
  return labels[status as keyof typeof labels] || status
}

const getStatusBadgeClass = (status: string) => {
  const classes = {
    'open': 'bg-red-100 text-red-800',
    'in-progress': 'bg-yellow-100 text-yellow-800',
    'resolved': 'bg-green-100 text-green-800',
    'closed': 'bg-gray-100 text-gray-800'
  }
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}

const getCategoryLabel = (category: string) => {
  const labels = {
    'bug': 'Error / Bug',
    'feature': 'Nueva característica',
    'question': 'Pregunta',
    'technical': 'Problema técnico'
  }
  return labels[category as keyof typeof labels] || category
}

const openImageModal = (imageUrl?: string) => {
  if (imageUrl) {
    selectedImage.value = imageUrl
  }
}

const getImageSrc = (src?: string) => {
  if (!src) return ''
  // Si es data URL o URL absoluta, retornar tal cual
  if (src.startsWith('data:') || src.startsWith('http')) return src
  // Para rutas relativas del backend, anteponer base si es necesario
  try {
    const base = import.meta.env?.VITE_API_BASE_URL || ''
    return base ? `${base}${src}` : src
  } catch {
    return src
  }
}


</script>
