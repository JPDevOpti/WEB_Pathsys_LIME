<template>
  <ComponentCard title="Nueva Técnica Complementaria" description="Configure una nueva técnica complementaria para casos existentes.">
    <template #icon>
      <TaskIcon class="w-5 h-5 mr-2 text-blue-600" />
    </template>

    <div class="space-y-6">
      <!-- Información del solicitante -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        <FormInputField 
          v-model="formData.medicoSolicitante" 
          label="Médico Solicitante" 
          placeholder="Médico que solicita la técnica" 
          :required="true" 
          :max-length="100" 
        />
        <FormInputField 
          v-model="formData.departamento" 
          label="Departamento/Servicio" 
          placeholder="Procedencia de la solicitud" 
          :required="false" 
          :max-length="100" 
        />
      </div>

      <!-- Información básica de la prueba -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6">
        <FormSelect 
          v-model="formData.tipoPrueba" 
          label="Tipo de Técnica" 
          placeholder="Seleccione el tipo" 
          :required="true" 
          :options="tipoPruebaOptions" 
        />
        <FormInputField 
          v-model="formData.fechaSolicitud" 
          label="Fecha de Solicitud" 
          type="date" 
          :required="true" 
        />
        <FormSelect 
          v-model="formData.prioridad" 
          label="Prioridad" 
          placeholder="Seleccione prioridad" 
          :required="true" 
          :options="prioridadOptions" 
        />
      </div>

      <!-- Descripción de la prueba -->
      <div>
        <FormTextarea 
          v-model="formData.descripcion" 
          label="Descripción de la Técnica" 
          placeholder="Describa el objetivo y metodología de la técnica..." 
          :rows="3" 
          :max-length="300" 
          :show-counter="true" 
        />
      </div>

      <!-- Configuración de muestras -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6">
        <FormInputField 
          v-model="formData.numeroMuestras" 
          label="Número de Muestras" 
          type="number" 
          :min="1" 
          :max="10" 
          :required="true" 
          help-text="Cantidad de submuestras (máximo 10)" 
          @input="handleNumeroMuestrasChange" 
        />
      </div>

      <!-- Sección de información de submuestras -->
      <div class="space-y-4">
        <h3 class="text-lg font-semibold text-gray-800 flex items-center">
          <TaskIcon class="w-5 h-5 mr-2 text-blue-600" />
          Configuración de Submuestras
        </h3>
        
        <div class="space-y-6">
          <div v-for="(muestra, muestraIndex) in formData.muestras" :key="muestra.numero" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <h4 class="font-medium text-gray-700 mb-4">Submuestra {{ muestra.numero }}</h4>
            
            <!-- Selección de región del cuerpo -->
            <div class="mb-4">
              <BodyRegionList 
                v-model="muestra.regionCuerpo" 
                :label="`Región del Cuerpo - Submuestra ${muestra.numero}`" 
                placeholder="Buscar región del cuerpo..." 
                :required="true" 
                :auto-load="true" 
                help-text="Seleccione la región anatómica de donde proviene la muestra" 
              />
            </div>
            
            <!-- Configuración de técnicas -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="block text-sm font-medium text-gray-700">Técnicas a Realizar <span class="text-red-500">*</span></label>
                <AddButton text="Agregar Técnica" @click="addPruebaToMuestra(muestraIndex)" />
              </div>
              
              <div class="space-y-2">
                <div v-for="(prueba, pruebaIndex) in muestra.pruebas" :key="pruebaIndex" class="flex flex-col sm:flex-row gap-2 sm:gap-3 items-stretch sm:items-center">
                  <div class="flex-1 min-w-0">
                    <TestList 
                      v-model="prueba.code" 
                      :label="`Técnica ${pruebaIndex + 1}`" 
                      :placeholder="`Buscar y seleccionar técnica ${pruebaIndex + 1}...`" 
                      :required="true" 
                      :auto-load="true" 
                      @test-selected="(test) => handleTestSelected(muestraIndex, pruebaIndex, test)" 
                    />
                  </div>
                  <div class="w-full sm:w-24">
                    <FormInputField 
                      v-model.number="prueba.cantidad" 
                      label="Cantidad" 
                      type="number" 
                      :min="1" 
                      :max="10" 
                      placeholder="Cantidad" 
                    />
                  </div>
                  <div class="flex items-center justify-center sm:justify-start sm:w-10 sm:mt-6">
                    <RemoveButton 
                      v-if="muestra.pruebas.length > 1" 
                      @click="removePruebaFromMuestra(muestraIndex, pruebaIndex)" 
                      title="Eliminar prueba" 
                    />
                  </div>
                </div>
              </div>
            </div>


          </div>
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-gray-200">
        <ClearButton @click="clearForm" />
        <SaveButton text="Guardar Técnica" @click="handleSaveClick" :disabled="!isFormValid" />
      </div>

      <!-- Mensaje de éxito -->
      <div v-if="showSuccessMessage" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <p class="text-sm text-green-600">Prueba complementaria guardada exitosamente (modo visual - sin backend)</p>
        </div>
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { ComponentCard } from '@/shared/components'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton, AddButton, RemoveButton } from '@/shared/components/buttons'
import { TestList, BodyRegionList } from '@/shared/components/List'
import { TaskIcon } from '@/assets/icons'

// ============================================================================
// INTERFACES Y TIPOS
// ============================================================================

interface PruebaComplementaria {
  code: string
  cantidad: number
  nombre: string
}

interface MuestraComplementaria {
  numero: number
  regionCuerpo: string
  pruebas: PruebaComplementaria[]
}

interface FormDataComplementaria {
  tipoPrueba: string
  descripcion: string
  numeroMuestras: string
  fechaSolicitud: string
  prioridad: string
  muestras: MuestraComplementaria[]
  medicoSolicitante: string
  departamento: string
}

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

const showSuccessMessage = ref(false)

const formData = reactive<FormDataComplementaria>({
  tipoPrueba: '',
  descripcion: '',
  numeroMuestras: '1',
  fechaSolicitud: new Date().toISOString().split('T')[0],
  prioridad: '',
  muestras: [{ 
    numero: 1, 
    regionCuerpo: '', 
    pruebas: [{ code: '', cantidad: 1, nombre: '' }]
  }],
  medicoSolicitante: '',
  departamento: ''
})

// ============================================================================
// OPTIONS PARA SELECTS
// ============================================================================

const tipoPruebaOptions = [
  { value: 'inmunohistoquimica', label: 'Inmunohistoquímica' },
  { value: 'biopsia_complementaria', label: 'Biopsia Complementaria' },
  { value: 'citologia_especial', label: 'Citología Especial' },
  { value: 'tincion_especial', label: 'Tinción Especial' },
  { value: 'microscopia_electronica', label: 'Microscopía Electrónica' },
  { value: 'analisis_molecular', label: 'Análisis Molecular' },
  { value: 'cultivo_celular', label: 'Cultivo Celular' }
]

const prioridadOptions = [
  { value: 'baja', label: 'Baja' },
  { value: 'normal', label: 'Normal' },
  { value: 'alta', label: 'Alta' },
  { value: 'urgente', label: 'Urgente' }
]



// ============================================================================
// COMPUTED PROPERTIES
// ============================================================================

const isFormValid = computed(() => {
  return (
    formData.tipoPrueba !== '' &&
    formData.fechaSolicitud !== '' &&
    formData.prioridad !== '' &&
    formData.medicoSolicitante.trim() !== '' &&
    formData.numeroMuestras !== '' &&
    formData.muestras.length > 0 &&
    formData.muestras.every(muestra => 
      muestra.regionCuerpo.trim() !== '' &&
      muestra.pruebas.some(prueba => prueba.code.trim() !== '')
    )
  )
})

// ============================================================================
// FUNCIONES
// ============================================================================

const createEmptySubSample = (numero: number): MuestraComplementaria => ({
  numero, 
  regionCuerpo: '', 
  pruebas: [{ code: '', cantidad: 1, nombre: '' }]
})

const createEmptyTest = (): PruebaComplementaria => ({ 
  code: '', 
  cantidad: 1, 
  nombre: '' 
})

const handleNumeroMuestrasChange = (nuevoNumero: string): void => {
  const numero = parseInt(nuevoNumero)
  if (isNaN(numero) || numero < 1) return
  
  formData.numeroMuestras = nuevoNumero
  
  if (numero > formData.muestras.length) {
    while (formData.muestras.length < numero) {
      formData.muestras.push(createEmptySubSample(formData.muestras.length + 1))
    }
  } else if (numero < formData.muestras.length) {
    formData.muestras = formData.muestras.slice(0, numero)
  }
}

const addPruebaToMuestra = (muestraIndex: number): void => {
  if (muestraIndex >= 0 && muestraIndex < formData.muestras.length) {
    formData.muestras[muestraIndex].pruebas.push(createEmptyTest())
  }
}

const removePruebaFromMuestra = (muestraIndex: number, pruebaIndex: number): void => {
  if (muestraIndex >= 0 && muestraIndex < formData.muestras.length) {
    const muestra = formData.muestras[muestraIndex]
    if (muestra.pruebas.length > 1 && pruebaIndex >= 0 && pruebaIndex < muestra.pruebas.length) {
      muestra.pruebas.splice(pruebaIndex, 1)
    }
  }
}

const handleTestSelected = (muestraIndex: number, pruebaIndex: number, test: any) => {
  if (test && muestraIndex >= 0 && muestraIndex < formData.muestras.length) {
    const muestra = formData.muestras[muestraIndex]
    if (pruebaIndex >= 0 && pruebaIndex < muestra.pruebas.length) {
      muestra.pruebas[pruebaIndex].code = test.pruebaCode || test.code || ''
      muestra.pruebas[pruebaIndex].nombre = test.pruebasName || test.nombre || test.label || ''
    }
  }
}

const clearForm = () => {
  Object.assign(formData, {
    tipoPrueba: '',
    descripcion: '',
    numeroMuestras: '1',
    fechaSolicitud: new Date().toISOString().split('T')[0],
    prioridad: '',
    muestras: [createEmptySubSample(1)],
    medicoSolicitante: '',
    departamento: ''
  })
  showSuccessMessage.value = false
}

const handleSaveClick = () => {
  if (!isFormValid.value) return
  
  // Simular guardado exitoso (sin backend)
  console.log('Datos de la prueba complementaria:', formData)
  showSuccessMessage.value = true
  
  // Ocultar mensaje después de 5 segundos
  setTimeout(() => {
    showSuccessMessage.value = false
  }, 5000)
  
  // Limpiar formulario después del guardado
  setTimeout(() => {
    clearForm()
  }, 2000)
}
</script>
