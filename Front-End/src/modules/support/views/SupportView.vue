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
          />
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/navigation'
import { NewTicket, ActualTickets } from '../components'
import type { SupportTicket } from '../types/support.types'

const currentPageTitle = ref('Soporte')

// Estado de tickets (datos dummy)
const tickets = ref<SupportTicket[]>([
  {
    id: '1',
    title: 'Error al cargar lista de casos',
    category: 'bug',
    description: 'Cuando intento acceder a la lista de casos, la página se queda cargando indefinidamente. Esto ha estado pasando desde ayer.',
    status: 'open',
    createdAt: '2024-01-15T10:30:00Z',
    attachments: []
  },
  {
    id: '2',
    title: 'Solicitud: Exportar reportes a Excel',
    category: 'feature',
    description: 'Sería muy útil poder exportar los reportes de patólogos y entidades a formato Excel para análisis más detallados.',
    status: 'in-progress',
    createdAt: '2024-01-14T14:20:00Z',
    attachments: []
  },
  {
    id: '3',
    title: 'No puedo cambiar mi contraseña',
    category: 'technical',
    description: 'Cuando intento cambiar mi contraseña en el perfil, me sale un error que dice "Token inválido".',
    status: 'resolved',
    createdAt: '2024-01-13T09:15:00Z',
    attachments: []
  }
])

// Función para manejar la creación de tickets
const onTicketCreated = (newTicket: SupportTicket) => {
  tickets.value.unshift(newTicket)
}

// Función para manejar el cambio de estado de tickets
const onTicketStatusChanged = (ticketId: string, newStatus: string) => {
  const ticket = tickets.value.find(t => t.id === ticketId)
  if (ticket) {
    ticket.status = newStatus as any
  }
}

// Función para manejar la eliminación de tickets
const onTicketDeleted = (ticketId: string) => {
  const index = tickets.value.findIndex(t => t.id === ticketId)
  if (index > -1) {
    tickets.value.splice(index, 1)
  }
}
</script>