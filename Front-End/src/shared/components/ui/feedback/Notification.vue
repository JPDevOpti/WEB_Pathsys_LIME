<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="transform scale-95 opacity-0"
    enter-to-class="transform scale-100 opacity-100"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="transform scale-100 opacity-100"
    leave-to-class="transform scale-95 opacity-0"
  >
    <div
      v-if="visible"
      :class="[
        inline 
          ? 'w-full rounded-xl shadow-xl border-l-4 mt-4 relative' 
          : containerPositionClasses,
        notificationClasses
      ]"
    >
      <!-- Botón cerrar - posición absoluta en esquina superior derecha -->
      <button
        @click="$emit('close')"
        :class="closeButtonClasses"
        title="Cerrar notificación"
        class="absolute top-2 right-2 z-10"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div class="flex items-start space-x-3 p-6 pr-10">
        <!-- Ícono con fondo circular - más pequeño -->
        <div class="flex-shrink-0">
          <div :class="iconContainerClasses">
            <!-- Ícono personalizado o por tipo -->
            <component v-if="customIcon" :is="customIcon" :class="customIconClasses" />
            <template v-else>
              <!-- Success -->
              <svg v-if="type === 'success'" :class="iconClasses" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Error -->
              <svg v-else-if="type === 'error'" :class="iconClasses" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Warning -->
              <svg v-else-if="type === 'warning'" :class="iconClasses" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <!-- Info -->
              <svg v-else :class="iconClasses" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </template>
          </div>
        </div>
        
        <div class="flex-1 min-w-0">
          <div class="w-full">
            <!-- Título -->
            <h4 :class="titleClasses">
              {{ title }}
            </h4>
            
            <!-- Mensaje -->
            <p :class="messageClasses">
              {{ message }}
            </p>
            
            <!-- Timestamp -->
            <div v-if="inline" :class="timestampClasses">
              <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ formattedTime }}
            </div>
          </div>
          
          <!-- Slot para contenido adicional - ocupa todo el ancho disponible -->
          <div v-if="$slots.content" class="mt-3 w-full">
            <slot name="content" />
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from 'vue'

type NotificationType = 'success' | 'error' | 'warning' | 'info'

interface Props {
  visible: boolean
  type: NotificationType
  title: string
  message: string
  autoClose?: boolean
  autoCloseDuration?: number
  inline?: boolean
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'center'
  customIcon?: any
  iconSize?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  autoClose: true,
  autoCloseDuration: 5000,
  inline: false,
  position: 'top-right',
  customIcon: undefined,
  iconSize: 'md'
})

const emit = defineEmits<{
  'close': []
}>()

let autoCloseTimer: NodeJS.Timeout | null = null

const setupAutoClose = () => {
  if (props.autoClose && props.visible) {
    autoCloseTimer = setTimeout(() => {
      emit('close')
    }, props.autoCloseDuration)
  }
}

const clearAutoClose = () => {
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer)
    autoCloseTimer = null
  }
}

// Watcher para manejar cambios en la visibilidad
watch(() => props.visible, (newVisible) => {
  clearAutoClose()
  if (newVisible) {
    setupAutoClose()
  }
})

onMounted(() => {
  if (props.visible) {
    setupAutoClose()
  }
})

onUnmounted(() => {
  clearAutoClose()
})

const notificationClasses = computed(() => {
  const classes = {
    success: 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-500',
    error: 'bg-gradient-to-r from-red-50 to-red-100 border-red-500',
    warning: 'bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-500',
    info: 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-500'
  }
  return classes[props.type]
})

const containerPositionClasses = computed(() => {
  const base = 'fixed max-w-md w-full shadow-lg rounded-lg p-4 z-50 relative'
  const map: Record<string, string> = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'center': 'inset-0 m-auto max-w-sm'
  }
  return `${base} ${map[props.position!]}`
})

const iconContainerClasses = computed(() => {
  const size = props.iconSize === 'lg' ? 'w-10 h-10' : props.iconSize === 'sm' ? 'w-7 h-7' : 'w-8 h-8'
  const base = `flex items-center justify-center ${size} rounded-full`
  const classes = {
    success: 'bg-green-100',
    error: 'bg-red-100',
    warning: 'bg-amber-100',
    info: 'bg-blue-100'
  }
  return `${base} ${classes[props.type]}`
})

const iconClasses = computed(() => {
  const size = props.iconSize === 'lg' ? 'w-5 h-5' : props.iconSize === 'sm' ? 'w-4 h-4' : 'w-4 h-4'
  const classes = {
    success: `${size} text-green-600`,
    error: `${size} text-red-600`,
    warning: `${size} text-amber-600`,
    info: `${size} text-blue-600`
  }
  return classes[props.type]
})

const customIconClasses = computed(() => {
  return props.iconSize === 'lg' ? 'w-5 h-5 text-current' : props.iconSize === 'sm' ? 'w-4 h-4 text-current' : 'w-4 h-4 text-current'
})

const titleClasses = computed(() => {
  const classes = {
    success: 'text-lg font-semibold text-green-800 mb-1',
    error: 'text-lg font-semibold text-red-800 mb-1',
    warning: 'text-lg font-semibold text-amber-800 mb-1',
    info: 'text-lg font-semibold text-blue-800 mb-1'
  }
  return classes[props.type]
})

const messageClasses = computed(() => {
  const classes = {
    success: 'text-sm text-green-700 mb-2',
    error: 'text-sm text-red-700 mb-2',
    warning: 'text-sm text-amber-700 mb-2',
    info: 'text-sm text-blue-700 mb-2'
  }
  return classes[props.type]
})

const timestampClasses = computed(() => {
  const base = 'flex items-center text-xs mb-3'
  const classes = {
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-amber-600',
    info: 'text-blue-600'
  }
  return `${base} ${classes[props.type]}`
})

const closeButtonClasses = computed(() => {
  const base = 'flex-shrink-0 transition-colors p-1 rounded-full'
  const classes = {
    success: 'text-green-400 hover:text-green-600 hover:bg-green-100',
    error: 'text-red-400 hover:text-red-600 hover:bg-red-100',
    warning: 'text-amber-400 hover:text-amber-600 hover:bg-amber-100',
    info: 'text-blue-400 hover:text-blue-600 hover:bg-blue-100'
  }
  return `${base} ${classes[props.type]}`
})

const formattedTime = computed(() => {
  try {
    return new Date().toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return new Date().toLocaleTimeString()
  }
})
</script>
