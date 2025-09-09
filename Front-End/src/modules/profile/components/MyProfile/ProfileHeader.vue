<template>
  <ComponentCard :hide-header="true" customClass="mb-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
      <!-- User Info Section -->
      <div class="flex flex-col sm:flex-row sm:items-center gap-4">
        <!-- Avatar -->
        <div class="relative w-24 h-24 sm:w-28 sm:h-28 mx-auto sm:mx-0">
          <div
            class="w-full h-full rounded-full overflow-hidden border-2 border-blue-200 shadow-lg group"
            :class="{ 'hover:border-blue-300': isEditable }"
          >
            <div class="w-full h-full bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center text-gray-700">
              <component :is="getRoleIcon(normalizedRole)" class="w-[86%] h-[86%]" />
            </div>
          </div>
          
          <!-- Status Indicator -->
          <div 
            class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full border-2 border-white shadow-sm"
            :class="user.isActive ? 'bg-green-500' : 'bg-gray-400'"
            :title="user.isActive ? 'Usuario activo' : 'Usuario inactivo'"
          ></div>
        </div>

        <!-- User Details -->
        <div class="text-center sm:text-left">
          <h2 class="text-2xl font-bold text-gray-900 mb-1">
            {{ user.firstName }} {{ user.lastName }}
          </h2>

          <p class="text-sm text-gray-600">
            {{ user.email }}
          </p>

          <div class="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
            <span 
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
              :class="getRoleStyles(normalizedRole)"
            >
              {{ getRoleLabel(normalizedRole) }}
            </span>
          </div>

          <p v-if="user.lastLogin" class="text-xs text-gray-500 mt-1">
            Último acceso: {{ formatLastLogin(user.lastLogin) }}
          </p>
        </div>
      </div>

      <!-- Edit Button -->
      <div v-if="isEditable" class="flex justify-center sm:justify-end">
        <button
          @click="$emit('edit')"
          class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200"
        >
          <PencilIcon class="w-4 h-4" />
          Editar perfil
        </button>
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { PencilIcon } from '@heroicons/vue/24/outline'
import type { UserProfile, UserRole } from '../../types/userProfile.types'
import { ComponentCard } from '@/shared/components/common'

interface Props {
  user: UserProfile
  isEditable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isEditable: true
})

defineEmits<{ edit: [] }>()

// Normalización defensiva del rol para evitar mostrar etiquetas incorrectas
const normalizeRole = (role: string): UserRole => {
  const r = String(role || '').toLowerCase()
  if ([ 'admin', 'administrator' ].includes(r)) return 'admin'
  if ([ 'patologo', 'pathologist', 'patólogo' ].includes(r)) return 'patologo'
  if ([ 'residente', 'resident' ].includes(r)) return 'residente'
  if ([ 'auxiliar', 'assistant', 'auxiliary' ].includes(r)) return 'auxiliar'
  return 'auxiliar'
}
import { computed } from 'vue'
const normalizedRole = computed(() => normalizeRole((props as any).user?.role))

const getRoleLabel = (role: UserRole): string => {
  const roleLabels: Record<UserRole, string> = {
    admin: 'Administrador',
    patologo: 'Patólogo',
    residente: 'Residente',
    auxiliar: 'Auxiliar'
  }
  return roleLabels[role]
}

const getRoleStyles = (role: UserRole): string => {
  const roleStyles: Record<UserRole, string> = {
    admin: 'bg-purple-100 text-purple-800',
    patologo: 'bg-blue-100 text-blue-800',
    residente: 'bg-green-100 text-green-800',
    auxiliar: 'bg-gray-100 text-gray-800'
  }
  return roleStyles[role]
}

const formatLastLogin = (date: Date): string => {
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date))
}

import { SettingsIcon, DoctorIcon, ResidenteIcon, AuxiliarIcon, MailBox } from '@/assets/icons'

const getRoleIcon = (role: UserRole) => {
  const roleIconMap: Record<UserRole, any> = {
    admin: SettingsIcon,
    patologo: DoctorIcon,
    residente: ResidenteIcon,
    auxiliar: AuxiliarIcon
  }
  return roleIconMap[role] || UserCircleIcon
}
</script>