<template>
  <ComponentCard title="Edición de usuarios" description="Selecciona una pestaña, busca y edita el perfil." :dense="true">
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 20h9" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M16.5 3.5a2.121 2.121 0 113 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>
    </template>
    <!-- Tabs de tipos -->
    <div class="border-b border-gray-200 mb-1">
      <nav class="-mb-px flex flex-wrap gap-1 md:gap-4" aria-label="Tabs">
        <button v-for="t in tabs" :key="t.value" type="button"
          class="whitespace-nowrap py-1 px-1 md:px-1 border-b-2 font-medium text-xs md:text-sm" :class="selectedType === t.value
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          @click="selectType(t.value)">
          {{ t.label }}
        </button>
      </nav>
    </div>

    <!-- Contenido: buscador, resultados y formulario de edición -->
    <div class="space-y-3 md:space-y-4">
      <div>
        <UserSearch :busqueda="searchQuery" :tipo-busqueda="selectedType" :esta-buscando="isSearching"
          :error="searchError" @buscar="onSearch" @limpiar="onClearSearch" />
      </div>

      <!-- Resultados -->
      <div>
        <SearchResults :resultados="filteredResults" :busqueda-realizada="searchPerformed" :esta-buscando="isSearching"
          :selected-id="selectedUser?.id || ''" @usuario-seleccionado="onSelectUserToEdit" />
      </div>

      <!-- Formulario de edición debajo de resultados para flujo vertical -->
      <div>
        <div v-if="selectedUser">
          <h5 class="text-base font-semibold text-gray-800 dark:text-white/90 mb-4">
            Editando: {{ selectedUser.nombre }}
          </h5>

          <FormEditAuxiliary v-if="selectedUser.tipo === 'auxiliar'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />

          <FormEditBilling v-else-if="selectedUser.tipo === 'facturacion'" v-model="selectedUser"
            @usuario-actualizado="onUpdateUser" />

          <FormEditPathologist v-else-if="selectedUser.tipo === 'patologo'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />

          <FormEditResident v-else-if="selectedUser.tipo === 'residente'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />

          <FormEditEntity v-else-if="selectedUser.tipo === 'entidad'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />

          <FormEditTests v-else-if="selectedUser.tipo === 'pruebas'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />
        </div>

        <div v-if="userUpdated && !selectedUser"
          class="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <p class="text-sm font-medium text-green-800 dark:text-green-200">
            {{ updateSuccessMessage }}
          </p>
        </div>
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ComponentCard } from '@/shared/components/common'
import UserSearch from './UserSearch.vue'
import SearchResults from './SearchResults.vue'
import FormEditAuxiliary from './FormEditAuxiliary.vue'
import FormEditBilling from './FormEditBilling.vue'
import FormEditPathologist from './FormEditPathologist.vue'
import FormEditResident from './FormEditResident.vue'
import FormEditEntity from './FormEditEntity.vue'
import FormEditTests from './FormEditTests.vue'
import { testSearchService } from '../../services/testSearchService'
import { entitySearchService } from '../../services/entitySearchService'

type UserType = 'auxiliar' | 'facturacion' | 'patologo' | 'residente' | 'entidad' | 'pruebas'

const tabs = [
  { value: 'auxiliar', label: 'Auxiliar administrativo' },
  { value: 'facturacion', label: 'Facturación' },
  { value: 'patologo', label: 'Patólogo' },
  { value: 'residente', label: 'Residente' },
  { value: 'entidad', label: 'Entidad' },
  { value: 'pruebas', label: 'Pruebas' }
] as const

const selectedType = ref<UserType>('auxiliar')
const searchQuery = ref('')
const searchPerformed = ref(false)
const isSearching = ref(false)
const searchError = ref('')
const results = ref<any[]>([])

const selectedUser = ref<any | null>(null)
const userUpdated = ref(false)
const updateSuccessMessage = ref('')

const filteredResults = computed(() => {
  return results.value.filter(r => r.tipo === selectedType.value)
})

const selectType = (type: UserType) => {
  selectedType.value = type
  selectedUser.value = null
}

// No precargar datos al abrir la página

const onSearch = async (params: { query: string; tipo: string; includeInactive: boolean }) => {
  searchQuery.value = params.query
  searchPerformed.value = true
  isSearching.value = true
  searchError.value = ''
  
  try {
    console.log('🔍 Iniciando búsqueda con parámetros:', params)
    let searchResults: any[] = []

    if (params.tipo === 'pruebas') {
      searchResults = await testSearchService.searchTests(params.query, params.includeInactive)
    } else if (params.tipo === 'entidad') {
      searchResults = await entitySearchService.searchEntities(params.query, params.includeInactive)
    } else if (params.tipo === 'residente') {
      searchResults = await entitySearchService.searchResidents(params.query, params.includeInactive)
    } else if (params.tipo === 'patologo') {
      searchResults = await entitySearchService.searchPathologists(params.query, params.includeInactive)
    } else if (params.tipo === 'auxiliar') {
      searchResults = await entitySearchService.searchAuxiliaries(params.query, params.includeInactive)
    } else if (params.tipo === 'facturacion') {
      searchResults = await entitySearchService.searchFacturacion(params.query, params.includeInactive)
    } else {
      searchResults = []
    }

    console.log('🔍 Resultados de búsqueda obtenidos:', searchResults)
    results.value = searchResults
    
    if (searchResults.length === 0) {
      const typeLabels = {
        auxiliar: 'auxiliares',
        facturacion: 'usuarios de facturación',
        patologo: 'patólogos', 
        residente: 'residentes',
        entidad: 'entidades',
        pruebas: 'pruebas'
      }
      const typeLabel = typeLabels[params.tipo as keyof typeof typeLabels] || 'registros'
      const statusText = params.includeInactive ? ' (incluyendo inactivos)' : ''
      searchError.value = `No se encontraron ${typeLabel} que coincidan con "${params.query}"${statusText}`
    }
  } catch (error: any) {
    console.error('Error en búsqueda:', error)
    searchError.value = error.message || 'Error al realizar la búsqueda. Por favor, inténtelo nuevamente.'
    results.value = []
  } finally {
    isSearching.value = false
  }
}

const onClearSearch = () => {
  searchQuery.value = ''
  results.value = []
  selectedUser.value = null
  searchError.value = ''
  searchPerformed.value = false
  isSearching.value = false
}

const onSelectUserToEdit = (item: any) => {
  // Mapeo específico según el tipo
  if (item.tipo === 'pruebas') {
    // Mapeo específico para pruebas con estructura del backend
    selectedUser.value = {
      id: item.id,
      nombre: item.nombre,
      tipo: item.tipo,
      codigo: item.codigo,
      activo: item.activo,
      // Campos específicos para pruebas (estructura del FormEditTests)
      pruebaCode: item.test_code || item.codigo,
      pruebasName: item.name || item.nombre,
      pruebasDescription: item.description || item.descripcion || '',
      tiempo: item.time || item.tiempo || 1,
      isActive: item.is_active !== undefined ? item.is_active : item.activo,
      fecha_creacion: item.created_at || item.fecha_creacion,
      fecha_actualizacion: item.updated_at || item.fecha_actualizacion
    }
  } else if (item.tipo === 'entidad') {
    // Mapeo específico para entidades con estructura del formulario de edición
    selectedUser.value = {
      id: item.id,
      nombre: item.nombre,
      tipo: item.tipo,
      codigo: item.codigo,
      activo: item.activo,
      // Campos específicos para entidades
      EntidadName: item.name || item.nombre,
      EntidadCode: item.entity_code || item.codigo,
      observaciones: item.notes || item.observaciones || '',
      isActive: item.is_active !== undefined ? item.is_active : item.activo,
      fecha_creacion: item.created_at || item.fecha_creacion,
      fecha_actualizacion: item.updated_at || item.fecha_actualizacion
    }
  } else if (item.tipo === 'facturacion') {
    // Mapeo específico para facturación con estructura del formulario de edición
    selectedUser.value = {
      id: item.id,
      nombre: item.nombre,
      tipo: item.tipo,
      codigo: item.codigo,
      activo: item.activo,
      email: item.email,
      // Campos específicos para facturación (estructura del FormEditBilling)
      facturacionName: item.billing_name || item.facturacionName || item.nombre,
      facturacionCode: item.billing_code || item.facturacionCode || item.codigo,
      FacturacionEmail: item.billing_email || item.FacturacionEmail || item.email,
      observaciones: item.observations || item.observaciones || '',
      isActive: item.is_active !== undefined ? item.is_active : (item.isActive !== undefined ? item.isActive : item.activo),
      fecha_creacion: item.created_at || item.fecha_creacion,
      fecha_actualizacion: item.updated_at || item.fecha_actualizacion
    }
  } else if (item.tipo === 'residente') {
    // Mapeo específico para residentes con estructura del formulario de edición
    selectedUser.value = {
      id: item.id,
      nombre: item.nombre,
      tipo: item.tipo,
      codigo: item.codigo,
      activo: item.activo,
      email: item.email,
      // Campos específicos para residentes
      residenteName: item.resident_name || item.residenteName || item.nombre,
      residenteCode: item.resident_code || item.residenteCode || item.codigo,
      InicialesResidente: item.initials || item.InicialesResidente || '',
      ResidenteEmail: item.resident_email || item.ResidenteEmail || item.email,
      registro_medico: item.medical_license || item.registro_medico || '',
      observaciones: item.observations || item.observaciones || '',
      isActive: item.is_active !== undefined ? item.is_active : (item.isActive !== undefined ? item.isActive : item.activo),
      fecha_creacion: item.created_at || item.fecha_creacion,
      fecha_actualizacion: item.updated_at || item.fecha_actualizacion
    }
  } else if (item.tipo === 'patologo') {
    // Mapeo específico para patólogos con estructura del formulario de edición
    selectedUser.value = {
      id: item.id,
      nombre: item.nombre,
      tipo: item.tipo,
      codigo: item.codigo,
      activo: item.activo,
      email: item.email,
      // Campos específicos
      patologoName: item.pathologist_name || item.patologoName || item.nombre,
      InicialesPatologo: item.initials || item.InicialesPatologo || '',
      patologoCode: item.pathologist_code || item.patologoCode || item.codigo,
      PatologoEmail: item.pathologist_email || item.PatologoEmail || item.email,
      registro_medico: item.medical_license || item.registro_medico || '',
      observaciones: item.observations || item.observaciones || '',
      isActive: item.is_active !== undefined ? item.is_active : (item.isActive !== undefined ? item.isActive : item.activo),
      fecha_creacion: item.created_at || item.fecha_creacion,
      fecha_actualizacion: item.updated_at || item.fecha_actualizacion
    }
  } else if (item.tipo === 'auxiliar') {
    // Mapeo específico para auxiliares con estructura del formulario de edición
    selectedUser.value = {
      id: item.id,
      nombre: item.nombre,
      tipo: item.tipo,
      codigo: item.codigo,
      activo: item.activo,
      email: item.email,
      auxiliarName: item.auxiliar_name || item.auxiliarName || item.nombre,
      auxiliarCode: item.auxiliar_code || item.auxiliarCode || item.codigo,
      AuxiliarEmail: item.auxiliar_email || item.AuxiliarEmail || item.email,
      observaciones: item.observations || item.observaciones || '',
      isActive: item.is_active !== undefined ? item.is_active : (item.isActive !== undefined ? item.isActive : item.activo),
      fecha_creacion: item.created_at || item.fecha_creacion,
      fecha_actualizacion: item.updated_at || item.fecha_actualizacion
    }
  } else if (item.tipo === 'facturacion') {
    // Mapeo específico para usuarios de facturación con estructura del formulario de edición
    selectedUser.value = {
      id: item.id,
      nombre: item.nombre,
      tipo: item.tipo,
      codigo: item.codigo,
      activo: item.activo,
      email: item.email,
      facturacionName: item.facturacionName || item.nombre,
      facturacionCode: item.facturacionCode || item.codigo,
      FacturacionEmail: item.FacturacionEmail || item.email,
      observaciones: item.observaciones || '',
      isActive: item.isActive !== undefined ? item.isActive : item.activo,
      fecha_creacion: item.fecha_creacion,
      fecha_actualizacion: item.fecha_actualizacion
    }
  } else {
    // Mapeo genérico para otros tipos (mantener estructura existente)
    selectedUser.value = {
      id: item.id,
      nombre: item.nombre,
      tipo: item.tipo,
      documento: item.documento,
      nit: item.nit,
      codigo: item.codigo,
      email: item.email || '',
      activo: item.activo,
      role: item.tipo,
      firstName: item.nombre,
      lastName: '',
      phone: '',
      startDate: '',
      isActive: item.activo,
      specialty: item.descripcion || '',
      medicalLicense: item.licencia || '',
      residencyYear: item.residencyYear || '',
      entityName: item.tipo === 'entidad' ? item.nombre : '',
      entityType: item.categoria || '',
      address: '',
      pruebaCode: item.codigo || '',
      pruebasName: item.nombre,
      pruebasCategory: item.categoria || '',
      pruebasDescription: item.descripcion || '',
      observaciones: item.observaciones || '',
      firmaPatologoUrl: ''
    }
  }
}



const onUpdateUser = (_data: any) => {
  const tipo = selectedUser.value?.tipo
  // Para formularios con notificación detallada interna, no duplicar notificaciones ni cerrar el formulario
  if (tipo === 'pruebas' || tipo === 'entidad' || tipo === 'residente' || tipo === 'auxiliar' || tipo === 'facturacion') {
    // Mantener el formulario visible y no mostrar banner externo
    return
  }
  // Comportamiento previo para otros tipos
  updateSuccessMessage.value = 'Registro actualizado exitosamente'
  userUpdated.value = true
  setTimeout(() => { selectedUser.value = null }, 700)
  setTimeout(() => { userUpdated.value = false; updateSuccessMessage.value = '' }, 3000)
}
</script>
