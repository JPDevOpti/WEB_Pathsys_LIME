<template>
  <div class="bg-white shadow rounded-lg">
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <TaskIcon class="w-5 h-5 mr-2 text-blue-600" />
          <h2 class="text-lg font-semibold text-gray-900">Tickets Actuales</h2>
        </div>
        
        <!-- Filtros -->
        <div class="flex items-center space-x-3">
          <div class="w-40">
            <FormSelect
              v-model="filters.status"
              :options="statusOptions"
              placeholder="Estado"
            />
          </div>
          
          <div class="w-44">
            <FormSelect
              v-model="filters.category"
              :options="categoryOptions"
              placeholder="Categoría"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="p-6">
      <!-- Estado sin tickets -->
      <div v-if="filteredTickets.length === 0" class="text-center py-8">
        <div class="flex flex-col items-center space-y-2">
          <TaskIcon class="w-12 h-12 text-gray-300" />
          <div class="text-center">
            <p class="text-gray-500 text-sm font-medium">
              {{ tickets.length === 0 ? 'No hay tickets en el sistema' : 'No se encontraron tickets con los filtros seleccionados' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Lista de tickets -->
      <div v-else class="space-y-4">
        <div
          v-for="ticket in filteredTickets"
          :key="ticket.id"
          class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
          @click="selectTicket(ticket)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <h3 class="font-medium text-gray-900">{{ ticket.title }}</h3>
                <span :class="getStatusBadgeClass(ticket.status)" class="text-xs font-medium px-2 py-1 rounded-full">
                  {{ getStatusLabel(ticket.status) }}
                </span>
                <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {{ getCategoryLabel(ticket.category) }}
                </span>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ ticket.description.substring(0, 100) }}...</p>
              <div class="flex items-center gap-4 text-xs text-gray-500">
                <span>Ticket #{{ ticket.id }}</span>
                <span>{{ formatDate(ticket.createdAt) }}</span>
                <span v-if="ticket.attachments.length > 0">{{ ticket.attachments.length }} archivo{{ ticket.attachments.length !== 1 ? 's' : '' }}</span>

              </div>
              
              <!-- Controles de administración (solo para administradores) -->
              <div v-if="isAdmin" class="flex items-center gap-2 mt-3 pt-3 border-t border-gray-200" @click.stop>
                <span class="text-xs font-medium text-gray-700"></span>
                <!-- Cambiar estado -->
                <div class="w-40">
                  <FormSelect
                    :modelValue="ticket.status"
                    @update:modelValue="changeTicketStatus(ticket.id, $event)"
                    :options="statusOptionsForAdmin"
                  />
                </div>
                
                <!-- Eliminar ticket -->
                <RemoveButton
                  size="xs"
                  variant="danger"
                  title="Eliminar ticket"
                  @click="deleteTicket(ticket.id)"
                />
              </div>
            </div>
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de detalle del ticket -->
    <TicketDetailModal
      :ticket="selectedTicket"
      @close="selectedTicket = null"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { TaskIcon } from '@/assets/icons'
import { FormSelect } from '@/shared/components/forms'
import { RemoveButton } from '@/shared/components/buttons'
import { usePermissions } from '@/shared/composables/usePermissions'
import TicketDetailModal from './TicketDetailModal.vue'
import type { SupportTicket, TicketFilters } from '../types/support.types'

// Props
const props = defineProps<{
  tickets: SupportTicket[]
}>()

// Emits
const emit = defineEmits<{
  ticketStatusChanged: [ticketId: string, newStatus: string]
  ticketDeleted: [ticketId: string]
}>()

// Composables
const { isAdmin } = usePermissions()

// Estado local
const selectedTicket = ref<SupportTicket | null>(null)

// Filtros
const filters = reactive<TicketFilters>({
  status: 'all',
  category: 'all',
  search: ''
})

// Opciones para los filtros
const statusOptions = [
  { value: 'all', label: 'Estados' },
  { value: 'open', label: 'Abiertos' },
  { value: 'in-progress', label: 'En progreso' },
  { value: 'resolved', label: 'Resueltos' },
  { value: 'closed', label: 'Cerrados' }
]

const categoryOptions = [
  { value: 'all', label: 'Categorías' },
  { value: 'bug', label: 'Error / Bug' },
  { value: 'feature', label: 'Nueva característica' },
  { value: 'question', label: 'Pregunta' },
  { value: 'technical', label: 'Problema técnico' }
]

// Opciones de estado para administradores (sin "all")
const statusOptionsForAdmin = [
  { value: 'open', label: 'Abierto' },
  { value: 'in-progress', label: 'En Progreso' },
  { value: 'resolved', label: 'Resuelto' },
  { value: 'closed', label: 'Cerrado' }
]

// Computed para tickets filtrados
const filteredTickets = computed(() => {
  return props.tickets.filter(ticket => {
    const matchesStatus = filters.status === 'all' || ticket.status === filters.status
    const matchesCategory = filters.category === 'all' || ticket.category === filters.category
    const matchesSearch = filters.search === '' || 
      ticket.title.toLowerCase().includes(filters.search.toLowerCase()) ||
      ticket.description.toLowerCase().includes(filters.search.toLowerCase())
    
    return matchesStatus && matchesCategory && matchesSearch
  })
})

// Funciones utilitarias
const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    open: 'Abierto',
    'in-progress': 'En progreso',
    resolved: 'Resuelto',
    closed: 'Cerrado'
  }
  return labels[status] || status
}

const getStatusBadgeClass = (status: string): string => {
  const classes: Record<string, string> = {
    open: 'bg-red-100 text-red-800',
    'in-progress': 'bg-yellow-100 text-yellow-800',
    resolved: 'bg-green-100 text-green-800',
    closed: 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getCategoryLabel = (category: string): string => {
  const labels: Record<string, string> = {
    bug: 'Error / Bug',
    feature: 'Nueva característica',
    question: 'Pregunta',
    technical: 'Problema técnico'
  }
  return labels[category] || category
}

// Funciones de interacción
const selectTicket = (ticket: SupportTicket) => {
  selectedTicket.value = ticket
}



const changeTicketStatus = (ticketId: string, newStatus: string) => {
  emit('ticketStatusChanged', ticketId, newStatus)
}

const deleteTicket = (ticketId: string) => {
  if (confirm('¿Estás seguro de que quieres eliminar este ticket?')) {
    emit('ticketDeleted', ticketId)
    if (selectedTicket.value?.id === ticketId) {
      selectedTicket.value = null
    }
  }
}
</script>
