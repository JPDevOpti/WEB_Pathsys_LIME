import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

/**
 * Guard para validar acceso basado en roles
 * Controla qué páginas puede visitar cada rol
 */
export function roleGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const authStore = useAuthStore()
  
  // Si no está autenticado, continuar (el guard principal ya maneja esto)
  if (!authStore.isAuthenticated) {
    next()
    return
  }

  const userRole = authStore.userRole
  
  // Debug: mostrar información del usuario y rol
  console.log('RoleGuard - User:', authStore.user)
  console.log('RoleGuard - UserRole:', userRole)
  console.log('RoleGuard - Navigating to:', to.path)
  
  // SIEMPRE permitir acceso al dashboard para evitar bucles infinitos
  if (to.path === '/dashboard') {
    next()
    return
  }
  
  // Si no hay rol definido, permitir acceso (fallback)
  if (!userRole) {
    next()
    return
  }
  
  // Definir las rutas permitidas para cada rol
  const roleRoutes: Record<string, string[]> = {
    pathologist: [
      '/dashboard',
      '/cases',
      '/results',
      '/profile',
      '/support'
    ],
    auxiliary: [
      '/dashboard',
      '/cases',
      '/results',
      '/profile',
      '/reports',
      '/statistics',
      '/support'
    ],
    resident: [
      '/dashboard',
      '/cases',
      '/results',
      '/profile',
      '/reports',
      '/support'
    ],
    billing: [
      '/dashboard',
      '/cases/current',
      '/statistics',
      '/profile',
      '/support'
    ],
    user: [
      '/dashboard',
      '/cases/current',
      '/statistics',
      '/profile',
      '/support'
    ],
    administrator: [
      '/dashboard',
      '/cases',
      '/results',
      '/profile',
      '/reports',
      '/statistics',
      '/support'
    ],
    patient: [
      '/dashboard',
      '/profile',
      '/support'
    ],
    receptionist: [
      '/dashboard',
      '/cases/current',
      '/profile',
      '/support'
    ]
  }

  // Obtener rutas permitidas para el rol del usuario
  const allowedRoutes = roleRoutes[userRole] || []
  
  // Verificar si la ruta actual está permitida para el rol
  const isRouteAllowed = allowedRoutes.some((route: string) => 
    to.path.startsWith(route)
  )

  if (!isRouteAllowed) {
    // Redirigir al dashboard sin mensaje de error
    next({ path: '/dashboard' })
    return
  }
  
  // Si la ruta está permitida, continuar
  next()
}
