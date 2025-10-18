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
authStore.initializeAuth().then(() => {
  app.mount('#app')
}).catch((error) => {
  console.error('Error initializing auth store:', error)
  app.mount('#app') // Mount anyway to avoid blocking the app
})