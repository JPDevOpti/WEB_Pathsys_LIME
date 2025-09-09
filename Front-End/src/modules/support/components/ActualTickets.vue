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
          <div class="w-48">
            <FormInputField
              v-model="filters.search"
              placeholder="Buscar tickets..."
              :showIcon="true"
            />
          </div>
          <div class="w-40">
            <FormSelect
              v-model="filters.estado"
              :options="statusOptions"
              placeholder="Estado"
            />
          </div>
          
          <div class="w-44">
            <FormSelect
              v-model="filters.categoria"
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
          :key="ticket.ticket_code"
          class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
          @click="selectTicket(ticket)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <h3 class="font-medium text-gray-900">{{ ticket.titulo }}</h3>
                <span :class="getStatusBadgeClass(ticket.estado)" class="text-xs font-medium px-2 py-1 rounded-full">
                  {{ getStatusLabel(ticket.estado) }}
                </span>
                <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {{ getCategoryLabel(ticket.categoria) }}
                </span>
              </div>
              <div v-if="ticket.descripcion" class="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-2">
                <p class="text-sm text-gray-700 whitespace-pre-line">{{ ticket.descripcion }}</p>
              </div>
              <div class="flex items-center gap-4 text-xs text-gray-500">
                <span>Ticket {{ ticket.ticket_code }}</span>
                <span>{{ ticket.fecha_ticket ? formatDate(ticket.fecha_ticket) : '' }}</span>
                <span v-if="ticket.imagen">1 imagen adjunta</span>
              </div>
              
              <!-- Controles de administración (solo para administradores) -->
              <div v-if="isAdmin" class="flex items-center gap-2 mt-3 pt-3 border-t border-gray-200" @click.stop>
                <span class="text-xs font-medium text-gray-700"></span>
                <!-- Cambiar estado -->
                <div class="w-40">
                  <FormSelect
                    :modelValue="ticket.estado"
                    @update:modelValue="changeTicketStatus(ticket.ticket_code, $event)"
                    :options="statusOptionsForAdmin"
                  />
                </div>
                
                <!-- Eliminar ticket -->
                <RemoveButton
                  size="xs"
                  variant="danger"
                  title="Eliminar ticket"
                  :loading="isLoading && pendingDeleteCode === ticket.ticket_code"
                  @click="(e: MouseEvent) => { e?.stopPropagation(); deleteTicket(ticket.ticket_code) }"
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

    <!-- Confirmación de eliminación -->
    <ConfirmDialog
      :model-value="showConfirm"
      title="Eliminar ticket"
      message="¿Estás seguro de eliminar este ticket? Esta acción no se puede deshacer."
      confirm-text="Eliminar"
      cancel-text="Cancelar"
      @update:modelValue="v => showConfirm = v as boolean"
      @confirm="confirmDelete"
      @cancel="showConfirm = false"
    />

    

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { TaskIcon } from '@/assets/icons'
import { FormSelect, FormInputField } from '@/shared/components/forms'
import { RemoveButton } from '@/shared/components/buttons'
import { ConfirmDialog } from '@/shared/components/feedback'
import { useToasts } from '@/shared/composables/useToasts'
import { usePermissions } from '@/shared/composables/usePermissions'
import { ticketsService } from '@/shared/services/tickets.service'
import TicketDetailModal from './TicketDetailModal.vue'
import type { SupportTicket, TicketFilters, TicketStatusEnum } from '../types/support.types'

// Props
const props = defineProps<{
  tickets: SupportTicket[]
}>()

// Emits
const emit = defineEmits<{
  ticketStatusChanged: [ticketCode: string, newStatus: string]
  ticketDeleted: [ticketCode: string]
  ticketsUpdated: []
}>()

// Composables
const { isAdmin } = usePermissions()

// Estado local
const selectedTicket = ref<SupportTicket | null>(null)
const isLoading = ref(false)
const showConfirm = ref(false)
const pendingDeleteCode = ref<string | null>(null)
const { success, error } = useToasts()
const showUpdate = (msg: string) => success('update', 'Ticket', msg, 3500)
const showDelete = (msg: string) => success('delete', 'Ticket', msg, 3500)
const showError = (msg: string) => error('generic', 'Error', msg, 5000)

// Filtros
const filters = reactive<TicketFilters>({
  estado: 'all',
  categoria: 'all',
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
  return props.tickets
    .filter(ticket => !!ticket && typeof ticket === 'object')
    .map(t => ({
      ticket_code: (t as any).ticket_code ?? (t as any).id ?? '',
      titulo: (t as any).titulo ?? (t as any).title ?? '',
      categoria: (t as any).categoria ?? (t as any).category ?? '',
      descripcion: (t as any).descripcion ?? (t as any).description ?? '',
      imagen: (t as any).imagen ?? (Array.isArray((t as any).attachments) && (t as any).attachments.length ? (t as any).attachments[0]?.previewUrl : undefined),
      fecha_ticket: (t as any).fecha_ticket ?? (t as any).createdAt ?? '',
      estado: (t as any).estado ?? (t as any).status ?? 'open'
    }))
    .filter(ticket => {
    const matchesStatus = filters.estado === 'all' || ticket.estado === filters.estado
    const matchesCategory = filters.categoria === 'all' || ticket.categoria === filters.categoria
    const matchesSearch = filters.search === '' || 
      ticket.titulo.toLowerCase().includes(filters.search.toLowerCase()) ||
      ticket.descripcion.toLowerCase().includes(filters.search.toLowerCase())
    
    return matchesStatus && matchesCategory && matchesSearch
  })
})

// Watch para recargar tickets cuando cambian los filtros (con debounce)
let searchTimeout: NodeJS.Timeout | null = null
watch(filters, () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    emit('ticketsUpdated')
  }, 300)
}, { deep: true })

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

const changeTicketStatus = async (ticketCode: string, newStatus: string) => {
  try {
    isLoading.value = true
    await ticketsService.changeStatus(ticketCode, newStatus as TicketStatusEnum)
    emit('ticketStatusChanged', ticketCode, newStatus)
    emit('ticketsUpdated')
    showUpdate('Estado actualizado correctamente')
  } catch (error: any) {
    console.error('Error cambiando estado:', error)
    const message = error?.response?.data?.detail || 'Error al cambiar el estado'
    showError(message)
  } finally {
    isLoading.value = false
  }
}

const deleteTicket = (ticketCode: string) => {
  pendingDeleteCode.value = ticketCode
  showConfirm.value = true
}

const confirmDelete = async () => {
  if (!pendingDeleteCode.value) return
  try {
    isLoading.value = true
    await ticketsService.deleteTicket(pendingDeleteCode.value)
    emit('ticketDeleted', pendingDeleteCode.value)
    emit('ticketsUpdated')
    showDelete('Ticket eliminado correctamente')
    
    if (selectedTicket.value?.ticket_code === pendingDeleteCode.value) {
      selectedTicket.value = null
    }
  } catch (error: any) {
    console.error('Error eliminando ticket:', error)
    const message = error?.response?.data?.detail || 'Error al eliminar el ticket'
    showError(message)
  } finally {
    isLoading.value = false
    showConfirm.value = false
    pendingDeleteCode.value = null
  }
}
</script>
