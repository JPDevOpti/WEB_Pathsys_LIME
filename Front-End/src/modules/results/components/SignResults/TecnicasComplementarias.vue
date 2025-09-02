<template>
  <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
    <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
      <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      Técnicas Complementarias
    </h3>

    <div class="mb-4">
      <FormCheckbox
        id="needs-complementary-techniques"
        :model-value="needsComplementaryTechniques"
        @update:model-value="handleNeedsTechniquesChange"
        label="Se necesitan técnicas complementarias"
        class="text-sm font-medium text-gray-700"
      />
    </div>

    <div v-if="needsComplementaryTechniques" class="space-y-4">
      <div>
        <label for="complementary-techniques-details" class="block text-sm font-medium text-gray-700 mb-2">
          Descripción de las técnicas complementarias requeridas
        </label>
        <FormTextarea
          id="complementary-techniques-details"
          :model-value="complementaryTechniquesDetails"
          @update:model-value="handleDetailsChange"
          placeholder="Describa las técnicas complementarias que se requieren para completar el diagnóstico..."
          :rows="4"
          class="w-full"
        />
      </div>

      <div class="flex justify-end">
        <SaveButton
          :disabled="!complementaryTechniquesDetails.trim()"
          :loading="signingWithChanges"
          text="Firmar con Cambios"
          loading-text="Firmando..."
          @click="handleSignWithChanges"
          size="md"
          variant="secondary"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton } from '@/shared/components/buttons'

interface Props {
  initialNeedsTechniques?: boolean
  initialDetails?: string
}

const props = withDefaults(defineProps<Props>(), {
  initialNeedsTechniques: false,
  initialDetails: ''
})

const emit = defineEmits<{
  (e: 'needs-techniques-change', value: boolean): void
  (e: 'details-change', value: string): void
  (e: 'sign-with-changes', details: string): void
}>()

const needsComplementaryTechniques = ref(props.initialNeedsTechniques)
const complementaryTechniquesDetails = ref(props.initialDetails)
const signingWithChanges = ref(false)

const handleNeedsTechniquesChange = (value: boolean) => {
  needsComplementaryTechniques.value = value
  if (!value) {
    complementaryTechniquesDetails.value = ''
  }
  emit('needs-techniques-change', value)
}

const handleDetailsChange = (value: string) => {
  complementaryTechniquesDetails.value = value
  emit('details-change', value)
}

const handleSignWithChanges = async () => {
  if (!complementaryTechniquesDetails.value.trim()) return
  
  signingWithChanges.value = true
  try {
    emit('sign-with-changes', complementaryTechniquesDetails.value)
  } finally {
    signingWithChanges.value = false
  }
}
</script>
