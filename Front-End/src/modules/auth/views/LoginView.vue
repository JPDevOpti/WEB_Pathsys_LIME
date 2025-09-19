<!--
  Componente LoginView
  Vista de inicio de sesión que permite a los usuarios acceder al sistema.
  
  Características:
  - Formulario de inicio de sesión con validación de email
  - Toggle de visibilidad de contraseña
  - Opción de mantener sesión iniciada
  - Estado de carga durante el envío
  - Diseño responsive
  - Animaciones y transiciones suaves
  - Validación visual de campos
-->
<template>
  <FullScreenLayout>
    <!-- Fondo blanco fijo -->
    <div class="fixed inset-0 z-0 bg-white"></div>
    <!-- Contenedor principal con fondo y centrado -->
    <div class="relative min-h-screen p-6 z-10 flex flex-col items-center justify-center">
      <!-- Sección de logos y navegación -->
      <div class="w-full max-w-md mx-auto mb-8 text-center">
        <!-- Contenedor de logos con animación al hover -->
        <div class="flex justify-center items-center gap-8 mb-8">
          <router-link to="/" class="inline-block transition-transform duration-300 hover:scale-105">
            <img src="@/assets/images/Baner_HAMA.png" alt="Logo HAMA" class="w-56 h-auto mx-auto" />
          </router-link>
          <router-link to="/" class="inline-block transition-transform duration-300 hover:scale-105">
            <img src="@/assets/images/Logo-LIME-NoFondo.png" alt="Logo LIME" class="w-44 h-auto mx-auto rounded-md" />
          </router-link>
          <router-link to="/" class="inline-block transition-transform duration-300 hover:scale-105">
            <img src="@/assets/images/Banner_UDEA.png" alt="Logo UDEA" class="w-44 h-auto mx-auto rounded-md" />
          </router-link>
        </div>
      </div>

      <!-- Contenedor del formulario con efecto glassmorphism y animación -->
      <div class="w-full max-w-md mx-auto bg-white/90 rounded-3xl shadow-3xl p-10 backdrop-blur-md border border-white/40 animate-fadeInUp transition-shadow duration-300 hover:shadow-4xl">
        <!-- Encabezado del formulario -->
        <div class="mb-10 text-center">
          <h1
            class="mb-2 font-extrabold text-gray-800 text-3xl sm:text-4xl tracking-tight drop-shadow-sm"
          >
            Sign In
          </h1>
          <p class="text-base text-gray-500 font-normal">
            Enter your email and password to sign in!
          </p>
        </div>

        <!-- Formulario de inicio de sesión -->
        <form @submit.prevent="onSubmit">
          <div class="space-y-7">
            <!-- Campo de email -->
            <EmailInput v-model="email" />

            <!-- Campo de contraseña -->
            <PasswordInput v-model="password" />

            <!-- Opciones adicionales -->
            <div class="flex items-center mt-2">
              <RememberMeCheckbox v-model="rememberMe" />
            </div>

            <!-- Mensaje de error -->
            <div v-if="error" class="text-center">
              <ErrorMessage :message="error" />
            </div>

            <!-- Botón de envío -->
            <div class="pt-2">
              <FormButton
                type="submit"
                text="Sign In"
                loading-text="Signing in..."
                :loading="isLoading"
                :disabled="!isFormValid"
                icon="ArrowRightIcon"
              />
            </div>
          </div>
        </form>
      </div>
    </div>
  </FullScreenLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FullScreenLayout from '@/shared/layouts/FullScreenLayout.vue'
import EmailInput from '../components/EmailInput.vue'
import PasswordInput from '../components/PasswordInput.vue'
import RememberMeCheckbox from '../components/RememberMeCheckbox.vue'
import { FormButton } from '@/shared/components/forms'
import { ErrorMessage } from '@/shared/components/feedback'
import { useLoginForm } from '../composables/useLoginForm'

// Icono para el botón
const ArrowRightIcon = {
  template: `
    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/>
    </svg>
  `
}

const router = useRouter()

// Usar el composable del formulario
const {
  email,
  password,
  rememberMe,
  isLoading,
  error,
  isFormValid,
  handleSubmit,
  resetForm,
  loadSavedData,
  saveData
} = useLoginForm()

// Manejar el envío del formulario
const onSubmit = async () => {
  const success = await handleSubmit()
  if (success) {
    // Guardar datos si se solicita
    saveData()
    // Redirigir al dashboard
    router.push('/dashboard')
  }
}

// Cargar datos guardados al montar el componente
onMounted(() => {
  loadSavedData()
})
</script>

<style scoped>
/* Animación de entrada suave para elementos */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}

/* Animación de entrada hacia arriba para la tarjeta */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
.animate-fadeInUp {
  animation: fadeInUp 0.6s cubic-bezier(0.23, 1, 0.32, 1);
}

.shadow-3xl {
  box-shadow: 0 8px 32px 0 rgba(60, 60, 90, 0.18), 0 1.5px 6px 0 rgba(60,60,90,0.10);
}
.shadow-4xl {
  box-shadow: 0 16px 48px 0 rgba(60, 60, 90, 0.22), 0 2px 8px 0 rgba(60,60,90,0.12);
}
.rounded-3xl {
  border-radius: 2rem;
}
</style>