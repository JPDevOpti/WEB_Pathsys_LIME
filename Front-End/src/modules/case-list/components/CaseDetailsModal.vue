<template>
  <transition enter-active-class="transition ease-out duration-300" enter-from-class="opacity-0 transform scale-95" enter-to-class="opacity-100 transform scale-100" leave-active-class="transition ease-in duration-200" leave-from-class="opacity-100 transform scale-100" leave-to-class="opacity-0 transform scale-95">
    <div
      v-if="caseItem"
      :class="[
        'fixed right-0 bottom-0 z-[9999] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/40',
        // Offset por header
        'top-16', // ~64px
        // Offset por sidebar en desktop
        overlayLeftClass
      ]"
      @click.self="$emit('close')"
    >
      <div class="relative bg-white w-full max-w-4xl rounded-t-2xl sm:rounded-2xl shadow-2xl h-[85vh] sm:h-auto sm:max-h-[90vh] overflow-y-auto overflow-x-hidden">
        <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900">Detalles del Caso</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="p-6 space-y-6">
          <div class="grid grid-cols-2 gap-4 bg-gray-50 rounded-xl p-4">
            <div>
              <p class="text-sm text-gray-500">Código del Caso</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.caseCode || caseItem?.id || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Estado</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.status || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Nombre del Paciente</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.patient?.fullName || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Documento de Identidad</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.patient?.id || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Edad</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.patient?.age ? `${caseItem.patient.age} años` : 'No especificada' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Sexo</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.patient?.sex || 'No especificado' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Tipo de Atención</p>
              <p class="text-base font-medium text-gray-900 capitalize">{{ caseItem?.patient?.attentionType || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Entidad</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.patient?.entity || 'No especificada' }}</p>
            </div>
          </div>

          <div class="grid grid-cols-4 gap-4 bg-gray-50 rounded-xl p-4">
            <div>
              <p class="text-sm text-gray-500">Fecha de Creación</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.receivedAt ? formatDate(caseItem.receivedAt) : 'N/A' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Fecha de Firma</p>
              <p class="text-base font-medium text-gray-900">{{ (caseItem?.signedAt || caseItem?.deliveredAt) ? formatDate((caseItem?.signedAt || caseItem?.deliveredAt) as string) : 'Pendiente' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Prioridad</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.priority || 'Normal' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Patólogo Asignado</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem?.pathologist || 'Sin asignar' }}</p>
            </div>
          </div>

          <div class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-sm font-medium text-gray-700">Muestras y Pruebas</h5>
            <div v-if="caseItem?.subsamples && caseItem.subsamples.length" class="space-y-3">
              <div v-for="(muestra, mIdx) in caseItem.subsamples" :key="mIdx" class="border border-gray-200 rounded-lg p-3 bg-white">
                <div class="flex items-center justify-between mb-2">
                  <p class="text-sm text-gray-600">Región del cuerpo</p>
                  <p class="text-sm font-medium text-gray-900">{{ muestra.bodyRegion || 'No especificada' }}</p>
                </div>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(prueba, pIdx) in muestra.tests"
                    :key="pIdx"
                    class="relative inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs pl-2 pr-6 py-0.5 rounded border text-nowrap"
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
            <div v-else class="text-sm text-gray-500">Sin muestras registradas</div>
          </div>

          <div v-if="caseItem?.result && (caseItem.result.method || caseItem.result.macro || caseItem.result.micro || caseItem.result.diagnosis)" class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-sm font-medium text-gray-700">Resultado del Informe</h5>
            
            <!-- Método -->
            <div v-if="caseItem.result.method" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Método</p>
              </div>
              <p class="text-sm font-medium text-gray-900 break-words">{{ caseItem.result.method }}</p>
            </div>

            <!-- Resultado Macroscópico -->
            <div v-if="caseItem.result.macro" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Resultado Macroscópico</p>
              </div>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.result.macro }}</p>
            </div>

            <!-- Resultado Microscópico -->
            <div v-if="caseItem.result.micro" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Resultado Microscópico</p>
              </div>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.result.micro }}</p>
            </div>

            <!-- Diagnóstico -->
            <div v-if="caseItem.result.diagnosis" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Diagnóstico</p>
              </div>
              <p class="text-sm text-gray-800 break-words">{{ caseItem.result.diagnosis }}</p>
            </div>
          </div>

          <!-- Nueva sección para diagnósticos CIE-10 y CIE-O -->
          <div v-if="caseItem?.result && (caseItem.result.diagnostico_cie10 || caseItem.result.diagnostico_cieo)" class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-sm font-medium text-gray-700">Diagnósticos Clasificados</h5>
            
            <!-- Diagnóstico CIE-10 -->
            <div v-if="caseItem.result.diagnostico_cie10" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="flex items-center gap-2 mb-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  CIE-10
                </span>
                <span class="text-sm font-mono text-gray-600">{{ caseItem.result.diagnostico_cie10.codigo }}</span>
              </div>
              <p class="text-sm text-gray-800">{{ caseItem.result.diagnostico_cie10.nombre }}</p>
            </div>

            <!-- Diagnóstico CIE-O -->
            <div v-if="caseItem.result.diagnostico_cieo" class="border border-gray-200 rounded-lg p-3 bg-white">
              <div class="flex items-center gap-2 mb-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  CIE-O
                </span>
                <span class="text-sm font-mono text-gray-600">{{ caseItem.result.diagnostico_cieo.codigo }}</span>
              </div>
              <p class="text-sm text-gray-800">{{ caseItem.result.diagnostico_cieo.nombre }}</p>
            </div>
          </div>

          <!-- Sección para notas adicionales -->
          <div v-if="props.caseItem?.status === 'Completado'" class="bg-gray-50 rounded-xl p-4 space-y-3">
            <div class="flex items-center gap-2 mb-3">
              <DocsIcon class="w-4 h-4 text-gray-600" />
              <h5 class="text-sm font-medium text-gray-700">Notas Adicionales</h5>
              <span v-if="props.caseItem?.notas_adicionales && props.caseItem.notas_adicionales.length > 0" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {{ props.caseItem.notas_adicionales.length }} {{ props.caseItem.notas_adicionales.length === 1 ? 'nota' : 'notas' }}
              </span>
            </div>
            
            <!-- Mostrar notas existentes -->
            <div v-if="props.caseItem?.notas_adicionales && props.caseItem.notas_adicionales.length > 0" class="space-y-3">
              <div v-for="(nota, index) in props.caseItem.notas_adicionales" :key="index" class="border border-gray-200 rounded-lg p-3 bg-white shadow-sm">
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-600 font-medium">{{ formatDate(nota.fecha, true) }}</span>
                    <span class="text-xs text-gray-400">•</span>
                    <span v-if="nota.agregado_por" class="text-xs text-gray-500">{{ nota.agregado_por }}</span>
                  </div>
                  <span class="text-xs text-gray-400">#{{ index + 1 }}</span>
                </div>
                <p class="text-sm text-gray-800 break-words leading-relaxed">{{ nota.nota }}</p>
              </div>
            </div>
            
            <!-- Mensaje cuando no hay notas -->
            <div v-else class="text-center py-4">
              <DocsIcon class="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p class="text-sm text-gray-500">No hay notas adicionales para este caso</p>
              <p class="text-xs text-gray-400 mt-1">Puedes agregar notas usando el botón "Notas adicionales"</p>
            </div>
          </div>
        </div>
        <div class="sticky bottom-0 bg-white border-t border-gray-200 px-4 sm:px-6 py-3 sm:py-4 rounded-b-2xl">
          <div class="flex justify-end">
            <div class="flex gap-2">
              <PreviewButton 
                v-if="props.caseItem?.status === 'Completado'" 
                :text="props.caseItem?.notas_adicionales && props.caseItem.notas_adicionales.length > 0 ? `Notas adicionales (${props.caseItem.notas_adicionales.length})` : 'Notas adicionales'" 
                :icon="DocsIcon"
                @click="handleNotesClick" 
              />
              <PreviewButton text="Previsualizar Informe" @click="caseItem && $emit('preview', caseItem)" />
              <PreviewButton text="Editar Caso" :icon="SettingsIcon" @click="caseItem && $emit('edit', caseItem)" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
  
  <!-- Modal de notas adicionales -->
  <NotesDialog
    v-model="showNotesDialog"
    title="Notas adicionales"
    subtitle="Agregar información complementaria al caso"
    textarea-label="Nueva nota"
    textarea-placeholder="Escriba aquí la nueva nota adicional para este caso..."
    help-text="Esta información será agregada al caso como nota adicional con fecha y hora actual"
    confirm-text="Agregar nota"
    cancel-text="Cancelar"
    @confirm="handleNotesConfirm"
    @cancel="handleNotesCancel"
  />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Case } from '../types/case.types'
import { PreviewButton } from '@/shared/components/buttons'
import { useSidebar } from '@/shared/composables/SidebarControl'
import { SettingsIcon, DocsIcon } from '@/assets/icons'
import { NotesDialog } from '@/shared/components/feedback'
import { casesApiService } from '@/modules/cases/services/casesApi.service'
import { useNotifications } from '@/modules/cases/composables/useNotifications'

const props = defineProps<{ caseItem: Case | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'edit', c: Case): void; (e: 'preview', c: Case): void; (e: 'notes', c: Case): void }>()

const showNotesDialog = ref(false)
const { showSuccess, showError } = useNotifications()

function formatDate(dateString: string, includeTime: boolean = false) {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  
  if (includeTime) {
    return d.toLocaleString('es-ES', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function handleNotesClick() {
  if (!props.caseItem) {
    return
  }
  
  showNotesDialog.value = true
}

async function handleNotesConfirm(notes: string) {
  try {
    const caseCode = props.caseItem?.caseCode || (props.caseItem as any)?.caso_code
    if (!caseCode) {
      showError('Error', 'No se pudo identificar el caso')
      return
    }

    await casesApiService.addAdditionalNote(caseCode, notes, 'Usuario')
    showSuccess('Nota agregada', 'La nota adicional se ha guardado exitosamente')
    showNotesDialog.value = false
    
    // Crear la nueva nota localmente sin recargar todo el caso
    const nuevaNota = {
      fecha: new Date().toISOString(),
      nota: notes,
      agregado_por: 'Usuario'
    }
    
    // Actualizar solo las notas adicionales localmente
    const casoActualizado = {
      ...props.caseItem,
      notas_adicionales: [
        ...(props.caseItem?.notas_adicionales || []),
        nuevaNota
      ]
    }
    
    // Emitir evento con solo la información de las notas actualizadas
    emit('notes', casoActualizado as any)
  } catch (error: any) {
    showError('Error', error.message || 'No se pudo guardar la nota adicional')
  }
}

function handleNotesCancel() {
  showNotesDialog.value = false
}

// Ajuste responsivo: respetar ancho del sidebar (colapsado/expandido) y su hover
const { isExpanded, isMobileOpen, isHovered } = useSidebar()

// En desktop (>= lg), cuando el sidebar está expandido u hovered, dejamos margen izquierdo ~18rem (w-72)
// Cuando está colapsado, dejamos ~5rem (w-20)
// En móvil, sidebar es overlay, así que sin margen (left: 0)
const overlayLeftClass = computed(() => {
  // Tailwind usa breakpoints; aquí usamos clases utilitarias fijas para left dinámico vía clases condicionales
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})
</script>


