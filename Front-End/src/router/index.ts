import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { roleGuard } from './guards/roleGuard'
import { dashboardRoutes } from '@/modules/dashboard/routes/dashboardRoutes'
import { authRoutes } from '@/modules/auth/routes/authRoutes'
import { casesRoutes } from '@/modules/cases/routes/casesRoutes'
import { profileRoutes } from '@/modules/profile/routes/profileRoutes'
import { caseListRoutes } from '@/modules/case-list/routes/caseListRoutes'
import { resultsRoutes } from '@/modules/results/routes/resultsRoutes'
import { reportsRoutes } from '@/modules/reports/routes/reportsRoutes'
import { supportRoutes } from '@/modules/support/routes/supportRoutes'
import { complementaryTechniquesRoutes } from '@/modules/complementary-techniques/routes/complementaryTechniquesRoutes'
import { casesApprovalRoutes } from '@/modules/cases-approval/routes/casesApprovalRoutes'
import { patientsRoutes } from '@/modules/patients/routes/patientsRoutes'
import { patientListRoutes } from '@/modules/patients-list/routes'
import { pathologistAssignmentRoutes } from '@/modules/pathologist-assignment'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/dashboard'
    },
    ...authRoutes,
    ...dashboardRoutes,
    ...casesRoutes,
    ...profileRoutes,
    ...caseListRoutes,
    ...resultsRoutes,
    ...reportsRoutes,
    ...supportRoutes,
    ...complementaryTechniquesRoutes,
    ...casesApprovalRoutes,
    ...patientsRoutes,
    ...patientListRoutes,
    ...pathologistAssignmentRoutes
  ]
})

// Guarda de Navegación: Gestiona el acceso a las rutas según el estado de autenticación.
// Este middleware se ejecuta antes de cada cambio de ruta para verificar si el usuario
// tiene permiso para acceder a la página solicitada.
// - Redirige a los usuarios no autenticados a la página de inicio de sesión si intentan acceder a una ruta protegida.
// - Redirige a los usuarios ya autenticados fuera de las páginas públicas (como /login) hacia el dashboard.
// - Intenta restaurar el estado de autenticación desde el almacenamiento local en la carga inicial.
// - Valida permisos específicos como acceso a estadísticas.
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  
  // Rutas públicas que no requieren autenticación
  const publicRoutes = ['/login']
  const isPublicRoute = publicRoutes.includes(to.path)
  
  // Si no está autenticado, intentar inicializar desde localStorage solo una vez
  if (!authStore.isAuthenticated) {
    await authStore.initializeAuth()
  }
  
  // Check token expiration and force logout if expired (read from storage decoded from JWT exp)
  if (authStore.isAuthenticated) {
    const savedExpiresAt = localStorage.getItem('auth_expires_at') || sessionStorage.getItem('auth_expires_at')
    if (savedExpiresAt && Number(savedExpiresAt) > 0 && Date.now() > Number(savedExpiresAt)) {
      await authStore.logout()
      next('/login')
      return
    }
  }

  // Si la ruta es pública y el usuario está autenticado, redirigir al dashboard
  if (isPublicRoute && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }
  
  // Si la ruta requiere autenticación y el usuario no está autenticado
  if (!isPublicRoute && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // Aplicar restricciones de rol si está autenticado
  if (authStore.isAuthenticated) {
    roleGuard(to, _from, next)
    return
  }
  
  // Continuar con la navegación
  next()
})

export default router