/**
 * Composable para controlar la navegación basada en roles
 * Define qué elementos del menú y navegación están disponibles para cada rol
 */

import { computed } from 'vue'
import { usePermissions } from './usePermissions'

export function useRoleNavigation() {
  const { isAdmin, isPatologo, isAuxiliar, isResidente, isFacturacion } = usePermissions()

  // Menú principal disponible para cada rol
  const availableMenuItems = computed(() => {
    const baseItems = [
      { name: 'Dashboard', path: '/dashboard', icon: 'dashboard', alwaysVisible: true },
      { name: 'Casos', path: '/cases', icon: 'cases', alwaysVisible: true },
  { name: 'Listado de Casos', path: '/cases/list', icon: 'list', alwaysVisible: true },
      { name: 'Resultados', path: '/results', icon: 'results', alwaysVisible: true },
      { name: 'Perfiles', path: '/profile', icon: 'profile', alwaysVisible: true },
      { name: 'Soporte', path: '/support', icon: 'support', alwaysVisible: true }
    ]

    const adminItems = [
      { name: 'Reportes', path: '/reports', icon: 'reports', alwaysVisible: false },
      { name: 'Estadísticas', path: '/statistics', icon: 'statistics', alwaysVisible: false },
      { name: 'Gestión de Usuarios', path: '/users', icon: 'users', alwaysVisible: false }
    ]

    const facturacionItems = [
      { name: 'Listado de Casos', path: '/case-list', icon: 'list', alwaysVisible: true },
      { name: 'Estadísticas', path: '/statistics', icon: 'statistics', alwaysVisible: true },
      { name: 'Mi Perfil', path: '/profile', icon: 'profile', alwaysVisible: true },
      { name: 'Soporte', path: '/support', icon: 'support', alwaysVisible: true }
    ]

    if (isAdmin.value) {
      return [...baseItems, ...adminItems]
    }

    if (isFacturacion.value) {
      return facturacionItems
    }

    // Mostrar Estadísticas para Auxiliar Administrativo
    if (isAuxiliar.value) {
      return [
        ...baseItems,
        { name: 'Estadísticas', path: '/statistics', icon: 'statistics', alwaysVisible: false }
      ]
    }

    return baseItems
  })

  // Funciones disponibles para cada rol
  const availableActions = computed(() => {
    const baseActions = {
      viewCases: true,
      viewResults: true,
      editProfile: true,
      accessSupport: true
    }

    if (isAdmin.value) {
      return {
        ...baseActions,
        createCases: true,
        editCases: true,
        deleteCases: true,
        signResults: true,
        manageUsers: true,
        viewReports: true,
        viewStatistics: true,
        manageSupportTickets: true
      }
    }

    if (isPatologo.value) {
      return {
        ...baseActions,
        editCases: true,
        signResults: true
      }
    }

    if (isAuxiliar.value) {
      return {
        ...baseActions,
        createCases: true,
        editCases: true
      }
    }

    if (isResidente.value) {
      return {
        ...baseActions,
        editCases: true
      }
    }

    if (isFacturacion.value) {
      return {
        viewCases: true,
        viewResults: false,
        editProfile: true,
        accessSupport: true,
        viewStatistics: true
      }
    }

    return baseActions
  })

  // Verificar si una ruta específica está disponible para el rol actual
  const canAccessRoute = (routePath: string): boolean => {
    const allowedRoutes = availableMenuItems.value.map(item => item.path)
    return allowedRoutes.some(route => routePath.startsWith(route))
  }

  // Verificar si una acción específica está disponible para el rol actual
  const canPerformAction = (action: string): boolean => {
    return availableActions.value[action as keyof typeof availableActions.value] || false
  }

  return {
    availableMenuItems,
    availableActions,
    canAccessRoute,
    canPerformAction
  }
}
