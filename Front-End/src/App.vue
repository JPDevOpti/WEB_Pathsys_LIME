<template>
  <div id="app">
    <!-- Mostrar spinner de carga mientras se inicializa la autenticación -->
    <div v-if="!isInitialized" class="loading-screen">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Cargando...</p>
      </div>
    </div>
    
    <!-- Contenido principal cuando está inicializado -->
    <router-view v-else />
    <!-- Toasts globales -->
    <ToastContainer />

    <!-- Notificación centrada para firma faltante -->
    <SignatureNotice
      :visible="signatureNoticeVisible && isInitialized"
      @close="handleSignatureNoticeClose"
    />
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthPersistence } from './composables/useAuthPersistence'
import ToastContainer from '@/shared/components/ui/feedback/ToastContainer.vue'
import { SignatureNotice } from '@/shared/components/ui/feedback'
import { useSignatureNotifier } from '@/shared/composables/useSignatureNotifier'

// Inicializar persistencia de autenticación
const { isInitialized } = useAuthPersistence()
const route = useRoute()

// Control de notificación centrada
const { visible: signatureNoticeVisible, checkAndShowOncePerSession, close: closeSignatureNotice } = useSignatureNotifier()

const handleSignatureNoticeClose = () => closeSignatureNotice()

// Mostrar al finalizar inicialización
watch(() => isInitialized.value, (ready) => {
  console.log('[App] isInitialized changed', ready)
  if (ready) checkAndShowOncePerSession()
}, { immediate: true })

// Mostrar al entrar al dashboard
// Comentario: Dispara la verificación solo cuando la ruta es '/dashboard'.
watch(() => route.path, (path) => {
  console.log('[App] route changed', path)
  if (path === '/dashboard') {
    checkAndShowOncePerSession()
  }
})

watch(() => signatureNoticeVisible.value, (v) => {
  console.log('[App] signatureNoticeVisible', v)
})
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Reset básico */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #333;
}

/* Pantalla de carga */
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-spinner {
  text-align: center;
  color: white;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  font-size: 16px;
  font-weight: 500;
}
</style>