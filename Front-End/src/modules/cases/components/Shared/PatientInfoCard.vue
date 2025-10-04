<template>
  <div v-if="patient" class="space-y-3">
    <!-- Información Principal -->
    <div class="bg-white rounded-lg p-3 border border-gray-200">
      <div class="mb-3 pb-3 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Nombre del Paciente</p>
            <h4 class="text-base font-semibold text-gray-900">{{ patient.name }}</h4>
          </div>
          <div class="flex items-center space-x-2 bg-green-50 px-2 py-1 rounded-full border border-green-200">
            <div class="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
            <span class="text-xs font-medium text-green-700">{{ badgeLabel }}</span>
          </div>
        </div>
      </div>

      <!-- Documento y Edad -->
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <div class="flex items-center space-x-2">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                </svg>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Documento</p>
              <p class="text-sm font-bold text-gray-900 font-mono truncate">{{ patient.patientCode }}</p>
            </div>
          </div>
        </div>

        <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <div class="flex items-center space-x-2">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Edad</p>
              <p class="text-sm font-bold text-gray-900">{{ patient.age }} años</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Género y Tipo de Atención -->
      <div class="grid grid-cols-2 gap-3 mt-3">
        <div v-if="patient.gender" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <div class="flex items-center space-x-2">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <GenderIcon size="16" color="#374151" />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Género</p>
              <p class="text-sm font-bold text-gray-900 capitalize">{{ patient.gender }}</p>
            </div>
          </div>
        </div>

        <div v-if="patient.careType" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <div class="flex items-center space-x-2">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <AttentionTypeIcon size="16" color="#374151" />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Atención</p>
              <p class="text-sm font-bold text-gray-900 capitalize">{{ patient.careType }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Entidad -->
    <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
      <div class="flex items-start space-x-2">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
            <EntityIcon class="w-4 h-4 text-gray-700" />
          </div>
        </div>
        <div class="flex-1">
          <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Entidad de Salud</p>
          <p class="text-sm font-semibold text-gray-900 break-words">{{ patient.entity }}</p>
          <p v-if="patient.entityCode" class="text-xs text-gray-600 font-mono mt-1">
            Código: {{ patient.entityCode }}
          </p>
        </div>
      </div>
    </div>

    <!-- Información de Ubicación -->
    <div v-if="hasLocationInfo" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
      <div class="flex items-start space-x-2 mb-3">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
            <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        </div>
        <div class="flex-1">
          <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-2">Información de Ubicación</p>
          
          <div class="grid grid-cols-2 gap-1">
            <!-- Municipio (Izquierda) -->
            <div v-if="locationMunicipality" class="space-y-1 flex flex-col justify-center">
              <p class="text-xs text-gray-500 font-medium">Municipio</p>
              <p class="text-sm font-semibold text-gray-900">{{ locationMunicipality }}</p>
              <p v-if="locationMunicipalityCode" class="text-xs text-gray-600 font-mono">
                Código: {{ locationMunicipalityCode }}
              </p>
            </div>
            
            <!-- Subregión y Dirección (Derecha) -->
            <div class="space-y-2">
              <!-- Subregión (Arriba) -->
              <div v-if="locationSubregion">
                <p class="text-xs text-gray-500 font-medium">Subregión</p>
                <p class="text-sm font-semibold text-gray-900">{{ locationSubregion }}</p>
              </div>
              
              <!-- Dirección (Abajo) -->
              <div v-if="locationAddress">
                <p class="text-xs text-gray-500 font-medium">Dirección</p>
                <p class="text-sm font-semibold text-gray-900">{{ locationAddress }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Observaciones (si existen) -->
    <div v-if="patient.observations" class="bg-blue-50 rounded-lg p-3 border border-blue-200">
      <div class="flex items-start space-x-2">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-blue-200">
            <svg class="w-4 h-4 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
          </div>
        </div>
        <div class="flex-1">
          <p class="text-xs uppercase tracking-wide text-blue-700 font-medium mb-1">Observaciones</p>
          <p class="text-xs text-blue-900 leading-relaxed whitespace-pre-line">{{ patient.observations }}</p>
        </div>
      </div>
    </div>
  </div>
  
  <div v-else class="flex items-center justify-center py-12 text-gray-400">
    <div class="text-center">
      <svg class="w-16 h-16 mx-auto mb-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
      </svg>
      <p class="text-sm font-medium text-gray-500">{{ emptyStateMessage }}</p>
      <p class="text-xs text-gray-400 mt-1">{{ emptyStateSubtext }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PatientData } from '@/modules/cases/types'
import EntityIcon from '@/assets/icons/EntityIcon.vue'
import GenderIcon from '@/assets/icons/GerdenIcon.vue'
import AttentionTypeIcon from '@/assets/icons/AtentionTypeIcon.vue'

interface PatientInfo {
  name: string
  patientCode: string
  age: string
  gender?: string
  careType?: string
  entity: string
  entityCode?: string
  location?: {
    address?: string
    municipality_name?: string
    municipality_code?: string
    subregion?: string
  }
  address?: string
  municipality_name?: string
  municipality_code?: string
  subregion?: string
  observations?: string
}

const props = withDefaults(defineProps<{
  patient?: PatientData | PatientInfo | null
  badgeLabel?: string
  emptyStateMessage?: string
  emptyStateSubtext?: string
}>(), {
  badgeLabel: 'Verificado',
  emptyStateMessage: 'No hay información del paciente',
  emptyStateSubtext: 'Complete la búsqueda para continuar'
})

const locationAddress = computed(() => {
  const p: any = props.patient || {}
  return p.location?.address || p.address || ''
})

const locationMunicipality = computed(() => {
  const p: any = props.patient || {}
  return p.location?.municipality_name || p.municipality_name || ''
})

const locationMunicipalityCode = computed(() => {
  const p: any = props.patient || {}
  return p.location?.municipality_code || p.municipality_code || ''
})

const locationSubregion = computed(() => {
  const p: any = props.patient || {}
  return p.location?.subregion || p.subregion || ''
})

const hasLocationInfo = computed(() => {
  return !!(locationMunicipality.value || locationSubregion.value || locationAddress.value)
})
</script>
