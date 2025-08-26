<template>
  <div class="flex items-center">
    <label
      :for="id"
      class="flex items-center text-sm font-medium text-gray-700 cursor-pointer select-none"
    >
      <div class="relative">
        <input
          :id="id"
          :checked="modelValue"
          @change="$emit('update:modelValue', ($event.target as HTMLInputElement).checked)"
          type="checkbox"
          class="sr-only"
        />
        <div
          :class="[
            'mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] transition-all duration-300',
            modelValue
              ? 'border-brand-500 bg-gradient-to-tr from-brand-400 to-brand-600 shadow-lg scale-110'
              : 'bg-white/60 border-gray-300'
          ]"
        >
          <span :class="modelValue ? 'opacity-100 scale-100' : 'opacity-0 scale-0'" class="transition-all duration-300">
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M11.6666 3.5L5.24992 9.91667L2.33325 7"
                stroke="white"
                stroke-width="1.94437"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>
        </div>
      </div>
      {{ label }}
    </label>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  id?: string
  label: string
}

const props = withDefaults(defineProps<Props>(), {
  id: () => `checkbox-${Math.random().toString(36).substr(2, 9)}`
})

defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script> 