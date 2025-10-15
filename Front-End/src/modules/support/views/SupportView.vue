<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="p-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Componente para crear nuevo ticket -->
        <div class="lg:col-span-1">
          <NewTicket @ticket-created="onTicketCreated" />
        </div>

        <!-- Componente para mostrar tickets existentes -->
        <div class="lg:col-span-2">
          <ActualTickets 
            :tickets="tickets" 
            @ticket-status-changed="onTicketStatusChanged"
            @ticket-deleted="onTicketDeleted"
            @tickets-updated="loadTickets"
          />
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/navigation'
import { NewTicket, ActualTickets } from '../components'
import { ticketsService } from '@/shared/services/tickets.service'
import { useAuthStore } from '@/stores/auth.store'
import type { SupportTicket } from '../types/support.types'

const currentPageTitle = ref('Soporte')
const authStore = useAuthStore()

// Estado de tickets (datos reales desde API)
const tickets = ref<SupportTicket[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

// Función para cargar tickets desde la API
const loadTickets = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    // Proactively check and refresh token before making API call
    console.log('🔍 [SUPPORT] Checking token before loading tickets...')
    const tokenRefreshed = await authStore.checkAndRefreshToken()
    
    if (!tokenRefreshed && !authStore.isAuthenticated) {
      console.warn('⚠️ [SUPPORT] Token refresh failed and user not authenticated')
      error.value = 'Sesión expirada. Por favor, inicia sesión nuevamente.'
      return
    }
    
    // Add a small delay to ensure token is properly stored before API call
    await new Promise(resolve => setTimeout(resolve, 100))
    
    console.log('✅ [SUPPORT] Token verified/refreshed, proceeding with API call')
    tickets.value = await ticketsService.getTickets()
  } catch (err: any) {
    console.error('Error cargando tickets:', err)
    error.value = err?.response?.data?.detail || 'Error al cargar los tickets'
    // TODO: Reemplazar alert con notificación centrada
    alert(`Error: ${error.value}`)
  } finally {
    isLoading.value = false
  }
}

// Función para manejar la creación de tickets (defensiva)
const onTicketCreated = (newTicket: SupportTicket) => {
  if (!Array.isArray(tickets.value)) tickets.value = []
  tickets.value.unshift(newTicket)
}

// Función para manejar el cambio de estado de tickets
const onTicketStatusChanged = (ticketCode: string, newStatus: string) => {
  const ticket = tickets.value.find(t => t.ticket_code === ticketCode)
  if (ticket) {
    ticket.status = newStatus as any
  }
}

// Función para manejar la eliminación de tickets
const onTicketDeleted = (ticketCode: string) => {
  const index = tickets.value.findIndex(t => t.ticket_code === ticketCode)
  if (index > -1) {
    tickets.value.splice(index, 1)
  }
}

// Cargar tickets al montar el componente
onMounted(() => {
  loadTickets()
})
</script>