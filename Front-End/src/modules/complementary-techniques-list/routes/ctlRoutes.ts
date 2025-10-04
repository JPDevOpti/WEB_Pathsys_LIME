import type { RouteRecordRaw } from 'vue-router'

export const complementaryTechniquesListRoutes: RouteRecordRaw[] = [
  {
    path: '/complementary-techniques/list',
    name: 'complementary-techniques.list',
    component: () => import('../views/ComplementaryTechniquesListView.vue'),
    meta: {
      title: 'Listado de Técnicas Complementarias',
      requiresAuth: true,
      requiresRole: ['admin', 'pathologist', 'resident']
    }
  }
]


