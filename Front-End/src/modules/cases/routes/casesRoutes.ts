import type { RouteRecordRaw } from 'vue-router'

export const casesRoutes: RouteRecordRaw[] = [
  {
    path: '/cases',
    name: 'cases',
    children: [
      {
        path: 'new',
        name: 'cases-new',
        component: () => import('../views/NewCaseView.vue'),
        meta: {
          title: 'Nueva Muestra',
          requiresAuth: true
        }
      },
      {
        path: 'edit/:code?',
        name: 'cases-edit',
        component: () => import('../views/EditCaseView.vue'),
        meta: {
          title: 'Editar Caso',
          requiresAuth: true
        }
      },
      {
        path: 'technique-complementary',
        name: 'cases-technique-complementary',
        component: () => import('../views/TechniqueComplementaryView.vue'),
        meta: {
          title: 'Técnicas Complementarias',
          requiresAuth: true
        }
      },
      {
        path: 'to-approve',
        name: 'cases-to-approve',
        component: () => import('../../case-list/views/CasesToApproveView.vue'),
        meta: {
          title: 'Casos por Aprobar',
          requiresAuth: true
        }
      }
    ]
  }
]
