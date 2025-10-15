import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'
import VueApexCharts from 'vue3-apexcharts'
import { useAuthStore } from '@/stores/auth.store'

// Inicializar funciones de prueba en desarrollo
if (import.meta.env.DEV) {
  import('./utils/consoleTestSetup')
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueApexCharts as any)

// Initialize auth store after Pinia is set up
const authStore = useAuthStore()
console.log('🔍 [DEBUG Main] Initializing auth store on app startup')
authStore.initializeAuth().then(() => {
  console.log('🔍 [DEBUG Main] Auth store initialized, mounting app')
  app.mount('#app')
}).catch((error) => {
  console.error('🔍 [DEBUG Main] Error initializing auth store:', error)
  app.mount('#app') // Mount anyway to avoid blocking the app
})