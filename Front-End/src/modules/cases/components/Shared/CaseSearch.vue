<template>
  <div class="bg-gray-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-gray-200">
    <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
      <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      Buscar caso para editar
    </h3>

    <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
      <div class="flex-1">
        <FormInputField
          :model-value="caseCode"
          type="text"
          placeholder="Ejemplo: 2025-00001"
          maxlength="10"
          autocomplete="off"
          :disabled="isSearching"
          @update:model-value="handleCodeChange"
          @keydown.enter.prevent="$emit('search')"
        />
        <div v-if="caseCode && !isValidFormat" class="mt-1 text-xs text-red-600">
          El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)
        </div>
      </div>
      <div class="flex gap-2 sm:gap-3">
        <SearchButton 
          text="Buscar" 
          loading-text="Buscando..." 
          :loading="isSearching" 
          @click="$emit('search')" 
          size="md" 
          variant="primary" 
        />
        <ClearButton 
          v-if="caseFound" 
          text="Limpiar" 
          @click="$emit('clear')" 
        />
      </div>
    </div>

    <!-- Search error banner -->
    <div v-if="errorMessage" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <p class="text-sm text-red-600">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { FormInputField } from '@/shared/components/ui/forms'
import { SearchButton, ClearButton } from '@/shared/components/ui/buttons'

const props = defineProps<{
  caseCode: string
  isSearching: boolean
  errorMessage: string
  caseFound: boolean
}>()

const emit = defineEmits<{
  (e: 'update:caseCode', value: string): void
  (e: 'search'): void
  (e: 'clear'): void
}>()

const isValidFormat = computed(() => {
  return /^\d{4}-\d{5}$/.test(props.caseCode)
})

const handleCodeChange = (value: string) => {
  // Format input to YYYY-NNNNN
  let v = value.replace(/[^\d-]/g, '').slice(0, 10)
  if (v.length >= 4 && !v.includes('-')) {
    v = v.slice(0, 4) + '-' + v.slice(4)
  }
  const parts = v.split('-')
  if (parts.length > 2) {
    v = parts[0] + '-' + parts.slice(1).join('')
  }
  if (v.includes('-') && v.indexOf('-') !== 4) {
    const digits = v.replace(/-/g, '')
    v = digits.length >= 4 ? digits.slice(0, 4) + '-' + digits.slice(4, 9) : digits
  }
  emit('update:caseCode', v)
}
</script>
