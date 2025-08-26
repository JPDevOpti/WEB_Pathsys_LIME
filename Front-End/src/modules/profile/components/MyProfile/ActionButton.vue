<template>
  <button
    :disabled="!action.isEnabled"
    class="flex items-center p-4 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2"
    :class="getButtonClasses()"
    @click="$emit('click')"
  >
    <component 
      :is="getIconComponent()" 
      class="w-5 h-5 mr-3 flex-shrink-0"
      :class="getIconClasses()"
    />
    <span class="text-sm font-medium truncate" :class="getTextClasses()">
      {{ action.label }}
    </span>
  </button>
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

interface Props {
  action: ActionItem
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: []
}>()

const getIconComponent = () => {
  const iconMap: Record<string, any> = {
    pencil: PencilIcon,
    key: KeyIcon,
    bell: BellIcon,
    download: ArrowDownTrayIcon,
    settings: CogIcon
  }
  return iconMap[props.action.icon] || CogIcon
}

const getButtonClasses = () => {
  const baseClasses = 'text-left'
  
  if (!props.action.isEnabled) {
    return `${baseClasses} border-gray-200 bg-gray-50 cursor-not-allowed opacity-50`
  }
  
  const variantClasses = {
    primary: 'border-blue-200 bg-blue-50 hover:bg-blue-100 hover:border-blue-300 focus:ring-blue-500',
    secondary: 'border-gray-200 bg-gray-50 hover:bg-gray-100 hover:border-gray-300 focus:ring-gray-500',
    danger: 'border-red-200 bg-red-50 hover:bg-red-100 hover:border-red-300 focus:ring-red-500'
  }
  
  return `${baseClasses} ${variantClasses[props.action.variant || 'secondary']}`
}

const getIconClasses = () => {
  if (!props.action.isEnabled) {
    return 'text-gray-400'
  }
  
  const variantClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    danger: 'text-red-600'
  }
  
  return variantClasses[props.action.variant || 'secondary']
}

const getTextClasses = () => {
  if (!props.action.isEnabled) {
    return 'text-gray-400'
  }
  
  const variantClasses = {
    primary: 'text-blue-900',
    secondary: 'text-gray-900',
    danger: 'text-red-900'
  }
  
  return variantClasses[props.action.variant || 'secondary']
}
</script>