import type { RouteRecordRaw } from 'vue-router'

export const complementaryTechniquesRoutes: RouteRecordRaw[] = [
  {
    path: '/complementary-techniques',
    name: 'complementary-techniques',
    component: () => import('../views/ComplementaryTechniquesView.vue'),
    meta: {
      title: 'Técnicas Complementarias',
      requiresAuth: true,
      requiresRole: ['admin', 'pathologist', 'resident']
    }
  }
]
