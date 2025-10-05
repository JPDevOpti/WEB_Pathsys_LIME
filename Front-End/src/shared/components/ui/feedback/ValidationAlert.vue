<template>
  <Notification
    :visible="visible"
    type="error"
    :title="title"
    :message="message"
    :inline="true"
    :auto-close="false"
    @close="$emit('close')"
    class="w-full col-span-full"
  >
    <template #content>
      <div class="w-full mt-3">
        <ul class="w-full list-disc list-inside space-y-2 text-sm text-red-700">
          <li v-for="error in errors" :key="error" class="text-red-700 break-words">
            {{ error }}
          </li>
        </ul>
      </div>
    </template>
  </Notification>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Notification from './Notification.vue'

interface Props {
  visible: boolean
  errors: string[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Por favor corrija los siguientes errores:'
})

const emit = defineEmits<{
  close: []
}>()

// Mensaje principal que se muestra en el campo message del Notification
const message = computed(() => {
  if (props.errors.length === 0) return ''
  if (props.errors.length === 1) return '' // evitar duplicar: la lista mostrará el único error
  return `${props.errors.length} errores encontrados`
})
</script>
