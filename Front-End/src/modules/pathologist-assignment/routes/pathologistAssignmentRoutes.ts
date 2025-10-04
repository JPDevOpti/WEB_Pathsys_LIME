import type { RouteRecordRaw } from 'vue-router'

export const pathologistAssignmentRoutes: RouteRecordRaw[] = [
  {
    path: '/pathologist-assignment',
    name: 'pathologist-assignment',
    component: () => import('../views/PathologistAssignmentView.vue'),
    meta: {
      title: 'Asignación de Patólogos',
      requiresAuth: true,
      roles: ['admin', 'pathologist'] // Ajustar según los roles que necesiten acceso
    }
  },
  {
    path: '/cases/assign-pathologists',
    redirect: { name: 'pathologist-assignment' }
  }
]

