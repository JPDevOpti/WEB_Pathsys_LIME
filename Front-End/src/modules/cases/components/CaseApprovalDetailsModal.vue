<template>
  <transition enter-active-class="transition ease-out duration-300" enter-from-class="opacity-0 transform scale-95" enter-to-class="opacity-100 transform scale-100" leave-active-class="transition ease-in duration-200" leave-from-class="opacity-100 transform scale-100" leave-to-class="opacity-0 transform scale-95">
    <div
      v-if="caseItem"
      :class="[
        'fixed right-0 bottom-0 z-[9999] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/40',
        'top-16',
        overlayLeftClass
      ]"
      @click.self="$emit('close')"
    >
      <div class="relative bg-white w-full max-w-5xl rounded-t-2xl sm:rounded-2xl shadow-2xl h-[90vh] sm:h-auto sm:max-h-[92vh] overflow-y-auto overflow-x-hidden">
        <!-- Header -->
        <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl flex items-center justify-between">
          <div class="flex flex-col">
            <h3 class="text-xl font-semibold text-gray-900">Revisión del Caso</h3>
            <p class="text-xs text-gray-500" v-if="caseItem.caseCode || caseItem.id">Código: {{ caseItem.caseCode || caseItem.id }}</p>
          </div>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600" aria-label="Cerrar">✕</button>
        </div>

        <div class="p-6 space-y-6">
          <!-- Estado y acciones rápidas -->
          <div class="flex flex-wrap items-center gap-3">
            <span v-if="caseItem.createdAt" class="text-xs text-gray-500">Fecha de creación: {{ formatDate(caseItem.createdAt) }}</span>
            <span v-if="caseItem.updatedAt" class="text-xs text-gray-500">Última actualización: {{ formatDate(caseItem.updatedAt) }}</span>
          </div>

          <!-- Datos del paciente -->
          <section class="grid grid-cols-2 lg:grid-cols-4 gap-4 bg-gray-50 rounded-xl p-4">
            <div>
              <p class="text-xs text-gray-500">Paciente</p>
              <p class="text-sm font-medium text-gray-900">{{ caseItem.patient?.fullName || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Documento</p>
              <p class="text-sm font-medium text-gray-900">{{ caseItem.patient?.id || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Edad</p>
              <p class="text-sm font-medium text-gray-900">{{ caseItem.patient?.age ? caseItem.patient.age + ' años' : 'N/D' }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Sexo</p>
              <p class="text-sm font-medium text-gray-900">{{ caseItem.patient?.sex || 'N/D' }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Tipo Atención</p>
              <p class="text-sm font-medium text-gray-900 capitalize">{{ caseItem.patient?.attentionType || 'N/D' }}</p>
            </div>
            <div class="col-span-2 lg:col-span-1">
              <p class="text-xs text-gray-500">Entidad</p>
              <p class="text-sm font-medium text-gray-900">{{ caseItem.patient?.entity || 'N/D' }}</p>
            </div>
          </section>

            <!-- Fechas y patólogo -->
          <section class="grid grid-cols-2 lg:grid-cols-3 gap-4 bg-gray-50 rounded-xl p-4">
            <div>
              <p class="text-xs text-gray-500">Recibido</p>
              <p class="text-sm font-medium text-gray-900">{{ caseItem.receivedAt ? formatDate(caseItem.receivedAt) : 'N/A' }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Entrega</p>
              <p class="text-sm font-medium text-gray-900">{{ caseItem.deliveredAt ? formatDate(caseItem.deliveredAt) : 'Pendiente' }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Patólogo</p>
              <p class="text-sm font-medium text-gray-900">{{ caseItem.pathologist || 'Sin asignar' }}</p>
            </div>
          </section>

          <!-- Descripción -->
          <section v-if="caseItem.description" class="bg-gray-50 rounded-xl p-4 space-y-2">
            <h5 class="text-xs font-medium text-gray-600">Descripción</h5>
            <p class="text-sm text-gray-800 whitespace-pre-line">{{ caseItem.description }}</p>
          </section>

          <!-- Muestras y pruebas -->
          <section class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-xs font-medium text-gray-600">Muestras y Pruebas</h5>
            <div v-if="caseItem.subsamples?.length" class="space-y-3">
              <div v-for="(muestra, mIdx) in caseItem.subsamples" :key="mIdx" class="border border-gray-200 rounded-lg p-3 bg-white">
                <div class="flex items-center justify-between mb-2">
                  <p class="text-xs text-gray-500">Región del cuerpo</p>
                  <p class="text-sm font-medium text-gray-900">{{ muestra.bodyRegion || 'No especificada' }}</p>
                </div>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(prueba, pIdx) in muestra.tests"
                    :key="pIdx"
                    class="relative inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-[11px] pl-2 pr-6 py-0.5 rounded border text-nowrap"
                    :title="prueba.name && prueba.name !== prueba.id ? prueba.name : ''"
                  >
                    {{ prueba.id }} - {{ prueba.name || prueba.id }}
                    <span
                      v-if="prueba.quantity > 1"
                      class="absolute -top-1 -right-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-blue-100 text-blue-600 text-[10px] font-bold"
                    >
                      {{ prueba.quantity }}
                    </span>
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="text-xs text-gray-500">Sin muestras registradas</div>
          </section>

          <!-- Pruebas nuevas asignadas por el patólogo -->
          <section v-if="caseItem.newAssignedTests && caseItem.newAssignedTests.length" class="bg-blue-50 rounded-xl p-4 space-y-3">
            <div class="flex items-center gap-2">
              <h5 class="text-xs font-medium text-blue-700">Pruebas nuevas asignadas por el patólogo</h5>
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-100 text-blue-700">{{ caseItem.newAssignedTests.length }}</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(test, idx) in caseItem.newAssignedTests"
                :key="idx"
                class="relative inline-flex items-center justify-center bg-white text-blue-700 font-mono text-[11px] pl-1 pr-6 py-0.5 rounded border border-blue-200 text-nowrap shadow-sm group"
                :title="test.name && test.name !== test.id ? test.name : ''"
              >
                <!-- Botón eliminar -->
                <button
                  type="button"
                  class="inline-flex items-center justify-center w-4 h-4 mr-1 rounded-sm text-red-500 hover:text-red-700 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-300 transition-colors"
                  aria-label="Eliminar prueba"
                  title="Eliminar prueba"
                  @click.stop="handleRemoveNewAssignedTest(idx, test)"
                >
                  <svg class="w-3 h-3" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 8.586l4.95-4.95 1.414 1.414L11.414 10l4.95 4.95-1.414 1.414L10 11.414l-4.95 4.95-1.414-1.414L8.586 10l-4.95-4.95L5.05 3.636 10 8.586z" clip-rule="evenodd" />
                  </svg>
                </button>
                {{ test.id }} - {{ test.name || test.id }}
                <span
                  v-if="test.quantity > 1"
                  class="absolute -top-1 -right-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-blue-600 text-white text-[10px] font-bold"
                >
                  {{ test.quantity }}
                </span>
              </span>
            </div>
          </section>

          <!-- Resultado del informe -->
          <section v-if="caseItem.result && (caseItem.result.method || caseItem.result.macro || caseItem.result.micro || caseItem.result.diagnosis)" class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-xs font-medium text-gray-600">Resultado del Informe</h5>
            <div v-if="caseItem.result.method" class="border border-gray-200 rounded-lg p-3 bg-white">
              <p class="text-xs text-gray-500 mb-1">Método</p>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.result.method }}</p>
            </div>
            <div v-if="caseItem.result.macro" class="border border-gray-200 rounded-lg p-3 bg-white">
              <p class="text-xs text-gray-500 mb-1">Resultado Macroscópico</p>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.result.macro }}</p>
            </div>
            <div v-if="caseItem.result.micro" class="border border-gray-200 rounded-lg p-3 bg-white">
              <p class="text-xs text-gray-500 mb-1">Resultado Microscópico</p>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.result.micro }}</p>
            </div>
            <div v-if="caseItem.result.diagnosis" class="border border-gray-200 rounded-lg p-3 bg-white">
              <p class="text-xs text-gray-500 mb-1">Diagnóstico</p>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.result.diagnosis }}</p>
            </div>
          </section>

          <!-- Diagnósticos Clasificados -->
          <section v-if="caseItem.result && (caseItem.result.diagnostico_cie10 || caseItem.result.diagnostico_cieo)" class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-xs font-medium text-gray-600">Diagnósticos Clasificados</h5>
            <div v-if="caseItem.result.diagnostico_cie10" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="flex items-center gap-2 mb-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-[10px] font-medium bg-blue-100 text-blue-800">CIE-10</span>
                <span class="text-xs font-mono text-gray-600">{{ caseItem.result.diagnostico_cie10.codigo }}</span>
              </div>
              <p class="text-sm text-gray-800">{{ caseItem.result.diagnostico_cie10.nombre }}</p>
            </div>
            <div v-if="caseItem.result.diagnostico_cieo" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="flex items-center gap-2 mb-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-[10px] font-medium bg-green-100 text-green-800">CIE-O</span>
                <span class="text-xs font-mono text-gray-600">{{ caseItem.result.diagnostico_cieo.codigo }}</span>
              </div>
              <p class="text-sm text-gray-800">{{ caseItem.result.diagnostico_cieo.nombre }}</p>
            </div>
          </section>
        </div>

        <!-- Footer -->
        <div class="sticky bottom-0 bg-white border-t border-gray-200 px-4 sm:px-6 py-3 sm:py-4 rounded-b-2xl">
          <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
            <div class="flex justify-center sm:justify-start w-full sm:w-auto">
              <BaseButton
                variant="outline"
                size="sm"
                text="Previsualizar"
                custom-class="bg-white border-blue-600 text-blue-600 hover:bg-blue-50"
                @click="$emit('preview', caseItem)"
              />
            </div>
            <div class="flex gap-2 justify-center sm:justify-end w-full sm:w-auto">
              <BaseButton variant="outline" size="sm" text="Aprobar" custom-class="bg-white border-green-600 text-green-600 hover:bg-green-50" :disabled="loadingApprove || loadingReject" :loading="loadingApprove" loading-text="Aprobando..." @click="$emit('approve', caseItem)" />
              <BaseButton variant="outline" size="sm" text="Rechazar" custom-class="bg-white border-red-600 text-red-600 hover:bg-red-50" :disabled="loadingApprove || loadingReject" :loading="loadingReject" loading-text="Rechazando..." @click="$emit('reject', caseItem)" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
  <!-- Dialogo de confirmación eliminación prueba nueva (fuera del <transition> para evitar múltiples hijos) -->
  <ConfirmDialog
    v-model="showConfirm"
    title="Eliminar prueba"
    :subtitle="pendingRemoval ? pendingRemoval.test?.name || pendingRemoval.test?.id : ''"
    message="Esta acción eliminará la prueba asignada. ¿Desea continuar?"
    confirm-text="Eliminar"
    cancel-text="Cancelar"
    @confirm="confirmRemoval"
    @cancel="cancelRemoval"
  />
</template>

<script setup lang="ts">
import { BaseButton } from '@/shared/components'
import { ConfirmDialog } from '@/shared/components/feedback'
import { computed } from 'vue'
import { useSidebar } from '@/shared/composables/SidebarControl'
import type { CaseApprovalDetails } from '../types/case-approval.types'

interface Props {
  caseItem: CaseApprovalDetails | null
  loadingApprove?: boolean
  loadingReject?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loadingApprove: false,
  loadingReject: false
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'approve', c: CaseApprovalDetails): void
  (e: 'reject', c: CaseApprovalDetails): void
  (e: 'preview', c: CaseApprovalDetails): void
  (e: 'remove-new-test', payload: { index: number; test: any; caseItem: CaseApprovalDetails }): void
}>()

function formatDate(dateString?: string) {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// Sidebar offset logic replicating CaseDetailsModal
const { isExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

function handleRemoveNewAssignedTest(index: number, test: any) {
  pendingRemoval.value = { index, test }
  showConfirm.value = true
}

// Estado para diálogo de confirmación
import { ref } from 'vue'
const showConfirm = ref(false)
const pendingRemoval = ref<{ index: number; test: any } | null>(null)

function confirmRemoval() {
  if (pendingRemoval.value && props.caseItem) {
    emit('remove-new-test', { index: pendingRemoval.value.index, test: pendingRemoval.value.test, caseItem: props.caseItem })
  }
  showConfirm.value = false
  pendingRemoval.value = null
}

function cancelRemoval() {
  showConfirm.value = false
  pendingRemoval.value = null
}
</script>
