import { RouteRecordRaw } from 'vue-router'

export const caseListRoutes: RouteRecordRaw[] = [
  {
    path: '/cases/current',
    name: 'case-list.current',
    component: () => import('../views/CurrentCasesListView.vue'),
    meta: {
      title: 'Casos Actuales'
    }
  },
  {
    path: '/cases/previous',
    name: 'case-list.previous',
    component: () => import('../views/PreviousCasesListView.vue'),
    meta: {
      title: 'Casos Anteriores'
    }
  },
  {
    path: '/cases/to-approve',
    name: 'case-list.to-approve',
    component: () => import('../views/CasesToApproveView.vue'),
    meta: {
      title: 'Casos por Aprobar'
    }
  },
  {
    path: '/cases/complementary-techniques',
    name: 'case-list.complementary-techniques',
    component: () => import('../views/ComplementaryTechniquesView.vue'),
    meta: {
      title: 'Técnicas Complementarias',
      requiresAuth: true,
      requiresRole: ['admin', 'pathologist', 'resident']
    }
  }
]


