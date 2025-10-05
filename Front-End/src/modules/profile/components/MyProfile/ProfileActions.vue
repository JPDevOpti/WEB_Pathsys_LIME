<template>
  <ComponentCard title="Acciones Rápidas" dense>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <button
        v-for="action in actions"
        :key="action.id"
        :disabled="!action.isEnabled"
        class="flex items-center p-4 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 text-left"
        :class="getButtonClasses(action)"
        @click="handleActionClick(action)"
      >
        <component 
          :is="getIconComponent(action.icon)" 
          class="w-5 h-5 mr-3 flex-shrink-0"
          :class="getIconClasses(action)"
        />
        <span class="text-sm font-medium truncate" :class="getTextClasses(action)">
          {{ action.label }}
        </span>
      </button>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  PencilIcon,
  KeyIcon,
  BellIcon,
  ArrowDownTrayIcon,
  CogIcon
} from '@heroicons/vue/24/outline'
import type { ActionItem } from '../../types/userProfile.types'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'

interface Props {
  availableActions?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  availableActions: () => ['edit', 'password', 'notifications', 'download']
})

const emit = defineEmits<{
  editProfile: []
  changePassword: []
  configureNotifications: []
  downloadInfo: []
}>()

const allActions: Record<string, ActionItem> = {
  edit: {
    id: 'edit',
    label: 'Editar Perfil',
    icon: 'pencil',
    action: () => emit('editProfile'),
    isEnabled: true,
    variant: 'primary'
  },
  password: {
    id: 'password',
    label: 'Cambiar Contraseña',
    icon: 'key',
    action: () => emit('changePassword'),
    isEnabled: true,
    variant: 'secondary'
  },
  notifications: {
    id: 'notifications',
    label: 'Notificaciones',
    icon: 'bell',
    action: () => emit('configureNotifications'),
    isEnabled: true,
    variant: 'secondary'
  },
  download: {
    id: 'download',
    label: 'Descargar Info',
    icon: 'download',
    action: () => emit('downloadInfo'),
    isEnabled: true,
    variant: 'secondary'
  }
}

const actions = computed(() => {
  return props.availableActions
    .map(actionId => allActions[actionId])
    .filter(Boolean)
})

const getIconComponent = (icon: string) => {
  const iconMap: Record<string, any> = {
    pencil: PencilIcon,
    key: KeyIcon,
    bell: BellIcon,
    download: ArrowDownTrayIcon,
    settings: CogIcon
  }
  return iconMap[icon] || CogIcon
}

const getButtonClasses = (action: ActionItem) => {
  const baseClasses = ''
  
  if (!action.isEnabled) {
    return `${baseClasses} border-gray-200 bg-gray-50 cursor-not-allowed opacity-50`
  }
  
  const variantClasses = {
    primary: 'border-blue-200 bg-blue-50 hover:bg-blue-100 hover:border-blue-300 focus:ring-blue-500',
    secondary: 'border-gray-200 bg-gray-50 hover:bg-gray-100 hover:border-gray-300 focus:ring-gray-500',
    danger: 'border-red-200 bg-red-50 hover:bg-red-100 hover:border-red-300 focus:ring-red-500'
  }
  
  return `${baseClasses} ${variantClasses[action.variant || 'secondary']}`
}

const getIconClasses = (action: ActionItem) => {
  if (!action.isEnabled) {
    return 'text-gray-400'
  }
  
  const variantClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    danger: 'text-red-600'
  }
  
  return variantClasses[action.variant || 'secondary']
}

const getTextClasses = (action: ActionItem) => {
  if (!action.isEnabled) {
    return 'text-gray-400'
  }
  
  const variantClasses = {
    primary: 'text-blue-900',
    secondary: 'text-gray-900',
    danger: 'text-red-900'
  }
  
  return variantClasses[action.variant || 'secondary']
}

const handleActionClick = (action: ActionItem) => {
  if (action.isEnabled) {
    action.action()
  }
}
</script>