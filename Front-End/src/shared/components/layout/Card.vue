<template>
  <div :class="[
    'rounded-2xl border border-gray-200 bg-white transition-all duration-300 hover:shadow-lg',
    paddingClass,
    customClass
  ]">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  padding?: 'sm' | 'md' | 'lg'
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  padding: 'md',
  class: ''
})

const paddingClass = computed(() => {
  switch (props.padding) {
    case 'sm':
      return 'p-4'
    case 'lg':
      return 'p-6'
    default:
      return 'p-5 md:p-6'
  }
})

const customClass = computed(() => props.class)
</script>