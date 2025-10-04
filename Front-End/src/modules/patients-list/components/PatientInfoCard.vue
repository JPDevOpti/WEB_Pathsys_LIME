<template>
  <ComponentCard
    title="Información del Paciente"
    :show-content="hasSelectedPatient"
  >
    <template #content>
      <div v-if="hasSelectedPatient" class="space-y-4">
        <!-- Patient basic info -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Código</label>
            <p class="text-sm text-gray-900">{{ selectedPatient?.code }}</p>
          </div>
          
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Nombre Completo</label>
            <p class="text-sm text-gray-900">{{ selectedPatient?.fullName }}</p>
          </div>
          
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Identificación</label>
            <p class="text-sm text-gray-900">{{ selectedPatient?.identification }}</p>
          </div>
          
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Sexo</label>
            <p class="text-sm text-gray-900">{{ selectedPatient?.gender }}</p>
          </div>
          
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Edad</label>
            <p class="text-sm text-gray-900">{{ selectedPatient?.age }} años</p>
          </div>
          
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Entidad</label>
            <p class="text-sm text-gray-900">{{ selectedPatient?.entity }}</p>
          </div>
          
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Tipo de Atención</label>
            <p class="text-sm text-gray-900">{{ selectedPatient?.careType }}</p>
          </div>
          
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Ubicación</label>
            <p class="text-sm text-gray-900">{{ selectedPatient?.location }}</p>
          </div>
          
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700">Fecha de Creación</label>
            <p class="text-sm text-gray-900">{{ selectedPatient?.createdAt ? formatDate(selectedPatient.createdAt) : '' }}</p>
          </div>
        </div>

        <!-- Additional patient details if available -->
        <div v-if="selectedPatient?.additionalInfo" class="border-t pt-4">
          <h4 class="text-sm font-medium text-gray-700 mb-2">Información Adicional</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-if="selectedPatient?.additionalInfo?.phone" class="space-y-1">
              <label class="text-sm font-medium text-gray-700">Teléfono</label>
              <p class="text-sm text-gray-900">{{ selectedPatient.additionalInfo.phone }}</p>
            </div>
            
            <div v-if="selectedPatient?.additionalInfo?.email" class="space-y-1">
              <label class="text-sm font-medium text-gray-700">Email</label>
              <p class="text-sm text-gray-900">{{ selectedPatient.additionalInfo.email }}</p>
            </div>
            
            <div v-if="selectedPatient?.additionalInfo?.address" class="space-y-1">
              <label class="text-sm font-medium text-gray-700">Dirección</label>
              <p class="text-sm text-gray-900">{{ selectedPatient.additionalInfo.address }}</p>
            </div>
          </div>
        </div>

        <!-- Patient actions -->
        <div class="border-t pt-4">
          <div class="flex flex-wrap gap-2">
            <button
              @click="handleViewDetails"
              class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Ver Detalles
            </button>
            
            <button
              @click="handleEdit"
              class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Editar
            </button>
            
            <button
              v-if="allowSelection"
              @click="handleSelect"
              class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Seleccionar
            </button>
          </div>
        </div>
      </div>
      
      <div v-else class="text-center py-8">
        <div class="text-gray-400 mb-2">
          <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <p class="text-sm text-gray-500">Selecciona un paciente para ver su información</p>
      </div>
    </template>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ComponentCard } from '@/shared/components'

// Types
interface PatientData {
  id: string
  code: string
  fullName: string
  identification: string
  gender: string
  age: number
  entity: string
  careType: string
  location: string
  createdAt: string
  updatedAt?: string
  additionalInfo?: {
    phone?: string
    email?: string
    address?: string
  }
}

// Props
interface Props {
  selectedPatient?: PatientData | null
  allowSelection?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selectedPatient: null,
  allowSelection: false
})

// Emits
const emit = defineEmits<{
  viewDetails: [patient: PatientData]
  edit: [patient: PatientData]
  select: [patient: PatientData]
}>()

// Computed
const hasSelectedPatient = computed(() => props.selectedPatient !== null)

// Methods
const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateString
  }
}

const handleViewDetails = () => {
  if (props.selectedPatient) {
    emit('viewDetails', props.selectedPatient)
  }
}

const handleEdit = () => {
  if (props.selectedPatient) {
    emit('edit', props.selectedPatient)
  }
}

const handleSelect = () => {
  if (props.selectedPatient) {
    emit('select', props.selectedPatient)
  }
}
</script>