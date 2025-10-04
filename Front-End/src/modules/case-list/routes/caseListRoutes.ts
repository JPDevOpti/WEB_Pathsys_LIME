import { RouteRecordRaw } from 'vue-router'

export const caseListRoutes: RouteRecordRaw[] = [
  {
    path: '/cases/list',
    name: 'case-list.current',
    component: () => import('../views/CurrentCasesListView.vue'),
    meta: {
      title: 'Casos Actuales'
    }
  },
  // Redirect old URL to new list path for backward compatibility
  {
    path: '/cases/current',
    redirect: '/cases/list'
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
    component: () => import('../../cases-approval/views/CasesToApproveView.vue'),
    meta: {
      title: 'Casos por Aprobar'
    }
  }
]


