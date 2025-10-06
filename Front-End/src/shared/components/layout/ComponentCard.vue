<!--
  Componente ComponentCard para el módulo de casos
  Basado en el diseño del frontend anterior con mejoras
-->
<template>
  <div
    :class="[
      'rounded-2xl border border-gray-200 bg-white transition-all duration-300 shadow-sm hover:shadow-md',
      { 'cursor-pointer card-hover': clickable },
      { 'opacity-50 cursor-not-allowed': disabled },
      { 'flex flex-col': $slots.footer },
      customClass,
    ]"
    @click="handleClick"
  >
    <!-- Card Header (opcional) -->
    <div
      v-if="!hideHeader && (title || description || $slots.header)"
      class="px-6 py-5 border-b border-gray-100"
    >
      <div class="flex items-center justify-between">
        <div v-if="title || description">
          <h3 v-if="title" class="text-lg font-semibold text-gray-900 flex items-center">
            <slot name="icon" />
            {{ title }}
          </h3>
          <p v-if="description" class="mt-1 text-sm text-gray-600">
            {{ description }}
          </p>
        </div>
        <div v-if="$slots.header" class="ml-4">
          <slot name="header" />
        </div>
      </div>
    </div>

    <!-- Card Body -->
    <div 
      :class="[
        'px-6',
        { 'bg-gray-50': loading },
        { 'flex-1 flex flex-col min-h-0': $slots.footer },
        { 'flex-1 flex flex-col min-h-0': fullHeight && !$slots.footer },
        { 'py-3': dense },
        { 'py-4': !dense && fullHeight },
        { 'py-6': !dense && !fullHeight }
      ]"
    >
      <div v-if="loading" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span class="ml-3 text-sm text-gray-500">{{ loadingText }}</span>
      </div>
      <div v-else :class="fullHeight ? 'flex-1 flex flex-col min-h-0' : 'space-y-4'">
        <slot />
      </div>
    </div>

    <!-- Card Footer -->
    <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100 rounded-b-2xl">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  /** Título de la tarjeta */
  title?: string
  /** Descripción opcional */
  description?: string
  /** Clases CSS adicionales */
  customClass?: string
  /** Si la tarjeta es clickeable */
  clickable?: boolean
  /** Si la tarjeta está deshabilitada */
  disabled?: boolean
  /** Si la tarjeta está en estado de carga */
  loading?: boolean
  /** Texto a mostrar durante la carga */
  loadingText?: string
  /** Reduce padding vertical del cuerpo */
  dense?: boolean
  /** Oculta por completo el header (título/descripción/slot header) */
  hideHeader?: boolean
  /** Si la tarjeta debe tener altura completa */
  fullHeight?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  description: '',
  customClass: '',
  clickable: false,
  disabled: false,
  loading: false,
  loadingText: 'Cargando...',
  dense: false,
  hideHeader: false
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const handleClick = (event: MouseEvent) => {
  if (props.disabled || props.loading) return
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped>
.card-hover {
  transform: translateY(0);
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
