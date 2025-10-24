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
    <div class="fixed inset-0 z-0 bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50"></div>
    <div class="fixed inset-0 z-0 bg-pattern opacity-5"></div>
    
    <div class="relative min-h-screen p-4 sm:p-6 z-10 flex flex-col items-center justify-center">
      <div class="absolute top-0 left-0 w-96 h-96 bg-emerald-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div class="absolute top-0 right-0 w-96 h-96 bg-teal-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div class="absolute bottom-0 left-1/2 w-96 h-96 bg-cyan-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
      
      <div class="w-full max-w-6xl mx-auto mb-6 sm:mb-10 text-center relative z-20 animate-fadeIn">
        <div class="flex flex-wrap justify-center items-center gap-4 sm:gap-8 lg:gap-13">
          <div class="flex items-center gap-1 sm:gap-2">
            <router-link to="/" class="inline-block transition-all duration-500 hover:scale-110 hover:-translate-y-2">
              <img src="@/assets/images/Banner_HAMA.png" alt="Logo HAMA" class="w-40 sm:w-48 lg:w-64 h-auto mx-auto filter drop-shadow-xl" />
            </router-link>
            <router-link to="/" class="inline-block transition-all duration-500 hover:scale-110 hover:-translate-y-2 flex justify-center">
              <img src="@/assets/images/Logo-LIME-NoFondo.png" alt="Logo LIME" class="w-24 sm:w-28 lg:w-32 h-auto rounded-xl filter drop-shadow-xl" />
            </router-link>
          </div>
          <router-link to="/" class="inline-block transition-all duration-500 hover:scale-110 hover:-translate-y-2">
            <img src="@/assets/images/Banner_UDEA.png" alt="Logo UDEA" class="w-32 sm:w-40 lg:w-52 h-auto mx-auto rounded-xl filter drop-shadow-xl" />
          </router-link>
        </div>
      </div>

      <div class="w-full max-w-md mx-auto bg-white rounded-3xl shadow-2xl p-8 sm:p-12 border border-gray-100 animate-fadeInUp transition-all duration-500 hover:shadow-3xl relative z-20 overflow-hidden">
        <div class="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-full filter blur-3xl opacity-30 -mr-20 -mt-20"></div>
        <div class="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-cyan-100 to-teal-100 rounded-full filter blur-3xl opacity-30 -ml-16 -mb-16"></div>
        
        <div class="relative z-10">
          <div class="mb-8 sm:mb-10 text-center">
            <h1 class="mb-3 font-bold text-gray-800 text-2xl sm:text-3xl lg:text-4xl tracking-tight">
              Bienvenido de nuevo
            </h1>
            <p class="text-sm sm:text-base text-gray-600 font-medium">
              Ingrese sus credenciales para acceder al sistema
            </p>
          </div>

          <form @submit.prevent="onSubmit">
            <div class="space-y-5 sm:space-y-6">
              <EmailInput v-model="email" />
              <PasswordInput v-model="password" />
              
              <div class="flex items-center justify-between mt-2">
                <RememberMeCheckbox v-model="rememberMe" />
              </div>

              <div v-if="error" class="text-center animate-shake">
                <ErrorMessage :message="error" />
              </div>

              <div class="pt-2 sm:pt-4">
                <FormButton
                  type="submit"
                  text="Ingresar"
                  loading-text="Ingresando..."
                  :loading="isLoading"
                  :disabled="!isFormValid || isLoading"
                  :icon="LoginIcon"
                />
              </div>
            </div>
          </form>
        </div>
      </div>

      <div class="mt-6 sm:mt-8 text-center text-xs sm:text-sm text-gray-600 relative z-20 animate-fadeIn animation-delay-500">
        <p>© 2025 PathSys LIME - Sistema de Gestión de Patología</p>
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
import { FormButton } from '@/shared/components/ui/forms'
import { ErrorMessage } from '@/shared/components/ui/feedback'
import { useLoginForm } from '../composables/useLoginForm'
import { LoginIcon } from '@/assets/icons'

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
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(60px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.animate-fadeInUp {
  animation: fadeInUp 0.8s cubic-bezier(0.23, 1, 0.32, 1);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(3deg);
  }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

@keyframes blob {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(20px, -50px) scale(1.1);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  75% {
    transform: translate(50px, 50px) scale(1.05);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10px);
  }
  75% {
    transform: translateX(10px);
  }
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

.animation-delay-500 {
  animation-delay: 0.5s;
}

.bg-pattern {
  background-image: radial-gradient(circle at 1px 1px, rgba(16, 185, 129, 0.15) 1px, transparent 0);
  background-size: 40px 40px;
}

.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
}

.shadow-3xl {
  box-shadow: 0 35px 60px -15px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 0, 0, 0.05);
}

@media (max-width: 640px) {
  .bg-pattern {
    background-size: 30px 30px;
  }
}
</style>