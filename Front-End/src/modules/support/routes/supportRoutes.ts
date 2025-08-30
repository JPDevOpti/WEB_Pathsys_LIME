import type { RouteRecordRaw } from 'vue-router'

export const supportRoutes: RouteRecordRaw[] = [
  {
    path: '/support',
    name: 'support',
    component: () => import('../views/SupportView.vue'),
    meta: {
      title: 'Soporte',
      requiresAuth: true
    }
  }
]
