<template>
  <ComponentCard title="Creación de usuarios" description="Seleciona una pestaña para crear un usuario." :dense="true">
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h8m4-7v3m0 0h3m-3 0h-3" />
      </svg>
    </template>
    <!-- Tabs de tipos -->
    <div class="border-b border-gray-200 mb-1">
      <nav class="-mb-px flex flex-wrap gap-1 md:gap-4" aria-label="Tabs">
        <button
          v-for="t in tabs"
          :key="t.value"
          type="button"
          class="whitespace-nowrap py-1 px-1 md:px-1 border-b-2 font-medium text-xs md:text-sm"
          :class="selectedType === t.value
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          @click="selectType(t.value)"
        >
          {{ t.label }}
        </button>
      </nav>
    </div>

    <!-- Contenido: formulario a ancho completo -->
    <FormAuxiliary
      v-if="selectedType === 'auxiliar'"
      v-model="formAuxiliar"
      @usuario-creado="forwardCreated('auxiliar', $event)"
    />
    <FormBilling
      v-else-if="selectedType === 'facturacion'"
      v-model="formFacturacion"
      @usuario-creado="forwardCreated('facturacion', $event)"
    />
    <FormPathologist
      v-else-if="selectedType === 'patologo'"
      v-model="formPatologo"
      @usuario-creado="forwardCreated('patologo', $event)"
    />
    <FormResident
      v-else-if="selectedType === 'residente'"
      v-model="formResident"
      @usuario-creado="forwardCreated('residente', $event)"
    />
    <FormEntity
      v-else-if="selectedType === 'entidad'"
      v-model="formEntidad"
      @usuario-creado="forwardCreated('entidad', $event)"
    />
    <FormTests
      v-else-if="selectedType === 'pruebas'"
      v-model="formPruebas"
      @usuario-creado="forwardCreated('pruebas', $event)"
    />
  </ComponentCard>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ComponentCard } from '@/shared/components/common'
import FormAuxiliary from './FormAuxiliary.vue'
import FormBilling from './FormBilling.vue'
import FormPathologist from './FormPathologist.vue'
import FormResident from './FormResident.vue'
import FormEntity from './FormEntity.vue'
import FormTests from './FormTests.vue'

type UserType = 'auxiliar' | 'facturacion' | 'patologo' | 'residente' | 'entidad' | 'pruebas'

const emit = defineEmits<{
  (e: 'usuario-creado', payload: { tipo: UserType; data: any }): void
  (e: 'foto-seleccionada', file: File): void
}>()

const tabs = [
  { value: 'auxiliar', label: 'Auxiliar administrativo' },
  { value: 'facturacion', label: 'Facturación' },
  { value: 'patologo', label: 'Patólogo' },
  { value: 'residente', label: 'Residente' },
  { value: 'entidad', label: 'Entidad' },
  { value: 'pruebas', label: 'Pruebas' }
] as const

const selectedType = ref<UserType>('auxiliar')

// Formularios locales - iniciados vacíos
const formAuxiliar = ref({ auxiliarName: '', auxiliarCode: '', AuxiliarEmail: '', password: '', observaciones: '', isActive: true })
const formFacturacion = ref({ facturacionName: '', facturacionCode: '', FacturacionEmail: '', password: '', observaciones: '', isActive: true })
const formPatologo = ref({ patologoName: '', InicialesPatologo: '', patologoCode: '', PatologoEmail: '', registro_medico: '', password: '', observaciones: '', isActive: true, firma: '' })
const formResident = ref({ residenteName: '', InicialesResidente: '', residenteCode: '', ResidenteEmail: '', registro_medico: '', password: '', observaciones: '', isActive: true })
const formEntidad = ref({ entityName: '', entityCode: '', notes: '', isActive: true })
const formPruebas = ref({ testCode: '', testName: '', testDescription: '', timeDays: 1, price: 0, isActive: true })

// Labels por tipo (reserva para futuros encabezados contextuales)
// Nota: reservado por si se muestra encabezado contextual en el futuro
// const creationTitle = computed(() => {
//   const labels: Record<UserType, string> = { auxiliar: 'Auxiliar administrativo', patologo: 'Patólogo', entidad: 'Entidad', pruebas: 'Pruebas' }
//   return labels[selectedType.value]
// })

const selectType = (type: UserType) => { selectedType.value = type }
const forwardCreated = (tipo: UserType, data: any) => {
  emit('usuario-creado', { tipo, data })
  // limpiar formulario del tipo actual
  if (tipo === 'auxiliar') formAuxiliar.value = { auxiliarName: '', auxiliarCode: '', AuxiliarEmail: '', password: '', observaciones: '', isActive: true }
  if (tipo === 'facturacion') formFacturacion.value = { facturacionName: '', facturacionCode: '', FacturacionEmail: '', password: '', observaciones: '', isActive: true }
  if (tipo === 'patologo') formPatologo.value = { patologoName: '', InicialesPatologo: '', patologoCode: '', PatologoEmail: '', registro_medico: '', password: '', observaciones: '', isActive: true, firma: '' }
  if (tipo === 'residente') formResident.value = { residenteName: '', InicialesResidente: '', residenteCode: '', ResidenteEmail: '', registro_medico: '', password: '', observaciones: '', isActive: true }
  if (tipo === 'entidad') formEntidad.value = { entityName: '', entityCode: '', notes: '', isActive: true }
  if (tipo === 'pruebas') formPruebas.value = { testCode: '', testName: '', testDescription: '', timeDays: 1, price: 0, isActive: true }
}
</script>


