import type { RouteRecordRaw } from 'vue-router'

export const casesApprovalRoutes: RouteRecordRaw[] = [
  {
    path: '/cases/to-approve',
    name: 'cases-approval.list',
    component: () => import('../views/CasesToApproveView.vue'),
    meta: {
      title: 'Casos por Aprobar',
      requiresAuth: true,
      requiresRole: ['admin']
    }
  }
]






