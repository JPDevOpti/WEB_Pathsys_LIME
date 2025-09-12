<template>
  <form @submit.prevent="onSubmit" class="space-y-6">
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
        <input v-model="patologoForm.InicialesPatologo" type="text" maxlength="10" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
        <input v-model="patologoForm.PatologoEmail" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Registro médico *</label>
        <input v-model="patologoForm.registro_medico" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
        <textarea v-model="patologoForm.observaciones" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña (opcional)</label>
        <input v-model="patologoForm.password" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
    </div>

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
        <input v-model="residenteForm.InicialesResidente" type="text" maxlength="10" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
        <input v-model="residenteForm.ResidenteEmail" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Registro médico *</label>
        <input v-model="residenteForm.registro_medico" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
        <textarea v-model="residenteForm.observaciones" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña (opcional)</label>
        <input v-model="residenteForm.password" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
    </div>

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
        <input v-model="auxiliarForm.AuxiliarEmail" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
        <textarea v-model="auxiliarForm.observaciones" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña (opcional)</label>
        <input v-model="auxiliarForm.password" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
    </div>

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
        <input v-model="facturacionForm.FacturacionEmail" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
        <textarea v-model="facturacionForm.observaciones" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña (opcional)</label>
        <input v-model="facturacionForm.password" type="password" placeholder="••••••••" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
    </div>

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
        <input v-model="adminForm.email" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
    </div>

    <div class="flex flex-col sm:flex-row gap-3 pt-6 border-t border-gray-200">
      <button type="submit" :disabled="isLoading || !hasChanges" class="flex-1 sm:flex-none sm:order-2 inline-flex items-center justify-center px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed">
        Guardar Cambios
      </button>
      <button type="button" @click="$emit('cancel')" :disabled="isLoading" class="flex-1 sm:flex-none sm:order-1 inline-flex items-center justify-center px-6 py-2 bg-white text-gray-700 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed">
        Cancelar
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
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
  observaciones: props.user.roleSpecificData?.observaciones || ''
})

const residenteForm = reactive({
  residenteName: `${props.user.firstName} ${props.user.lastName}`.trim(),
  InicialesResidente: props.user.roleSpecificData?.iniciales || '',
  ResidenteEmail: props.user.email,
  registro_medico: props.user.roleSpecificData?.registroMedico || '',
  password: '',
  observaciones: props.user.roleSpecificData?.observaciones || ''
})

const auxiliarForm = reactive({
  auxiliarName: `${props.user.firstName} ${props.user.lastName}`.trim(),
  AuxiliarEmail: props.user.email,
  password: '',
  observaciones: props.user.roleSpecificData?.observaciones || ''
})

const facturacionForm = reactive({
  facturacionName: `${props.user.firstName} ${props.user.lastName}`.trim(),
  FacturacionEmail: props.user.email,
  password: '',
  observaciones: props.user.roleSpecificData?.observaciones || ''
})

const originalState = JSON.stringify({ adminForm, patologoForm, residenteForm, auxiliarForm, facturacionForm })

const hasChanges = computed(() => JSON.stringify({ adminForm, patologoForm, residenteForm, auxiliarForm, facturacionForm }) !== originalState)

const isLoading = computed(() => props.isLoading)

const onSubmit = () => {
  let payload: ProfileEditPayload
  if (props.user.role === 'patologo') {
    payload = { role: 'patologo', ...patologoForm }
  } else if (props.user.role === 'residente') {
    payload = { role: 'residente', ...residenteForm }
  } else if (props.user.role === 'auxiliar') {
    payload = { role: 'auxiliar', ...auxiliarForm, auxiliarCode: '' }
  } else if (props.user.role === 'facturacion') {
    payload = { role: 'facturacion', ...facturacionForm, facturacionCode: '' }
  } else {
    payload = { role: 'admin', ...adminForm }
  }
  emit('submit', payload)
}
</script>


