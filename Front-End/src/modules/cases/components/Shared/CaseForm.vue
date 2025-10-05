<template>
  <div class="overflow-y-auto custom-scrollbar pr-2" style="max-height: 650px;">
    <div class="space-y-6">
      <!-- Entity and care type -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        <EntityList
          v-model="formData.patientEntity"
          label="Entidad del Paciente"
          placeholder="Selecciona la entidad"
          :required="true"
          :auto-load="true"
          :error="validationState?.hasAttemptedSubmit && !formData.patientEntity ? 'La entidad es obligatoria' : ''"
          @entity-selected="(entity: any) => $emit('entitySelected', entity)"
        />
        <FormSelect
          v-model="formData.patientCareType"
          label="Tipo de Atención"
          placeholder="Seleccione el tipo de atención"
          :required="true"
          :options="tipoAtencionOptions"
          :error="validationState?.hasAttemptedSubmit && !formData.patientCareType ? 'Por favor seleccione el tipo de atención' : ''"
        />
      </div>

      <!-- Entry date and priority -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        <FormInputField
          v-model="formData.entryDate"
          label="Fecha de Ingreso"
          type="date"
          :required="true"
          :errors="errors?.entryDate"
          :warnings="warnings?.entryDate"
          help-text="Fecha en que ingresa el caso al sistema"
        />
        <FormSelect
          v-model="formData.casePriority"
          label="Prioridad del Caso"
          placeholder="Seleccione la prioridad"
          :required="true"
          :options="prioridadOptions"
          :error="validationState?.hasAttemptedSubmit && !formData.casePriority ? 'La prioridad es obligatoria' : ''"
          help-text="Nivel de urgencia del caso"
        />
      </div>

      <!-- Requesting physician and service -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        <FormInputField
          v-model="formData.requestingPhysician"
          label="Médico Solicitante"
          placeholder="Ejemplo: Alberto Perez"
          :required="true"
          :max-length="200"
          help-text="Médico solicitante del estudio"
          :errors="getMedicoErrors"
          :only-letters="true"
        />
        <FormInputField
          v-model="formData.service"
          label="Servicio"
          placeholder="Ejemplo: Medicina Interna"
          :required="true"
          :max-length="100"
          help-text="Área de procedencia del caso"
          :errors="getServicioErrors"
        />
      </div>

      <!-- Edit mode fields: Case state and assigned pathologist -->
      <div v-if="editMode" class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        <FormSelect
          :model-value="state"
          @update:model-value="(value: string) => $emit('update:state', value)"
          label="Estado del Caso"
          placeholder="Seleccione el estado"
          :required="true"
          :options="estadoOptions"
          help-text="Estado actual del proceso"
        />
        <PathologistList
          :model-value="assignedPathologist"
          @update:model-value="(value: string) => $emit('update:assignedPathologist', value)"
          label="Patólogo Asignado"
          placeholder="Buscar y seleccionar patólogo"
          :required="false"
          :auto-load="true"
          help-text="Patólogo responsable del caso"
          @pathologist-selected="(pathologist: any) => $emit('pathologistSelected', pathologist)"
        />
      </div>

      <!-- Number of samples (only in create mode) -->
      <div v-if="!editMode" class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        <FormInputField
          v-model.number="formData.numberOfSamples"
          label="Número de Muestras"
          type="number"
          :min="1"
          :required="true"
          :errors="errors?.numberOfSamples"
          :warnings="warnings?.numberOfSamples"
          help-text="Cantidad de submuestras para este caso"
          @input="onNumberOfSamplesChange"
        />
      </div>

      <!-- Samples details -->
      <div v-if="formData.samples && formData.samples.length > 0" class="space-y-4">
        <h3 class="text-lg font-semibold text-gray-800 flex items-center">
          <SampleIcon class="w-5 h-5 mr-2 text-blue-600" />
          Información de Submuestras
        </h3>

        <div class="space-y-6">
          <div 
            v-for="(sample, sampleIndex) in formData.samples" 
            :key="editMode ? sampleIndex : (sample as any).number" 
            class="border border-gray-200 rounded-lg p-4 bg-gray-50"
          >
            <h4 class="font-medium text-gray-700 mb-4">
              Submuestra #{{ editMode ? sampleIndex + 1 : (sample as any).number }}
            </h4>

            <!-- Body region per sample -->
            <div class="mb-4">
              <BodyRegionList
                v-model="(sample as any).bodyRegion"
                label="Región del Cuerpo"
                placeholder="Buscar región del cuerpo..."
                :required="true"
                :auto-load="true"
                :errors="getRegionErrors ? getRegionErrors(sampleIndex) : []"
                help-text="Seleccione la región anatómica de donde proviene la muestra"
              />
            </div>

            <!-- Tests per sample -->
            <div class="space-y-3">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <label class="block text-sm font-medium text-gray-700">Pruebas a realizar</label>
                <div class="self-end sm:self-auto">
                  <AddButton text="Agregar Prueba" @click="onAddTest(sampleIndex)" />
                </div>
              </div>

              <div class="space-y-2">
                <div 
                  v-for="(test, testIndex) in (sample as any).tests" 
                  :key="testIndex" 
                  class="flex flex-col sm:flex-row gap-2 sm:gap-3 items-stretch sm:items-center"
                >
                  <div class="flex-1 min-w-0">
                    <TestList
                      v-model="test.code"
                      :label="`Prueba #${testIndex + 1}`"
                      :placeholder="`Buscar y seleccionar prueba ${testIndex + 1}...`"
                      :required="true"
                      :auto-load="true"
                      :errors="getPruebaErrors ? getPruebaErrors(sampleIndex, testIndex) : []"
                      @test-selected="(t: any) => onTestSelected(sampleIndex, testIndex, t)"
                    />
                  </div>
                  <div class="w-full sm:w-24">
                    <FormInputField 
                      v-model.number="test.quantity" 
                      label="Cantidad" 
                      type="number" 
                      :min="1" 
                      placeholder="Cantidad" 
                    />
                  </div>
                  <div class="flex items-center justify-center sm:justify-start sm:w-10 sm:mt-6">
                    <RemoveButton 
                      @click="onRemoveTest(sampleIndex, testIndex)" 
                      title="Eliminar prueba" 
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Observations -->
      <FormTextarea
        v-model="formData.observations"
        label="Observaciones del caso"
        placeholder="Observaciones adicionales sobre el caso o procedimiento..."
        :rows="3"
        :max-length="500"
        :show-counter="true"
        help-text="Información adicional relevante para el procesamiento del caso"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/ui/forms'
import { AddButton, RemoveButton } from '@/shared/components/ui/buttons'
import { EntityList, TestList, BodyRegionList, PathologistList } from '@/shared/components/ui/lists'
import { SampleIcon } from '@/assets/icons'

const props = withDefaults(defineProps<{
  formData: any
  editMode?: boolean
  validationState?: any
  errors?: any
  warnings?: any
  tipoAtencionOptions: { value: string; label: string }[]
  prioridadOptions: { value: string; label: string }[]
  estadoOptions?: { value: string; label: string }[]
  state?: string
  assignedPathologist?: string
  getMedicoErrors?: string[]
  getServicioErrors?: string[]
  getRegionErrors?: (sampleIndex: number) => string[]
  getPruebaErrors?: (sampleIndex: number, testIndex: number) => string[]
}>(), {
  editMode: false,
  validationState: null,
  errors: () => ({}),
  warnings: () => ({}),
  estadoOptions: () => [],
  state: '',
  assignedPathologist: '',
  getMedicoErrors: () => [],
  getServicioErrors: () => [],
  getRegionErrors: () => () => [],
  getPruebaErrors: () => () => []
})

const emit = defineEmits<{
  (e: 'numberOfSamplesChange', v: number): void
  (e: 'addTest', sampleIndex: number): void
  (e: 'removeTest', sampleIndex: number, testIndex: number): void
  (e: 'testSelected', sampleIndex: number, testIndex: number, t: any): void
  (e: 'entitySelected', entity: any): void
  (e: 'pathologistSelected', pathologist: any): void
  (e: 'update:state', value: string): void
  (e: 'update:assignedPathologist', value: string): void
}>()

const onNumberOfSamplesChange = (value: string) => {
  if (!props.editMode) {
    emit('numberOfSamplesChange', Number(value))
  }
}

const onAddTest = (sampleIndex: number) => emit('addTest', sampleIndex)
const onRemoveTest = (sampleIndex: number, testIndex: number) => emit('removeTest', sampleIndex, testIndex)
const onTestSelected = (sampleIndex: number, testIndex: number, t: any) => emit('testSelected', sampleIndex, testIndex, t)
</script>
