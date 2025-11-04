import type { RouteRecordRaw } from 'vue-router'

export const unreadCasesRoutes: RouteRecordRaw[] = [
  {
    path: '/unread-cases',
    name: 'unread-cases',
    component: () => import('../views/UnreadCasesView.vue'),
    meta: { title: 'Casos sin lectura', requiresAuth: true }
  }
]
