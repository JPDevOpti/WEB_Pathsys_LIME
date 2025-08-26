<template>
  <div 
    class="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:shadow-sm transition-all duration-200"
    :class="{ 'opacity-60': isEmpty }"
    :title="tooltip"
  >
    <div class="flex items-start gap-3">
      <!-- Icon -->
      <div class="p-2 bg-white rounded-lg shadow-sm">
        <component 
          :is="getIconComponent()" 
          class="w-5 h-5"
          :class="getIconColor()"
        />
      </div>
      
      <!-- Content -->
      <div class="flex-1 min-w-0">
        <p class="text-xs font-medium text-gray-500 mb-1">
          {{ label }}
        </p>
        <p 
          class="text-sm font-semibold truncate"
          :class="getValueColor()"
        >
          {{ value }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  IdentificationIcon,
  UserGroupIcon,
  CheckCircleIcon,
  XCircleIcon,
  AcademicCapIcon,
  DocumentTextIcon,
  CalendarIcon,
  UserCircleIcon,
  BuildingOfficeIcon,
  KeyIcon
} from '@heroicons/vue/24/outline'

interface Props {
  icon: string
  label: string
  value: string
  isEmpty?: boolean
  statusColor?: 'green' | 'red' | 'yellow'
  tooltip?: string
}

const props = withDefaults(defineProps<Props>(), {
  isEmpty: false,
  statusColor: undefined,
  tooltip: undefined
})

const getIconComponent = () => {
  const iconMap: Record<string, any> = {
    user: UserIcon,
    email: EnvelopeIcon,
    phone: PhoneIcon,
    document: IdentificationIcon,
    role: UserGroupIcon,
    status: props.statusColor === 'green' ? CheckCircleIcon : XCircleIcon,
    initials: UserCircleIcon,
    registro: DocumentTextIcon
  }
  return iconMap[props.icon] || UserIcon
}

const getIconColor = () => {
  if (props.isEmpty) return 'text-gray-400'
  
  if (props.icon === 'status') {
    return props.statusColor === 'green' ? 'text-green-500' : 'text-red-500'
  }
  
  const colorMap: Record<string, string> = {
    user: 'text-blue-500',
    email: 'text-purple-500',
    phone: 'text-green-500',
    document: 'text-orange-500',
    role: 'text-indigo-500',
    initials: 'text-violet-500',
    registro: 'text-cyan-500'
  }
  
  return colorMap[props.icon] || 'text-gray-500'
}

const getValueColor = () => {
  if (props.isEmpty) return 'text-gray-400'
  
  if (props.icon === 'status') {
    return props.statusColor === 'green' ? 'text-green-700' : 'text-red-700'
  }
  
  return 'text-gray-900'
}
</script>