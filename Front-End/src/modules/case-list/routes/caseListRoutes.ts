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
    path: '/preview-multiple',
    name: 'case-list.preview-multiple',
    component: () => import('../views/MultiplePreviewView.vue'),
    meta: {
      title: 'Vista Previa Múltiple'
    }
  }
]


