/**
 * Composable para manejar permisos y restricciones de roles
 */

import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import type { RolEnum } from '@/modules/auth/types/auth.types'

export function usePermissions() {
  const authStore = useAuthStore()

  // Getters para verificar roles específicos
  const isAdmin = computed(() => authStore.isAdministrador)
  const isAuxiliar = computed(() => authStore.isAuxiliar)
  const isPatologo = computed(() => authStore.isPatologo)
  const isResidente = computed(() => authStore.isResidente)
  const isRecepcionista = computed(() => authStore.userRole === 'recepcionista')

  // Permisos específicos por funcionalidad
  const canCreateCases = computed(() => isAdmin.value || isRecepcionista.value)
  const canEditCases = computed(() => isAdmin.value || isPatologo.value || isRecepcionista.value)
  const canSignResults = computed(() => isAdmin.value || isPatologo.value)
  const canManageUsers = computed(() => isAdmin.value)
  const canDeleteRecords = computed(() => isAdmin.value)
  const canAccessSupport = computed(() => true) // Todos los roles pueden acceder a soporte
  const canManageSupportTickets = computed(() => isAdmin.value) // Solo admin puede gestionar tickets
  
  // Permisos específicos por módulo
  const canAccessDashboard = computed(() => true) // Todos pueden acceder al dashboard
  const canAccessCases = computed(() => isAdmin.value || isPatologo.value || isAuxiliar.value || isResidente.value) // Patólogos, auxiliares y residentes pueden acceder a casos
  const canAccessCaseList = computed(() => isAdmin.value || isPatologo.value || isAuxiliar.value || isResidente.value) // Patólogos, auxiliares y residentes pueden ver listado de casos
  const canAccessResults = computed(() => isAdmin.value || isPatologo.value || isAuxiliar.value || isResidente.value) // Patólogos, auxiliares y residentes pueden acceder a resultados
  const canAccessProfile = computed(() => true) // Todos pueden acceder a perfil
  const canAccessReports = computed(() => isAdmin.value) // Solo admin puede acceder a reportes
  const canAccessStatistics = computed(() => isAdmin.value) // Solo admin puede acceder a estadísticas

  // Función para verificar si un usuario tiene un rol específico
  const hasRole = (role: RolEnum): boolean => {
    return authStore.userRole === role
  }

  // Función para verificar si un usuario tiene alguno de los roles especificados
  const hasAnyRole = (roles: RolEnum[]): boolean => {
    return roles.includes(authStore.userRole as RolEnum)
  }

  // Función para verificar si un usuario tiene todos los roles especificados
  const hasAllRoles = (roles: RolEnum[]): boolean => {
    return roles.every(role => authStore.userRole === role)
  }

  return {
    // Getters de roles
    isAdmin,
    isAuxiliar,
    isPatologo,
    isResidente,
    isRecepcionista,
    
    // Permisos específicos
    canCreateCases,
    canEditCases,
    canSignResults,
    canManageUsers,
    canDeleteRecords,
    canAccessSupport,
    canManageSupportTickets,
    
    // Permisos por módulo
    canAccessDashboard,
    canAccessCases,
    canAccessCaseList,
    canAccessResults,
    canAccessProfile,
    canAccessReports,
    canAccessStatistics,
    
    // Funciones de verificación
    hasRole,
    hasAnyRole,
    hasAllRoles
  }
}
