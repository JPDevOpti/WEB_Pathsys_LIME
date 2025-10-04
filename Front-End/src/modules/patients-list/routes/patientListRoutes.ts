import { RouteRecordRaw } from 'vue-router'

export const patientListRoutes: RouteRecordRaw[] = [
  {
    path: '/patients/list',
    name: 'patients-list',
    component: () => import('../views/PatientsListView.vue'),
    meta: {
      title: 'Lista de Pacientes'
    }
  },
  // Redirect old URL to new list path for backward compatibility
  {
    path: '/patients',
    redirect: '/patients/list'
  }
]