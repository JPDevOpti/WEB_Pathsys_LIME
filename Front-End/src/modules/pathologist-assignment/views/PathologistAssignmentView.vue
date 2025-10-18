<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Asignación de Patólogos" />
    <PathologistAssignmentForm @patologo-asignado="handlePatologoAsignado" />
  </AdminLayout>
</template>

<script setup lang="ts">
import { AdminLayout } from '@/shared'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import { PathologistAssignmentForm } from '../components'
import type { AssignmentEventData } from '../types'

// Handle successful pathologist assignment
const handlePatologoAsignado = (data: AssignmentEventData) => {
  console.log('Patólogo asignado:', data)
  // Aquí puedes agregar lógica adicional como actualizar listas, 
  // mostrar notificaciones globales, etc.
}
</script>
