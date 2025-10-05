<template>
  <ComponentCard title="Creación de usuarios" description="Seleciona una pestaña para crear un usuario." :dense="true">
    <template #icon>
      <NewUserIcon class="w-5 h-5 mr-2" />
    </template>
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
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import NewUserIcon from '@/assets/icons/NewUserIcon.vue'
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

const formAuxiliar = ref({ auxiliarName: '', auxiliarCode: '', AuxiliarEmail: '', password: '', observaciones: '', isActive: true })
const formFacturacion = ref({ billingName: '', billingCode: '', billingEmail: '', password: '', observations: '', isActive: true })
const formPatologo = ref({ patologoName: '', InicialesPatologo: '', patologoCode: '', PatologoEmail: '', registro_medico: '', password: '', observaciones: '', isActive: true, firma: '' })
const formResident = ref({ residenteName: '', InicialesResidente: '', residenteCode: '', ResidenteEmail: '', registro_medico: '', password: '', observaciones: '', isActive: true })
const formEntidad = ref({ entityName: '', entityCode: '', notes: '', isActive: true })
const formPruebas = ref({ testCode: '', testName: '', testDescription: '', timeDays: 1, price: 0, isActive: true })

const selectType = (type: UserType) => { selectedType.value = type }
const forwardCreated = (tipo: UserType, data: any) => {
  emit('usuario-creado', { tipo, data })
  if (tipo === 'auxiliar') formAuxiliar.value = { auxiliarName: '', auxiliarCode: '', AuxiliarEmail: '', password: '', observaciones: '', isActive: true }
  if (tipo === 'facturacion') formFacturacion.value = { billingName: '', billingCode: '', billingEmail: '', password: '', observations: '', isActive: true }
  if (tipo === 'patologo') formPatologo.value = { patologoName: '', InicialesPatologo: '', patologoCode: '', PatologoEmail: '', registro_medico: '', password: '', observaciones: '', isActive: true, firma: '' }
  if (tipo === 'residente') formResident.value = { residenteName: '', InicialesResidente: '', residenteCode: '', ResidenteEmail: '', registro_medico: '', password: '', observaciones: '', isActive: true }
  if (tipo === 'entidad') formEntidad.value = { entityName: '', entityCode: '', notes: '', isActive: true }
  if (tipo === 'pruebas') formPruebas.value = { testCode: '', testName: '', testDescription: '', timeDays: 1, price: 0, isActive: true }
}
</script>


