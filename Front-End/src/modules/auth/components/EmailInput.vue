<template>
  <div class="relative group">
    <label
      for="email"
      class="mb-1.5 block text-sm font-semibold text-gray-700"
    >
      Email Address<span class="text-error-500">*</span>
    </label>
    <div class="relative">
      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-brand-500 transition-colors duration-300">
        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
      </span>
      <input
        v-model="emailValue"
        type="email"
        id="email"
        placeholder="info@gmail.com"
        class="h-12 w-full rounded-lg border border-gray-300 bg-transparent py-2.5 pl-10 pr-10 text-base text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-200/40 transition-all duration-300 outline-none"
        :class="{'border-success-500': emailValue && isValidEmail(emailValue), 'border-error-500': emailValue && !isValidEmail(emailValue)}"
      />
      <!-- Iconos de validación de email -->
      <span v-if="emailValue" class="absolute right-3 top-1/2 -translate-y-1/2">
        <svg v-if="isValidEmail(emailValue)" class="w-5 h-5 text-success-500 scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else class="w-5 h-5 text-error-500 scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </span>
    </div>
    
    <!-- Mensaje de error -->
    <p v-if="emailError" class="mt-1 text-sm text-error-500">
      {{ emailError }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const emailValue = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value)
})

const emailError = computed(() => {
  if (!emailValue.value) return ''
  if (!isValidEmail(emailValue.value)) {
    return 'Please enter a valid email address'
  }
  return ''
})

const isValidEmail = (email: string) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}
</script> 