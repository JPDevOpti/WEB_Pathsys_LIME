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
      '/complementary-techniques',
      '/patients',
      '/profile',
      '/support'
    ],
    auxiliar: [
      '/dashboard',
      '/cases',
      '/results',
      '/complementary-techniques',
      '/patients',
      '/profile',
      '/reports',
      '/statistics',
      '/support'
    ],
    resident: [
      '/dashboard',
      '/cases',
      '/results',
      '/complementary-techniques',
      '/patients',
      '/profile',
      '/reports',
      '/support'
    ],
    billing: [
      '/dashboard',
      '/cases/list',
      '/statistics',
      '/profile',
      '/support'
    ],
    user: [
      '/dashboard',
      '/cases/list',
      '/statistics',
      '/profile',
      '/support'
    ],
    administrator: [
      '/dashboard',
      '/cases',
      '/results',
      '/complementary-techniques',
      '/patients',
      '/profile',
      '/reports',
      '/statistics',
      '/support',
      '/pathologist-assignment'
    ],
    patient: [
      '/dashboard',
      '/cases/list',
      '/profile',
      '/support'
    ],
    receptionist: [
      '/dashboard',
      '/cases/list',
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

  // Debug para la ruta de asignación de patólogos
  if (to.path === '/pathologist-assignment') {
    console.log('🔍 [DEBUG RoleGuard] Intentando acceder a:', to.path)
    console.log('🔍 [DEBUG RoleGuard] Rol del usuario:', userRole)
    console.log('🔍 [DEBUG RoleGuard] Rutas permitidas:', allowedRoutes)
    console.log('🔍 [DEBUG RoleGuard] ¿Ruta permitida?:', isRouteAllowed)
  }

  if (!isRouteAllowed) {
    // Redirigir al dashboard sin mensaje de error
    console.log('🔍 [DEBUG RoleGuard] Redirigiendo al dashboard desde:', to.path)
    next({ path: '/dashboard' })
    return
  }
  
  // Si la ruta está permitida, continuar
  next()
}
