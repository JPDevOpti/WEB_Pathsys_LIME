import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

/**
 * Guard para validar acceso basado en roles
 * Controla qué páginas puede visitar cada rol
 */
export function roleGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const authStore = useAuthStore()
  // Si no está autenticado, continuar (el guard principal ya maneja esto)
  if (!authStore.isAuthenticated) {
    next()
    return
  }
  // Normalizar rol para evitar discrepancias por mayúsculas/minúsculas o acentos
  const rawRole = authStore.userRole || ''
  const userRole = rawRole.toString().trim().toLowerCase()
  
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
    // Patólogo (inglés y español)
    pathologist: [
      '/dashboard',
      '/cases',
      '/results',
      '/complementary-techniques',
      '/patients',
      '/profile',
      '/support'
    ],
    patologo: [
      '/dashboard',
      '/cases',
      '/results',
      '/complementary-techniques',
      '/patients',
      '/profile',
      '/support'
    ],
    'patólogo': [
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
    // Alias en español para residente
    residente: [
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
    // Alias en español para facturación
    facturacion: [
      '/dashboard',
      '/cases/list',
      '/statistics',
      '/profile',
      '/support'
    ],
    'facturación': [
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
    // Administrador (inglés y español)
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
    administrador: [
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
    // Paciente (inglés y español)
    patient: [
      '/dashboard',
      '/cases/list',
      '/profile',
      '/support'
    ],
    paciente: [
      '/dashboard',
      '/cases/list',
      '/profile',
      '/support'
    ],
    // Recepcionista (inglés y español)
    receptionist: [
      '/dashboard',
      '/cases/list',
      '/profile',
      '/support'
    ],
    recepcionista: [
      '/dashboard',
      '/cases/list',
      '/profile',
      '/support'
    ],
    // Additional role mappings for potential backend role variations
    // Auxiliar (variaciones)
    auxiliary: [
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
    // Admin (alias)
    admin: [
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
    ]
  }

  // Obtener rutas permitidas para el rol del usuario
  const allowedRoutes = roleRoutes[userRole] || []
  
  // Verificar si la ruta actual está permitida para el rol
  let isRouteAllowed = allowedRoutes.some((route: string) => 
    to.path.startsWith(route)
  )

  // Fallback: Allow access to support for any authenticated user, regardless of role
  if (!isRouteAllowed && to.path === '/support') {
    isRouteAllowed = true
  }

  if (!isRouteAllowed) {
    // Redirigir al dashboard sin mensaje de error
    next({ path: '/dashboard' })
    return
  }
  
  // Si la ruta está permitida, continuar
  next()
}
