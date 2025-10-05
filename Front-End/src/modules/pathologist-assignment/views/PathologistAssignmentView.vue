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
import { useAuthStore } from '@/stores/auth.store'
import { usePermissions } from '@/shared/composables/usePermissions'

// Debug: Verificar permisos del usuario
const authStore = useAuthStore()
const { isAdmin } = usePermissions()

console.log('🔍 [DEBUG] Usuario actual:', authStore.user)
console.log('🔍 [DEBUG] Rol del usuario:', authStore.userRole)
console.log('🔍 [DEBUG] ¿Es administrador?:', isAdmin.value)

// Handle successful pathologist assignment
const handlePatologoAsignado = (data: AssignmentEventData) => {
  console.log('Patólogo asignado:', data)
  // Aquí puedes agregar lógica adicional como actualizar listas, 
  // mostrar notificaciones globales, etc.
}
</script>
