<template>
  <transition 
    enter-active-class="transition ease-out duration-300" 
    enter-from-class="opacity-0 transform scale-95" 
    enter-to-class="opacity-100 transform scale-100" 
    leave-active-class="transition ease-in duration-200" 
    leave-from-class="opacity-100 transform scale-100" 
    leave-to-class="opacity-0 transform scale-95"
  >
    <div
      v-if="modelValue"
      :class="[
        'fixed right-0 bottom-0 z-[9999] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/40',
        // Offset por header
        'top-16', // ~64px
        // Offset por sidebar en desktop
        overlayLeftClass
      ]"
      @click.self="handleClose"
    >
      <div 
        :class="[
          'relative bg-white w-full rounded-t-2xl sm:rounded-2xl shadow-2xl flex flex-col',
          sizeClass
        ]"
      >
        <!-- Header -->
        <div 
          v-if="showHeader"
          class="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl flex items-center justify-between"
        >
          <div class="flex items-center gap-3">
            <component 
              v-if="icon" 
              :is="icon" 
              :class="['w-5 h-5', iconClass]"
            />
            <h3 class="text-xl font-semibold text-gray-900">{{ title }}</h3>
          </div>
          <button 
            @click="handleClose" 
            class="text-gray-400 hover:text-gray-600 transition-colors"
            :aria-label="closeAriaLabel"
          >
            ✕
          </button>
        </div>

        <!-- Content -->
        <div 
          :class="[
            'flex-1 overflow-y-auto overflow-x-hidden',
            contentPaddingClass
          ]"
        >
          <slot />
        </div>

        <!-- Footer -->
        <div 
          v-if="$slots.footer"
          class="bg-gray-50 border-t border-gray-200 px-6 py-4 rounded-b-2xl"
        >
          <slot name="footer" />
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSidebar } from '@/shared/composables/SidebarControl'

interface Props {
  modelValue: boolean
  title?: string
  icon?: any
  iconClass?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showHeader?: boolean
  closeAriaLabel?: string
  contentPadding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Modal',
  icon: null,
  iconClass: 'text-blue-500',
  size: 'lg',
  showHeader: true,
  closeAriaLabel: 'Cerrar modal',
  contentPadding: 'md'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}>()

// Ajuste responsivo: respetar ancho del sidebar (colapsado/expandido) y su hover
const { isExpanded, isMobileOpen, isHovered } = useSidebar()

// En desktop (>= lg), cuando el sidebar está expandido u hovered, dejamos margen izquierdo ~18rem (w-72)
// Cuando está colapsado, dejamos ~5rem (w-20)
// En móvil, sidebar es overlay, así que sin margen (left: 0)
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const sizeClass = computed(() => {
  const sizeMap = {
    sm: 'max-w-sm h-[50vh]',
    md: 'max-w-md h-[60vh]',
    lg: 'max-w-4xl h-[75vh]',
    xl: 'max-w-6xl h-[80vh]',
    full: 'max-w-full h-[85vh]'
  }
  return sizeMap[props.size]
})

const contentPaddingClass = computed(() => {
  const paddingMap = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }
  return paddingMap[props.contentPadding]
})

const handleClose = () => {
  emit('update:modelValue', false)
  emit('close')
}
</script>
