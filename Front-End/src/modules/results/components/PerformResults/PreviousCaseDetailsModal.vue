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
              <p class="text-base font-medium text-gray-900">{{ caseItem?.CasoCode || 'N/A' }}</p>
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
              <p class="text-sm text-gray-500">Cédula</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.paciente?.cedula || 'N/A' }}</p>
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
          </div>

          <!-- Información temporal y patólogo -->
          <div class="grid grid-cols-3 gap-4 bg-gray-50 rounded-xl p-4">
            <div>
              <p class="text-sm text-gray-500">Fecha de Ingreso</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.fecha_ingreso ? formatDate(caseItem.fecha_ingreso) : 'N/A' }}</p>
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

          <!-- Información adicional del caso -->
          <div v-if="caseItem?.servicio || caseItem?.observaciones_generales" class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-sm font-medium text-gray-700">Información Adicional</h5>
            <div v-if="caseItem.servicio" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Servicio</p>
              </div>
              <p class="text-sm font-medium text-gray-900">{{ caseItem.servicio }}</p>
            </div>
            <div v-if="caseItem.observaciones_generales" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Observaciones Generales</p>
              </div>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.observaciones_generales }}</p>
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

          <!-- Información de auditoría -->
          <div v-if="caseItem?.creado_por || caseItem?.actualizado_por || caseItem?.fecha_actualizacion" class="bg-gray-50 rounded-xl p-4">
            <h5 class="text-sm font-medium text-gray-700 mb-3">Información de Auditoría</h5>
            <div class="grid grid-cols-2 gap-4">
              <div v-if="caseItem.creado_por">
                <p class="text-sm text-gray-500">Creado por</p>
                <p class="text-base font-medium text-gray-900">{{ caseItem.creado_por }}</p>
              </div>
              <div v-if="caseItem.actualizado_por">
                <p class="text-sm text-gray-500">Actualizado por</p>
                <p class="text-base font-medium text-gray-900">{{ caseItem.actualizado_por }}</p>
              </div>
              <div v-if="caseItem.fecha_actualizacion">
                <p class="text-sm text-gray-500">Última actualización</p>
                <p class="text-base font-medium text-gray-900">{{ formatDate(caseItem.fecha_actualizacion) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CaseModel } from '@/modules/cases/types/case'
import { useSidebar } from '@/shared/composables/SidebarControl'

defineProps<{ caseItem: CaseModel | null }>()
defineEmits<{ (e: 'close'): void }>()

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
</script>
