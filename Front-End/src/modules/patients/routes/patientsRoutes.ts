import type { RouteRecordRaw } from 'vue-router'

export const patientsRoutes: RouteRecordRaw[] = [
  {
    path: '/patients/new',
    name: 'patients-new',
    component: () => import('../views/NewPatientView.vue'),
    meta: { title: 'Crear Paciente', requiresAuth: true }
  },
  {
    path: '/patients/edit',
    name: 'patients-edit',
    component: () => import('../views/EditPatientView.vue'),
    meta: { title: 'Editar Paciente', requiresAuth: true }
  }
]






