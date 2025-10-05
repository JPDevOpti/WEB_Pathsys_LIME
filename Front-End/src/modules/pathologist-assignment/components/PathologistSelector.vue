<template>
  <div class="bg-white border border-gray-200 rounded-lg p-4 flex flex-col shadow-sm">
    <!-- Header -->
    <div class="flex items-center mb-3 pb-3 border-b border-gray-200">
      <DoctorIcon class="w-5 h-5 text-blue-600 mr-2 flex-shrink-0" />
      <h4 class="text-sm font-semibold text-gray-800">Asignación de Patólogo</h4>
    </div>

    <!-- Content -->
    <div class="flex-1 flex flex-col space-y-4">
      <!-- Current pathologist info (if assigned) -->
      <div v-if="currentPathologistInfo" class="bg-amber-50 border border-amber-200 rounded-md p-3">
        <div class="flex items-start gap-2">
          <svg class="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-amber-800 uppercase tracking-wide">Patólogo Actualmente Asignado</p>
            <p class="text-sm text-amber-900 font-semibold mt-1 break-words">{{ currentPathologistInfo }}</p>
            <p class="text-xs text-amber-700 mt-1">Puedes cambiar la asignación seleccionando un nuevo patólogo abajo</p>
          </div>
        </div>
      </div>

      <!-- No pathologist assigned -->
      <div v-else-if="!currentPathologistInfo && modelValue" class="bg-blue-50 border border-blue-200 rounded-md p-3">
        <div class="flex items-start gap-2">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
          </svg>
          <div class="flex-1">
            <p class="text-xs font-semibold text-blue-800 uppercase tracking-wide">Nuevo Patólogo</p>
            <p class="text-sm text-blue-700 mt-1">Este caso no tiene un patólogo asignado. Selecciona uno de la lista.</p>
          </div>
        </div>
      </div>

      <!-- Pathologist selector -->
      <div class="flex-1 flex flex-col">
        <PathologistList
          :model-value="modelValue"
          label="Seleccionar Patólogo"
          placeholder="Buscar y seleccionar patólogo..."
          :required="true"
          :errors="errors"
          :disabled="disabled"
          help-text="Seleccione el patólogo responsable de este caso"
          @update:model-value="handleUpdate"
          @pathologist-selected="handlePathologistSelected"
          @load-success="handleLoadSuccess"
        />
      </div>

      <!-- Assignment preview -->
      <div v-if="assignmentPreview" class="bg-green-50 border border-green-200 rounded-md p-3 mt-auto">
        <div class="flex items-start gap-2">
          <svg class="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-green-800 uppercase tracking-wide">
              {{ isReassignment ? 'Reasignación preparada' : 'Asignación preparada' }}
            </p>
            <div class="mt-1 text-sm text-green-900">
              <p class="font-semibold break-words">{{ assignmentPreview.name }}</p>
              <div class="flex flex-wrap gap-x-3 gap-y-1 mt-1 text-xs text-green-700">
                <span v-if="assignmentPreview.code" class="font-mono">Código: {{ assignmentPreview.code }}</span>
                <span v-if="assignmentPreview.initials" class="uppercase font-medium">{{ assignmentPreview.initials }}</span>
                <span v-if="assignmentPreview.document">Doc: {{ assignmentPreview.document }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action hint when disabled -->
      <div v-if="disabled" class="bg-gray-50 border border-gray-200 rounded-md p-4 text-center">
        <svg class="w-10 h-10 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
        </svg>
        <p class="text-sm font-medium text-gray-500">Asignación bloqueada</p>
        <p class="text-xs text-gray-400 mt-1">Busque un caso válido para asignar un patólogo</p>
      </div>

      <!-- Action hint -->
      <div v-else-if="!assignmentPreview && !modelValue" class="text-center py-6 text-gray-400">
        <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
        </svg>
        <p class="text-sm">Selecciona un patólogo para continuar</p>
      </div>
    </div>

    <!-- Form actions (only visible when showActions is true) -->
    <div v-if="showActions" class="pt-4 border-t border-gray-200 mt-4">
      <div class="flex flex-col sm:flex-row justify-end gap-3">
        <button
          type="button"
          @click="handleClear"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          Limpiar
        </button>
        <button
          type="button"
          @click="handleAssign"
          :disabled="!isFormValid || isLoadingAssignment"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center min-w-[140px]"
        >
          <svg v-if="isLoadingAssignment" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ isLoadingAssignment ? 'Asignando...' : buttonText }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PathologistList } from '@/shared/components/ui/lists'
import type { FormPathologistInfo } from '@/modules/cases/types'
import { DoctorIcon } from '@/assets/icons'

interface AssignmentPreviewInfo {
  id: string
  name: string
  code?: string
  initials?: string
  document?: string
}

interface Props {
  modelValue: string
  currentPathologistInfo?: string | null
  assignmentPreview?: AssignmentPreviewInfo | null
  errors?: string[]
  disabled?: boolean
  showActions?: boolean
  isLoadingAssignment?: boolean
  isFormValid?: boolean
  buttonText?: string
}

const props = withDefaults(defineProps<Props>(), {
  currentPathologistInfo: null,
  assignmentPreview: null,
  errors: () => [],
  disabled: false,
  showActions: false,
  isLoadingAssignment: false,
  isFormValid: false,
  buttonText: 'Asignar Patólogo'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'pathologist-selected': [pathologist: FormPathologistInfo | null]
  'load-success': [pathologists: FormPathologistInfo[]]
  'update:assignmentPreview': [preview: AssignmentPreviewInfo | null]
  'clear': []
  'assign': []
}>()

const isReassignment = computed(() => {
  return !!(props.currentPathologistInfo && props.assignmentPreview && props.modelValue)
})

const handleUpdate = (value: string) => {
  emit('update:modelValue', value)
}

const handlePathologistSelected = (pathologist: FormPathologistInfo | null) => {
  emit('pathologist-selected', pathologist)
  
  if (pathologist) {
    const preview: AssignmentPreviewInfo = {
      id: pathologist.patologo_code || pathologist.id || '',
      name: pathologist.nombre,
      code: pathologist.patologo_code || pathologist.id,
      initials: pathologist.iniciales,
      document: pathologist.documento
    }
    emit('update:assignmentPreview', preview)
  } else {
    emit('update:assignmentPreview', null)
  }
}

const handleLoadSuccess = (pathologists: FormPathologistInfo[]) => {
  emit('load-success', pathologists)
}

const handleClear = () => {
  emit('clear')
}

const handleAssign = () => {
  emit('assign')
}
</script>
