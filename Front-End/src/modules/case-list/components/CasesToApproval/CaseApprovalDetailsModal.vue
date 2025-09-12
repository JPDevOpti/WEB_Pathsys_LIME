<template>
  <Modal
    v-model="isOpen"
    title="Detalles de Solicitud de Pruebas Complementarias"
    size="lg"
    @close="$emit('close')"
  >
    <div class="space-y-6">
      <!-- Estado de la solicitud -->
          <div class="bg-gray-50 rounded-xl p-4">
            <div class="flex items-center justify-between">
              <h4 class="text-lg font-medium text-gray-900">Estado de la Solicitud</h4>
              <span 
                :class="[
                  'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium',
                  approvalCase?.estado_aprobacion === 'solicitud_hecha' ? 'bg-blue-100 text-blue-800' :
                  approvalCase?.estado_aprobacion === 'pendiente_aprobacion' ? 'bg-yellow-100 text-yellow-800' :
                  approvalCase?.estado_aprobacion === 'aprobado' ? 'bg-green-100 text-green-800' :
                  'bg-red-100 text-red-800'
                ]"
              >
                {{ getStatusLabel(approvalCase?.estado_aprobacion || '') }}
              </span>
            </div>
            <div class="mt-3">
              <div>
                <p class="text-sm text-gray-500">Fecha de solicitud</p>
                <p class="font-medium text-gray-900">{{ formatDate(approvalCase?.fecha_creacion) }}</p>
              </div>
            </div>
          </div>

          <!-- Información del caso original -->
          <div class="bg-gray-50 rounded-xl p-4">
            <h4 class="text-lg font-medium text-gray-900 mb-3">Información del Caso Original</h4>
            <div v-if="loadingOriginalCase" class="text-center py-4">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              <p class="text-sm text-gray-500 mt-2">Cargando información del caso...</p>
            </div>
            <div v-else-if="originalCaseError" class="text-center py-4">
              <p class="text-sm text-red-600">{{ originalCaseError }}</p>
            </div>
            <div v-else-if="originalCase" class="space-y-4">
              <!-- Información básica del caso -->
              <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p class="text-sm text-gray-500">Código del caso</p>
                  <p class="font-medium text-gray-900">{{ originalCase.caso_code }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Estado</p>
                  <p class="font-medium text-gray-900 capitalize">{{ originalCase.estado }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Fecha de ingreso</p>
                  <p class="font-medium text-gray-900">{{ 
                    formatDate(
                      originalCase.fecha_ingreso || 
                      originalCase.fechaIngreso || 
                      originalCase.fecha_creacion || 
                      originalCase.createdAt ||
                      originalCase.fecha_registro
                    ) 
                  }}</p>
                </div>
              </div>

              <!-- Información del paciente -->
              <div>
                <h5 class="text-sm font-medium text-gray-700 mb-2">Información del Paciente</h5>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 bg-white border border-gray-200 rounded-lg p-3">
                  <div>
                    <p class="text-sm text-gray-500">Nombre</p>
                    <p class="font-medium text-gray-900">{{ originalCase.paciente?.nombre || 'N/A' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Código</p>
                    <p class="font-medium text-gray-900">{{ originalCase.paciente?.paciente_code || 'N/A' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Edad</p>
                    <p class="font-medium text-gray-900">{{ originalCase.paciente?.edad ? `${originalCase.paciente.edad} años` : 'N/A' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Sexo</p>
                    <p class="font-medium text-gray-900">{{ originalCase.paciente?.sexo || 'N/A' }}</p>
                  </div>
                </div>
              </div>

              <!-- Patólogo asignado -->
              <div v-if="originalCase.patologo_asignado">
                <h5 class="text-sm font-medium text-gray-700 mb-2">Patólogo Asignado</h5>
                <div class="bg-white border border-gray-200 rounded-lg p-3">
                  <p class="font-medium text-gray-900">{{ originalCase.patologo_asignado.nombre }}</p>
                  <p class="text-sm text-gray-500">Código: {{ originalCase.patologo_asignado.codigo }}</p>
                </div>
              </div>

              <!-- Muestras y pruebas del caso original -->
              <div v-if="originalCase.muestras && originalCase.muestras.length">
                <h5 class="text-sm font-medium text-gray-700 mb-2">Muestras del Caso Original</h5>
                <div class="space-y-2">
                  <div v-for="(muestra, index) in originalCase.muestras" :key="index" class="bg-white border border-gray-200 rounded-lg p-3">
                    <div class="mb-2">
                      <p class="text-sm text-gray-500">Región del cuerpo</p>
                      <p class="font-medium text-gray-900">{{ muestra.region_cuerpo || 'No especificada' }}</p>
                    </div>
                    <div v-if="muestra.pruebas && muestra.pruebas.length">
                      <p class="text-sm text-gray-500 mb-1">Pruebas realizadas</p>
                      <div class="flex flex-wrap gap-1">
                        <span
                          v-for="prueba in muestra.pruebas"
                          :key="prueba.id"
                          class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700"
                        >
                          {{ prueba.id }} - {{ prueba.nombre }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Resultados del caso original -->
              <div v-if="originalCase.resultados || originalCase.diagnosticos || originalCase.conclusion">
                <h5 class="text-sm font-medium text-gray-700 mb-2">Resultados del Caso Original</h5>
                <div class="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
                  
                  <!-- Descripción macroscópica -->
                  <div v-if="originalCase.resultados?.descripcion_macroscopica">
                    <h6 class="text-sm font-medium text-gray-600 mb-1">Descripción Macroscópica</h6>
                    <div class="bg-gray-50 rounded-lg p-3">
                      <p class="text-sm text-gray-900 whitespace-pre-line">{{ originalCase.resultados.descripcion_macroscopica }}</p>
                    </div>
                  </div>

                  <!-- Descripción microscópica -->
                  <div v-if="originalCase.resultados?.descripcion_microscopica">
                    <h6 class="text-sm font-medium text-gray-600 mb-1">Descripción Microscópica</h6>
                    <div class="bg-gray-50 rounded-lg p-3">
                      <p class="text-sm text-gray-900 whitespace-pre-line">{{ originalCase.resultados.descripcion_microscopica }}</p>
                    </div>
                  </div>

                  <!-- Diagnósticos -->
                  <div v-if="originalCase.diagnosticos && originalCase.diagnosticos.length">
                    <h6 class="text-sm font-medium text-gray-600 mb-2">Diagnósticos</h6>
                    <div class="space-y-2">
                      <div v-for="(diagnostico, index) in originalCase.diagnosticos" :key="index" class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <div class="flex flex-wrap gap-2 mb-2">
                          <span v-if="diagnostico.cie10_codigo" class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            CIE-10: {{ diagnostico.cie10_codigo }}
                          </span>
                          <span v-if="diagnostico.cieo_codigo" class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                            CIE-O: {{ diagnostico.cieo_codigo }}
                          </span>
                        </div>
                        <p v-if="diagnostico.descripcion" class="text-sm text-gray-900">{{ diagnostico.descripcion }}</p>
                        <p v-if="diagnostico.cie10_descripcion" class="text-xs text-gray-600 mt-1">{{ diagnostico.cie10_descripcion }}</p>
                      </div>
                    </div>
                  </div>

                  <!-- Conclusión -->
                  <div v-if="originalCase.resultados?.conclusion || originalCase.conclusion">
                    <h6 class="text-sm font-medium text-gray-600 mb-1">Conclusión</h6>
                    <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                      <p class="text-sm text-gray-900 whitespace-pre-line">{{ originalCase.resultados?.conclusion || originalCase.conclusion }}</p>
                    </div>
                  </div>

                  <!-- Método utilizado -->
                  <div v-if="originalCase.resultados?.metodo">
                    <h6 class="text-sm font-medium text-gray-600 mb-1">Método Utilizado</h6>
                    <div class="bg-gray-50 rounded-lg p-2">
                      <p class="text-sm text-gray-900">{{ originalCase.resultados.metodo }}</p>
                    </div>
                  </div>

                  <!-- Estado de resultados -->
                  <div v-if="originalCase.resultados?.estado">
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium text-gray-600">Estado de resultados:</span>
                      <span :class="[
                        'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                        originalCase.resultados.estado === 'firmado' ? 'bg-green-100 text-green-800' :
                        originalCase.resultados.estado === 'borrador' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      ]">
                        {{ originalCase.resultados.estado }}
                      </span>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>

          <!-- Pruebas complementarias solicitadas -->
          <div class="bg-orange-50 border border-orange-200 rounded-xl p-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-lg font-medium text-gray-900 flex items-center gap-2">
                <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                Pruebas Complementarias Solicitadas
              </h4>
              <button
                v-if="canEditTests && !isEditingTests"
                @click="startEditingTests"
                class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-orange-600 bg-orange-100 rounded-lg hover:bg-orange-200 transition-colors"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
                Editar
              </button>
            </div>
            
            <!-- Lista de pruebas -->
            <div class="space-y-2 mb-4">
              <div
                v-for="(test, index) in editedTests"
                :key="index"
                class="flex justify-between items-center bg-white border border-orange-200 rounded-lg p-3"
              >
                <div class="flex items-center gap-3">
                  <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800">
                    {{ test.codigo }}
                  </span>
                  <span class="font-medium text-gray-900">{{ test.nombre }}</span>
                </div>
                <div class="flex items-center gap-3">
                  <div v-if="isEditingTests" class="flex items-center gap-2">
                    <label class="text-sm text-gray-600">Cantidad:</label>
                    <input
                      v-model.number="test.cantidad"
                      type="number"
                      min="1"
                      max="20"
                      class="w-16 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>
                  <div v-else class="text-sm text-gray-600">
                    <span class="font-medium">Cantidad:</span> {{ test.cantidad }}
                  </div>
                  <button
                    v-if="isEditingTests"
                    @click="removeTest(index)"
                    class="text-red-500 hover:text-red-700 p-1"
                    title="Eliminar prueba"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Botones de edición -->
            <div v-if="isEditingTests" class="flex gap-2 mb-4">
              <BaseButton
                variant="outline"
                size="sm"
                text="Guardar Cambios"
                @click="saveTestChanges"
                custom-class="bg-white border-green-600 text-green-600 hover:bg-green-50"
              />
              <BaseButton
                variant="outline"
                size="sm"
                text="Cancelar"
                @click="cancelTestEditing"
                custom-class="bg-white border-gray-600 text-gray-600 hover:bg-gray-50"
              />
            </div>

            <!-- Motivo de la solicitud -->
            <div>
              <h5 class="text-sm font-medium text-gray-700 mb-2">Motivo de la Solicitud</h5>
              <div class="bg-white border border-orange-200 rounded-lg p-3">
                <p class="text-gray-900">{{ approvalCase?.aprobacion_info?.motivo || 'Sin motivo especificado' }}</p>
              </div>
            </div>
          </div>

          <!-- Información de aprobación (si existe) -->
          <div v-if="approvalCase?.aprobacion_info?.fecha_aprobacion" class="bg-gray-50 rounded-xl p-4">
            <h4 class="text-lg font-medium text-gray-900 mb-3">Información de Aprobación</h4>
            <div>
              <p class="text-sm text-gray-500">Fecha de aprobación</p>
              <p class="font-medium text-gray-900">{{ formatDate(approvalCase.aprobacion_info.fecha_aprobacion) }}</p>
            </div>
          </div>
        </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <PrintPdfButton text="Imprimir PDF" :caseCode="approvalCase?.caso_original" />
        <CloseButton
          @click="$emit('close')"
          variant="danger-outline"
          size="md"
          text="Cerrar"
        />
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { CloseButton, PrintPdfButton } from '@/shared/components/buttons'
import { Modal } from '@/shared/components/layout'
import casesApiService from '@/modules/cases/services/casesApi.service'
import casoAprobacionService from '@/modules/results/services/casoAprobacion.service'
import type { CasoAprobacionResponse } from '@/modules/results/services/casoAprobacion.service'

// Props
interface Props {
  approvalCase: CasoAprobacionResponse | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'tests-updated', tests: Array<{ codigo: string; nombre: string; cantidad: number }>): void
}>()

// Estado del modal principal
const isOpen = computed(() => !!props.approvalCase)

// Estado del componente
const originalCase = ref<any>(null)
const loadingOriginalCase = ref(false)
const originalCaseError = ref('')


// Estado para edición de pruebas
const isEditingTests = ref(false)
const editedTests = ref<Array<{ codigo: string; nombre: string; cantidad: number }>>([])
const originalTests = ref<Array<{ codigo: string; nombre: string; cantidad: number }>>([])

// Cargar información del caso original
const loadOriginalCase = async () => {
  if (!props.approvalCase?.caso_original) return
  
  loadingOriginalCase.value = true
  originalCaseError.value = ''
  
  try {
    originalCase.value = await casesApiService.getCaseByCode(props.approvalCase.caso_original)
  } catch (error: any) {
    originalCaseError.value = error.message || 'Error al cargar información del caso original'
  } finally {
    loadingOriginalCase.value = false
  }
}

// Computed properties
const canEditTests = computed(() => {
  return props.approvalCase?.estado_aprobacion === 'solicitud_hecha'
})

// Watchers
watch(() => props.approvalCase, (newCase) => {
  if (newCase) {
    loadOriginalCase()
    // Inicializar pruebas para edición
    editedTests.value = [...(newCase.pruebas_complementarias || [])]
    originalTests.value = [...(newCase.pruebas_complementarias || [])]
    isEditingTests.value = false
  }
}, { immediate: true })

// Funciones utilitarias
const formatDate = (dateValue: any): string => {
  if (!dateValue) return 'N/A'
  
  try {
    let dateToFormat: Date
    
    // Si es un objeto con $date (formato MongoDB)
    if (typeof dateValue === 'object' && dateValue.$date) {
      dateToFormat = new Date(dateValue.$date)
    }
    // Si es un string o número
    else if (typeof dateValue === 'string' || typeof dateValue === 'number') {
      dateToFormat = new Date(dateValue)
    }
    // Si ya es un objeto Date
    else if (dateValue instanceof Date) {
      dateToFormat = dateValue
    }
    else {
      return 'Formato no válido'
    }
    
    // Verificar si la fecha es válida
    if (isNaN(dateToFormat.getTime())) {
      return 'Fecha inválida'
    }
    
    return dateToFormat.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return 'Error de formato'
  }
}

const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'solicitud_hecha': return 'Solicitud Hecha'
    case 'pendiente_aprobacion': return 'Pendiente de Aprobación'
    case 'aprobado': return 'Aprobado'
    case 'rechazado': return 'Rechazado'
    default: return status
  }
}



// Funciones para edición de pruebas
const startEditingTests = () => {
  isEditingTests.value = true
}

const removeTest = (index: number) => {
  editedTests.value.splice(index, 1)
}

const saveTestChanges = async () => {
  if (!props.approvalCase) return
  
  try {
    // Validar que al menos quede una prueba
    if (editedTests.value.length === 0) {
      alert('Debe mantener al menos una prueba complementaria')
      return
    }
    
    // Validar cantidades
    const invalidTest = editedTests.value.find(test => test.cantidad < 1 || test.cantidad > 20)
    if (invalidTest) {
      alert('Las cantidades deben estar entre 1 y 20')
      return
    }
    
    // Obtener el caso_original
    const casoOriginal = props.approvalCase?.caso_original || ''
    
    if (!casoOriginal) {
      alert('Error: No se pudo obtener el código del caso original')
      return
    }
    
    // Actualizar las pruebas en el backend
    await casoAprobacionService.updatePruebasComplementarias(
      casoOriginal, 
      editedTests.value
    )
    
    // Actualizar el estado local
    originalTests.value = [...editedTests.value]
    isEditingTests.value = false
    
    // Emitir evento para que el componente padre actualice
    emit('tests-updated', editedTests.value)
    
  } catch (error) {
    alert('Error al guardar los cambios. Intente nuevamente.')
  }
}

const cancelTestEditing = () => {
  editedTests.value = [...originalTests.value]
  isEditingTests.value = false
}

</script>
