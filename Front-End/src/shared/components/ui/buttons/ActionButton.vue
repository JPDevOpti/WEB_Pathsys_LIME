<template>
  <BaseButton
    :variant="variant"
    :size="size"
    :type="type"
    :disabled="disabled"
    :loading="loading"
    :loading-text="loadingText"
    :text="text"
    :icon="icon"
    :class="class"
    @click="handleAction"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseButton from './BaseButton.vue'

export interface ActionButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  text?: string
  icon?: any
  class?: string
  confirmAction?: boolean
  confirmMessage?: string
  confirmTitle?: string
}

const props = withDefaults(defineProps<ActionButtonProps>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  disabled: false,
  loading: false,
  loadingText: 'Cargando...',
  text: '',
  class: '',
  confirmAction: false,
  confirmMessage: '¿Está seguro que desea realizar esta acción?',
  confirmTitle: 'Confirmar Acción'
})

const emit = defineEmits<{
  action: [event: MouseEvent]
  confirm: [event: MouseEvent]
}>()

const handleAction = (event: MouseEvent) => {
  if (props.confirmAction) {
    // Aquí podrías implementar un modal de confirmación
    // Por ahora solo emitimos el evento de confirmación
    emit('confirm', event)
  } else {
    emit('action', event)
  }
}
</script> 