import { RouteRecordRaw } from 'vue-router'

export const authRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: {
      requiresAuth: false,
      title: 'Sign In'
    }
  },
  {
    path: '/auth/login',
    name: 'auth-login',
    component: () => import('../views/LoginView.vue'),
    meta: {
      requiresAuth: false,
      title: 'Sign In'
    }
  }
] 