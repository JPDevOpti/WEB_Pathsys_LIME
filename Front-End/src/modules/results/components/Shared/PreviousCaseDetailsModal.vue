<template>
  <transition 
    enter-active-class="transition ease-out duration-300" 
    enter-from-class="opacity-0 transform scale-95" 
    enter-to-class="opacity-100 transform scale-100" 
    leave-active-class="transition ease-in duration-200" 
    leave-from-class="opacity-100 transform scale-100" 
    leave-to-class="opacity-0 transform scale-95"
  >
    <div
      v-if="caseItem"
      :class="[
        'fixed right-0 bottom-0 z-[9999] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/40',
        'top-16',
        overlayLeftClass
      ]"
      @click.self="$emit('close')"
    >
      <div class="relative bg-white w-full max-w-4xl rounded-t-2xl sm:rounded-2xl shadow-2xl h-[85vh] sm:h-auto sm:max-h-[90vh] overflow-y-auto overflow-x-hidden">
        <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900">Detalles del Caso Anterior</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="p-6 space-y-6">
          <!-- Información básica del caso -->
          <div class="grid grid-cols-2 gap-4 bg-gray-50 rounded-xl p-4">
            <div>
              <p class="text-sm text-gray-500">Código del Caso</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.caso_code || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Estado</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.estado || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Nombre del Paciente</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.paciente?.nombre || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Código del Paciente</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.paciente?.paciente_code || 'N/A' }}</p>
            </div>
            <div v-if="caseItem?.paciente?.edad">
              <p class="text-sm text-gray-500">Edad</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem.paciente.edad }} años</p>
            </div>
            <div v-if="caseItem?.paciente?.sexo">
              <p class="text-sm text-gray-500">Sexo</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem.paciente.sexo }}</p>
            </div>
            <div v-if="caseItem?.paciente?.tipo_atencion">
              <p class="text-sm text-gray-500">Tipo de Atención</p>
              <p class="text-base font-medium text-gray-900 capitalize">{{ caseItem.paciente.tipo_atencion }}</p>
            </div>
            <div v-if="caseItem?.paciente?.entidad_info">
              <p class="text-sm text-gray-500">Entidad</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem.paciente.entidad_info.nombre || 'No especificada' }}</p>
            </div>
            <div v-if="caseItem?.servicio">
              <p class="text-sm text-gray-500">Servicio</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem.servicio }}</p>
            </div>
            <div v-if="caseItem?.prioridad">
              <p class="text-sm text-gray-500">Prioridad</p>
              <p class="text-base font-medium text-gray-900 capitalize">{{ caseItem.prioridad }}</p>
            </div>
          </div>

          <!-- Observaciones Generales -->
          <div v-if="caseItem?.observaciones_generales" class="bg-gray-50 rounded-xl p-4">
            <h5 class="text-sm font-medium text-gray-700 mb-3">Observaciones Generales</h5>
            <div class="border border-gray-200 rounded-lg p-3 bg-white">
              <p class="text-sm text-gray-800 break-words">{{ caseItem.observaciones_generales }}</p>
            </div>
          </div>

          <!-- Información temporal y patólogo -->
          <div class="grid grid-cols-3 gap-4 bg-gray-50 rounded-xl p-4">
            <div>
              <p class="text-sm text-gray-500">Fecha de Ingreso</p>
              <p class="text-base font-medium text-gray-900">{{ (caseItem?.fecha_ingreso || caseItem?.fecha_creacion) ? formatDate(caseItem.fecha_ingreso || caseItem.fecha_creacion) : 'N/A' }}</p>
            </div>
            <div v-if="caseItem?.fecha_firma">
              <p class="text-sm text-gray-500">Fecha de Firma</p>
              <p class="text-base font-medium text-gray-900">{{ formatDate(caseItem.fecha_firma) }}</p>
            </div>
            <div v-else>
              <p class="text-sm text-gray-500">Fecha de Firma</p>
              <p class="text-base font-medium text-gray-900">Pendiente</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Patólogo Asignado</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.patologo_asignado?.nombre || 'Sin asignar' }}</p>
            </div>
          </div>

          <!-- Muestras y pruebas -->
          <div class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-sm font-medium text-gray-700">Muestras y Pruebas</h5>
            <div v-if="caseItem?.muestras && caseItem.muestras.length" class="space-y-3">
              <div v-for="(muestra, mIdx) in caseItem.muestras" :key="mIdx" class="border border-gray-200 rounded-lg p-3 bg-white">
                <div class="flex items-center justify-between mb-2">
                  <p class="text-sm text-gray-600">Región del cuerpo</p>
                  <p class="text-sm font-medium text-gray-900">{{ muestra.region_cuerpo || 'No especificada' }}</p>
                </div>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(prueba, pIdx) in muestra.pruebas"
                    :key="pIdx"
                    class="relative inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs pl-2 pr-6 py-0.5 rounded border text-nowrap"
                    :title="prueba.nombre && prueba.nombre !== prueba.id ? prueba.nombre : ''"
                  >
                    {{ prueba.id }} - {{ prueba.nombre || prueba.id }}
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="text-sm text-gray-500">Sin muestras registradas</div>
          </div>

          <!-- Resultado del caso -->
          <div v-if="caseItem?.resultado && (caseItem.resultado.resultado_macro || caseItem.resultado.resultado_micro || caseItem.resultado.diagnostico || caseItem.resultado.tipo_resultado)" class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-sm font-medium text-gray-700">Resultado del Informe</h5>
            
            <!-- Tipo de Resultado -->
            <div v-if="caseItem.resultado.tipo_resultado" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Tipo de Resultado</p>
              </div>
              <p class="text-sm font-medium text-gray-900 break-words">{{ caseItem.resultado.tipo_resultado }}</p>
            </div>

            <!-- Resultado Macroscópico -->
            <div v-if="caseItem.resultado.resultado_macro" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Resultado Macroscópico</p>
              </div>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.resultado.resultado_macro }}</p>
            </div>

            <!-- Resultado Microscópico -->
            <div v-if="caseItem.resultado.resultado_micro" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Resultado Microscópico</p>
              </div>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.resultado.resultado_micro }}</p>
            </div>

            <!-- Diagnóstico -->
            <div v-if="caseItem.resultado.diagnostico" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Diagnóstico</p>
              </div>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.resultado.diagnostico }}</p>
            </div>
          </div>

          <!-- Diagnósticos CIE-10 y CIE-O -->
          <div v-if="caseItem?.resultado && (caseItem.resultado.diagnostico_cie10 || caseItem.resultado.diagnostico_cieo)" class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-sm font-medium text-gray-700">Diagnósticos Clasificados</h5>
            
            <!-- Diagnóstico CIE-10 -->
            <div v-if="caseItem.resultado.diagnostico_cie10" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="flex items-center gap-2 mb-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  CIE-10
                </span>
                <span class="text-sm font-mono text-gray-600">{{ caseItem.resultado.diagnostico_cie10.codigo }}</span>
              </div>
              <p class="text-sm text-gray-800">{{ caseItem.resultado.diagnostico_cie10.nombre }}</p>
            </div>

            <!-- Diagnóstico CIE-O -->
            <div v-if="caseItem.resultado.diagnostico_cieo" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="flex items-center gap-2 mb-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  CIE-O
                </span>
                <span class="text-sm font-mono text-gray-600">{{ caseItem.resultado.diagnostico_cieo.codigo }}</span>
              </div>
              <p class="text-sm text-gray-800">{{ caseItem.resultado.diagnostico_cieo.nombre }}</p>
            </div>
          </div>

          <!-- Información de firma -->
          <div v-if="caseItem?.resultado?.firmado" class="bg-gray-50 rounded-xl p-4">
            <h5 class="text-sm font-medium text-gray-700 mb-3">Información de Firma</h5>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">Fecha de Firma</p>
                <p class="text-base font-medium text-gray-900">{{ caseItem.resultado.fecha_firma ? formatDate(caseItem.resultado.fecha_firma) : 'N/A' }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Patólogo Firmante</p>
                <p class="text-base font-medium text-gray-900">{{ caseItem.resultado.patologo_firma || 'N/A' }}</p>
              </div>
            </div>
          </div>

        </div>
        
        <!-- Botones de acción -->
        <div class="sticky bottom-0 bg-white border-t border-gray-200 px-4 sm:px-6 py-3 sm:py-4 rounded-b-2xl">
          <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
            <div class="flex justify-center sm:justify-start">
              <!-- Botón de previsualización temporalmente deshabilitado -->
            </div>
            <div class="flex gap-2 justify-center sm:justify-end">
              <button
                @click="$emit('close')"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { CaseModel } from '@/modules/cases/types/case'
import { useSidebar } from '@/shared/composables/SidebarControl'

const props = defineProps<{ caseItem: CaseModel | null }>()
defineEmits<{ (e: 'close'): void }>()

const router = useRouter()

function formatDate(dateString: string) {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// Ajuste responsivo: respetar ancho del sidebar (colapsado/expandido) y hover
const { isExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const handlePreview = () => {
  // Cerrar el modal primero
  const closeEvent = new CustomEvent('close')
  window.dispatchEvent(closeEvent)
  
  // Preparar payload completo para la previsualización
  if (props.caseItem?.caso_code) {
    const payload = {
      sampleId: props.caseItem.caso_code,
      patient: props.caseItem.paciente ? {
        id: props.caseItem.paciente.paciente_code,
        fullName: props.caseItem.paciente.nombre,
        document: props.caseItem.paciente.paciente_code,
        age: props.caseItem.paciente.edad,
        entity: props.caseItem.paciente.entidad_info?.nombre,
        entityCode: props.caseItem.paciente.entidad_info?.codigo,
        sexo: props.caseItem.paciente.sexo,
        observaciones: props.caseItem.paciente.observaciones || ''
      } : null,
      caseDetails: {
        _id: props.caseItem._id || '',
        caso_code: props.caseItem.caso_code,
        paciente: props.caseItem.paciente,
        medico_solicitante: props.caseItem.medico_solicitante,
        muestras: props.caseItem.muestras || [],
        estado: props.caseItem.estado,
        fecha_creacion: props.caseItem.fecha_creacion,
        fecha_ingreso: props.caseItem.fecha_ingreso || props.caseItem.fecha_creacion,
        fecha_firma: props.caseItem.fecha_firma,
        fecha_actualizacion: props.caseItem.fecha_actualizacion,
        observaciones_generales: props.caseItem.observaciones_generales,
        is_active: props.caseItem.activo ?? true,
        patologo_asignado: props.caseItem.patologo_asignado,
        actualizado_por: props.caseItem.actualizado_por,
        entidad_info: props.caseItem.entidad_info,
        servicio: props.caseItem.servicio,
        resultado: props.caseItem.resultado
      },
      sections: props.caseItem.resultado ? {
        method: props.caseItem.resultado.metodo || [],
        macro: props.caseItem.resultado.resultado_macro || '',
        micro: props.caseItem.resultado.resultado_micro || '',
        diagnosis: props.caseItem.resultado.diagnostico || ''
      } : null,
      diagnosis: {
        cie10: props.caseItem.resultado?.diagnostico_cie10 ? {
          codigo: props.caseItem.resultado.diagnostico_cie10.codigo,
          nombre: props.caseItem.resultado.diagnostico_cie10.nombre
        } : undefined,
        cieo: props.caseItem.resultado?.diagnostico_cieo ? {
          codigo: props.caseItem.resultado.diagnostico_cieo.codigo,
          nombre: props.caseItem.resultado.diagnostico_cieo.nombre
        } : undefined,
        formatted: props.caseItem.resultado?.diagnostico_cie10 ? 
          `${props.caseItem.resultado.diagnostico_cie10.codigo} - ${props.caseItem.resultado.diagnostico_cie10.nombre}` : 
          (props.caseItem.resultado?.diagnostico_cieo ? 
            `${props.caseItem.resultado.diagnostico_cieo.codigo} - ${props.caseItem.resultado.diagnostico_cieo.nombre}` : 
            '')
      },
      generatedAt: new Date().toISOString()
    }
    
    // Función de previsualización temporalmente deshabilitada
    console.log('Previsualización temporalmente deshabilitada')
  }
}
</script>
