import { RouteRecordRaw } from 'vue-router'

export const resultsRoutes: RouteRecordRaw[] = [
  {
    path: '/results/perform',
    name: 'results-perform',
    component: () => import('../views/PerformResultsView.vue'),
    meta: {
      title: 'Realizar Resultados'
    }
  },
  {
    path: '/results/sign',
    name: 'results-sign',
    component: () => import('../views/SignResultsView.vue'),
    meta: {
      title: 'Firmar Resultados'
    }
  },
  {
    path: '/results/preview',
    name: 'results-preview',
    component: () => import('../views/PreviewReportView.vue'),
    meta: {
      title: 'Previsualización de Informe'
    }
  }
]


