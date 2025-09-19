<template>
  <FormCheckbox
    v-model="rememberMeValue"
    label="Keep me signed in"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { FormCheckbox } from '@/shared/components/forms'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const rememberMeValue = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})
</script> 