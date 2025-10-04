<template>
  <svg 
    :width="size" 
    :height="size" 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    :class="className"
  >
    <path 
      d="M12 17V11" 
      :stroke="color" 
      stroke-width="1.5" 
      stroke-linecap="round"
    />
    <circle 
      cx="1" 
      cy="1" 
      r="1" 
      transform="matrix(1 0 0 -1 11 9)" 
      :fill="color"
    />
    <path 
      d="M22 12C22 16.714 22 19.0711 20.5355 20.5355C19.0711 22 16.714 22 12 22C7.28595 22 4.92893 22 3.46447 20.5355C2 19.0711 2 16.714 2 12C2 7.28595 2 4.92893 3.46447 3.46447C4.92893 2 7.28595 2 12 2C16.714 2 19.0711 2 20.5355 3.46447C21.5093 4.43821 21.8356 5.80655 21.9449 8" 
      :stroke="color" 
      stroke-width="1.5" 
      stroke-linecap="round"
    />
  </svg>
</template>

<script setup lang="ts">
interface Props {
  size?: string | number
  color?: string
  className?: string
}

withDefaults(defineProps<Props>(), {
  size: '24',
  color: 'currentColor',
  className: ''
})
</script>
