<template>
  <form @submit.prevent="onSubmit" class="space-y-6">
    <!-- Patólogo Form -->
    <div v-if="user.role === 'patologo'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="md:col-span-2">
        <h4 class="text-lg font-medium text-gray-900 mb-1">Editar Patólogo</h4>
        <p class="text-sm text-gray-500">Modifica los datos del patólogo</p>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre completo *</label>
        <input v-model="patologoForm.patologoName" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Iniciales</label>
        <input v-model="patologoForm.InicialesPatologo" type="text" maxlength="10" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="off" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
        <input v-model="patologoForm.PatologoEmail" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="email" name="email" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Registro médico *</label>
        <input v-model="patologoForm.registro_medico" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="off" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
        <textarea v-model="patologoForm.observaciones" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña (opcional)</label>
        <input v-model="patologoForm.password" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="new-password" name="new-password" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña</label>
        <input v-model="patologoForm.passwordConfirm" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="new-password" name="confirm-password" />
      </div>
    </div>

    <!-- Residente Form -->
    <div v-else-if="user.role === 'residente'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="md:col-span-2">
        <h4 class="text-lg font-medium text-gray-900 mb-1">Editar Residente</h4>
        <p class="text-sm text-gray-500">Modifica los datos del residente</p>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre completo *</label>
        <input v-model="residenteForm.residenteName" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Iniciales</label>
        <input v-model="residenteForm.InicialesResidente" type="text" maxlength="10" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="off" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
        <input v-model="residenteForm.ResidenteEmail" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="email" name="email" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Registro médico *</label>
        <input v-model="residenteForm.registro_medico" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="off" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
        <textarea v-model="residenteForm.observaciones" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña (opcional)</label>
        <input v-model="residenteForm.password" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="new-password" name="new-password" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña</label>
        <input v-model="residenteForm.passwordConfirm" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="new-password" name="confirm-password" />
      </div>
    </div>

    <!-- Auxiliar Form -->
    <div v-else-if="user.role === 'auxiliar'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="md:col-span-2">
        <h4 class="text-lg font-medium text-gray-900 mb-1">Editar Auxiliar</h4>
        <p class="text-sm text-gray-500">Modifica los datos del auxiliar</p>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre completo *</label>
        <input v-model="auxiliarForm.auxiliarName" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
        <input v-model="auxiliarForm.AuxiliarEmail" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="email" name="email" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
        <textarea v-model="auxiliarForm.observaciones" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña (opcional)</label>
        <input v-model="auxiliarForm.password" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="new-password" name="new-password" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña</label>
        <input v-model="auxiliarForm.passwordConfirm" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="new-password" name="confirm-password" />
      </div>
    </div>

    <!-- Facturación Form -->
    <div v-else-if="user.role === 'facturacion'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="md:col-span-2">
        <h4 class="text-lg font-medium text-gray-900 mb-1">Editar Usuario de Facturación</h4>
        <p class="text-sm text-gray-500">Modifica los datos del usuario de facturación</p>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre completo *</label>
        <input v-model="facturacionForm.facturacionName" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
        <input v-model="facturacionForm.FacturacionEmail" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="email" name="email" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
        <textarea v-model="facturacionForm.observaciones" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña (opcional)</label>
        <input v-model="facturacionForm.password" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="new-password" name="new-password" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña</label>
        <input v-model="facturacionForm.passwordConfirm" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="new-password" name="confirm-password" />
      </div>
    </div>

    <!-- Admin Form -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="md:col-span-2">
        <h4 class="text-lg font-medium text-gray-900 mb-1">Editar Perfil</h4>
        <p class="text-sm text-gray-500">Modifica tus datos básicos</p>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
        <input v-model="adminForm.firstName" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Apellido *</label>
        <input v-model="adminForm.lastName" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
        <input v-model="adminForm.email" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" autocomplete="email" name="email" />
      </div>
    </div>

    <!-- Form Actions -->
    <div class="flex flex-col sm:flex-row gap-3 pt-6 border-t border-gray-200">
      <button
        type="submit"
        :disabled="isLoading || !hasChanges"
        class="flex-1 sm:flex-none sm:order-2 inline-flex items-center justify-center px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <span v-if="!isLoading">Guardar Cambios</span>
        <span v-else class="flex items-center gap-2">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Guardando...
        </span>
      </button>
      
      <button
        type="button"
        @click="$emit('cancel')"
        :disabled="isLoading"
        class="flex-1 sm:flex-none sm:order-1 inline-flex items-center justify-center px-6 py-2 bg-white text-gray-700 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Cancelar
      </button>
    </div>

    <!-- Unsaved Changes Warning -->
    <div v-if="hasChanges && !isLoading" class="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
      <ExclamationTriangleIcon class="w-5 h-5 text-amber-600 flex-shrink-0" />
      <p class="text-sm text-amber-800">
        Tienes cambios sin guardar. Asegúrate de guardar antes de cerrar.
      </p>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import type { UserProfile, ProfileEditPayload } from '../../types/userProfile.types'

interface Props {
  user: UserProfile
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), { isLoading: false })
const emit = defineEmits<{ submit: [payload: ProfileEditPayload]; cancel: []; change: [hasChanges: boolean] }>()

const adminForm = reactive({
  firstName: props.user.firstName,
  lastName: props.user.lastName,
  email: props.user.email
})

const patologoForm = reactive({
  patologoName: `${props.user.firstName} ${props.user.lastName}`.trim(),
  InicialesPatologo: props.user.roleSpecificData?.iniciales || '',
  PatologoEmail: props.user.email,
  registro_medico: props.user.roleSpecificData?.registroMedico || '',
  password: '',
  passwordConfirm: '',
  observaciones: props.user.roleSpecificData?.observaciones || ''
})

const residenteForm = reactive({
  residenteName: `${props.user.firstName} ${props.user.lastName}`.trim(),
  InicialesResidente: props.user.roleSpecificData?.iniciales || '',
  ResidenteEmail: props.user.email,
  registro_medico: props.user.roleSpecificData?.registroMedico || '',
  password: '',
  passwordConfirm: '',
  observaciones: props.user.roleSpecificData?.observaciones || ''
})

const auxiliarForm = reactive({
  auxiliarName: `${props.user.firstName} ${props.user.lastName}`.trim(),
  AuxiliarEmail: props.user.email,
  password: '',
  passwordConfirm: '',
  observaciones: props.user.roleSpecificData?.observaciones || ''
})

const facturacionForm = reactive({
  facturacionName: `${props.user.firstName} ${props.user.lastName}`.trim(),
  FacturacionEmail: props.user.email,
  password: '',
  passwordConfirm: '',
  observaciones: props.user.roleSpecificData?.observaciones || ''
})

const originalState = JSON.stringify({ adminForm, patologoForm, residenteForm, auxiliarForm, facturacionForm })

const hasChanges = computed(() => JSON.stringify({ adminForm, patologoForm, residenteForm, auxiliarForm, facturacionForm }) !== originalState)

const isLoading = computed(() => props.isLoading)

const validatePasswords = (password: string, passwordConfirm: string): boolean => {
  // If password is empty, no validation needed
  if (!password || !password.trim()) {
    return true
  }
  
  if (password.length < 6) {
    alert('La contraseña debe tener al menos 6 caracteres')
    return false
  }
  if (password !== passwordConfirm) {
    alert('Las contraseñas no coinciden')
    return false
  }
  return true
}

const onSubmit = () => {
  let payload: ProfileEditPayload
  
  if (props.user.role === 'patologo') {
    if (!validatePasswords(patologoForm.password, patologoForm.passwordConfirm)) return
    payload = { role: 'patologo', ...patologoForm }
  } else if (props.user.role === 'residente') {
    if (!validatePasswords(residenteForm.password, residenteForm.passwordConfirm)) return
    payload = { role: 'residente', ...residenteForm }
  } else if (props.user.role === 'auxiliar') {
    if (!validatePasswords(auxiliarForm.password, auxiliarForm.passwordConfirm)) return
    payload = { role: 'auxiliar', ...auxiliarForm, auxiliarCode: '' }
  } else if (props.user.role === 'facturacion') {
    if (!validatePasswords(facturacionForm.password, facturacionForm.passwordConfirm)) return
    payload = { role: 'facturacion', ...facturacionForm, facturacionCode: (props.user.roleSpecificData as any)?.facturacionCode || (props.user.roleSpecificData as any)?.billingCode || '' }
  } else {
    payload = { role: 'admin', ...adminForm }
  }
  emit('submit', payload)
}
</script>