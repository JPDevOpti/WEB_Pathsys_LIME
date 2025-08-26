<template>
  <ComponentCard title="Acciones Rápidas" dense>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <ActionButton
        v-for="action in actions"
        :key="action.id"
        :action="action"
        @click="handleActionClick(action)"
      />
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ActionItem } from '../../types/userProfile.types'
import ActionButton from './ActionButton.vue'
import { ComponentCard } from '@/shared/components/common'

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

const handleActionClick = (action: ActionItem) => {
  if (action.isEnabled) {
    action.action()
  }
}
</script>