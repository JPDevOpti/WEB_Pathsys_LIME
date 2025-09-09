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
    return
  }

  const userRole = authStore.userRole
  
  // SIEMPRE permitir acceso al dashboard para evitar bucles infinitos
  if (to.path === '/dashboard') {
    return
  }
  
  // Si no hay rol definido, permitir acceso (fallback)
  if (!userRole) {
    return
  }
  
  // Definir las rutas permitidas para cada rol
  const roleRoutes: Record<string, string[]> = {
    patologo: [
      '/dashboard',
      '/cases',
      '/results',
      '/profile',
      '/support'
    ],
    auxiliar: [
      '/dashboard',
      '/cases',
      '/results',
      '/profile',
      '/reports',
      '/statistics',
      '/support'
    ],
    residente: [
      '/dashboard',
      '/cases',
      '/results',
      '/profile',
      '/reports',
      '/support'
    ],
    administrador: [
      '/dashboard',
      '/cases',
      '/results',
      '/profile',
      '/reports',
      '/statistics',
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
}
