import type { RouteRecordRaw } from 'vue-router'

export const profileRoutes: RouteRecordRaw[] = [
  {
    path: '/profile',
    name: 'profile',
    redirect: '/profile/my-profile',
    children: [
      {
        path: 'my-profile',
        name: 'profile-my-profile',
        component: () => import('../views/MyProfileView.vue'),
        meta: {
          title: 'Mi Perfil',
          requiresAuth: true
        }
      },
      {
        path: 'users',
        name: 'profile-users',
        component: () => import('../views/ManageUsersView.vue'),
        meta: {
          title: 'Gestión de Usuarios',
          requiresAuth: true
        }
      }
    ]
  }
]


