import type { RouteRecordRaw } from 'vue-router'

export const reportsRoutes: RouteRecordRaw[] = [
  {
    path: '/statistics',
    name: 'statistics',
    children: [
      {
        path: 'opportunity',
        name: 'statistics-opportunity',
        component: () => import('../views/OpportunityReportsView.vue'),
        meta: {
          title: 'Reportes de Oportunidad',
          requiresAuth: true,
          requiresStatisticsAccess: true
        }
      },
      {
        path: 'pathologists',
        name: 'statistics-pathologists',
        component: () => import('../views/PathologistsReportsView.vue'),
        meta: {
          title: 'Reportes de Patólogos',
          requiresAuth: true,
          requiresStatisticsAccess: true
        }
      },
      {
        path: 'entities',
        name: 'statistics-entities',
        component: () => import('../views/EntitiesReportsView.vue'),
        meta: {
          title: 'Reportes de Entidades',
          requiresAuth: true,
          requiresStatisticsAccess: true
        }
      },
      {
        path: 'tests',
        name: 'statistics-tests',
        component: () => import('../views/TestsReportsView.vue'),
        meta: {
          title: 'Reportes de Pruebas',
          requiresAuth: true,
          requiresStatisticsAccess: true
        }
      }
    ]
  }
]
