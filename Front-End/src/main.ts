import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'
import VueApexCharts from 'vue3-apexcharts'

// Inicializar funciones de prueba en desarrollo
if (import.meta.env.DEV) {
  import('./utils/consoleTestSetup')
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueApexCharts as any)
app.mount('#app')