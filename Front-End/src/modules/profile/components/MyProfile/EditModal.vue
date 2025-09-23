<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click="handleBackdropClick"
        @keydown.esc="handleClose"
      >
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
        
        <!-- Modal Container -->
        <div class="flex min-h-full items-center justify-center p-4">
          <Transition
            enter-active-class="transition-all duration-300"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition-all duration-300"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="isOpen"
              ref="modalRef"
              class="relative w-full max-w-2xl bg-white rounded-xl shadow-2xl border border-gray-200 transform transition-all"
              @click.stop
            >
              <!-- Header -->
              <div class="flex items-center justify-between p-6 border-b border-gray-200">
                <div class="flex items-center gap-3">
                  <div class="flex items-center justify-center w-10 h-10 rounded-full bg-blue-50">
                    <PencilIcon class="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold text-gray-900">
                      Editar Información Personal
                    </h3>
                    <p class="text-sm text-gray-500">
                      Actualice sus datos para mantener su perfil al día
                    </p>
                  </div>
                </div>
                
                <button
                  @click="handleClose"
                  class="flex items-center justify-center w-8 h-8 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                  aria-label="Cerrar modal"
                >
                  <XMarkIcon class="w-5 h-5" />
                </button>
              </div>

              <!-- Content -->
              <div class="p-6">
                <ProfileEditForm
                  :user="user"
                  :is-loading="isLoading"
                  @submit="handleSubmit"
                  @cancel="handleClose"
                  @change="handleFormChange"
                />
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { PencilIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import type { UserProfile, ValidationError, ProfileEditPayload } from '../../types/userProfile.types'
import ProfileEditForm from './ProfileEditForm.vue'

interface Props {
  isOpen: boolean
  user: UserProfile
  isLoading?: boolean
  errors?: ValidationError[]
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  errors: () => []
})

const emit = defineEmits<{
  close: []
  submit: [data: ProfileEditPayload]
  change: [hasChanges: boolean]
}>()

const modalRef = ref<HTMLElement>()

// Focus management
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen) {
    await nextTick()
    // Focus the first focusable element in the modal
    const firstFocusable = modalRef.value?.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as HTMLElement
    firstFocusable?.focus()
  }
})

const handleBackdropClick = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    handleClose()
  }
}

const handleClose = () => {
  emit('close')
}

const handleSubmit = (data: ProfileEditPayload) => {
  emit('submit', data)
}

const handleFormChange = (hasChanges: boolean) => {
  emit('change', hasChanges)
}
</script>