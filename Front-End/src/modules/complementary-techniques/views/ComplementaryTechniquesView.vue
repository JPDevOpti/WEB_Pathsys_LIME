<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <!-- Main list (frontend-only) -->
    <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Listado de técnicas complementarias</h3>
        <button class="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" @click="openCreateModal">Nueva técnica</button>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Fecha</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">N° Caso</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Paciente</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Institución</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Placas recibe</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Recibo</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="item in items" :key="item.id">
              <td class="px-3 py-2 text-sm text-gray-700">{{ item.date }}</td>
              <td class="px-3 py-2 text-sm text-gray-700">{{ item.caseNumber }}</td>
              <td class="px-3 py-2 text-sm text-gray-700">{{ item.patientName }}</td>
              <td class="px-3 py-2 text-sm text-gray-700">{{ item.institution }}</td>
              <td class="px-3 py-2 text-sm text-gray-700">{{ item.receivedSlidesCount }}</td>
              <td class="px-3 py-2 text-sm text-gray-700">{{ item.receiptStatus }}</td>
              <td class="px-3 py-2 text-sm">
                <button class="px-2 py-1 text-blue-600 hover:text-blue-800" @click="openEditModal(item)">Editar</button>
              </td>
            </tr>
            <tr v-if="items.length === 0">
              <td colspan="7" class="px-3 py-3 text-center text-gray-500">No hay registros. Cree una nueva técnica.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Side-by-side cards -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div class="space-y-6">
        <ComponentCard 
          title="Modificar técnica complementaria"
          description="Modifique técnicas complementarias existentes en el sistema."
        >
          <template #icon>
            <EditIcon class="w-5 h-5 mr-2 text-blue-600" />
          </template>
          <div v-if="selected">
            <EditComplementaryTechnique v-model="selected" @saved="onEdited" />
          </div>
          <p v-else class="text-gray-500">Seleccione un registro del listado para editarlo.</p>
        </ComponentCard>
      </div>
      
      <div class="space-y-6">
        <ComponentCard 
          title="Crear nueva técnica complementaria"
          description="Registre una nueva técnica complementaria para casos patológicos."
        >
          <template #icon>
            <DocumentNewIcon class="w-5 h-5 mr-2 text-blue-600" />
          </template>
          <CreateComplementaryTechnique @created="onCreated" />
        </ComponentCard>
      </div>
    </div>

    <!-- Create Modal -->
    <Modal v-model="showCreate" title="Nueva técnica complementaria" :content-padding="'md'" :size="'xl'">
      <CreateComplementaryTechnique @created="onCreatedFromModal" />
    </Modal>

    <!-- Edit Modal -->
    <Modal v-model="showEdit" title="Editar técnica complementaria" :content-padding="'md'" :size="'xl'">
      <div v-if="selected">
        <EditComplementaryTechnique v-model="selected" @saved="onEditedFromModal" />
      </div>
      <p v-else class="text-gray-500">No hay registro seleccionado.</p>
    </Modal>
  </AdminLayout>
</template>

<script setup lang="ts">
// Imports
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import { Modal } from '@/shared/components/layout'
import { DocumentNewIcon, EditIcon } from '@/assets/icons'
import { CreateComplementaryTechnique, EditComplementaryTechnique } from '../components'
import type { ComplementaryTechnique } from '../types/special-cases.types'

const currentPageTitle = ref('Técnicas Complementarias')

// Local list (frontend only; values shown to user in Spanish)
const items = ref<ComplementaryTechnique[]>([])
const selected = ref<ComplementaryTechnique | null>(null)

// Modal state
const showCreate = ref(false)
const showEdit = ref(false)

// Open/close handlers
const openCreateModal = () => { showCreate.value = true }
const openEditModal = (item: ComplementaryTechnique) => { selected.value = { ...item }; showEdit.value = true }

// Create handlers
const onCreated = (payload: ComplementaryTechnique) => {
  items.value = [payload, ...items.value]
}

const onCreatedFromModal = (payload: ComplementaryTechnique) => {
  items.value = [payload, ...items.value]
  showCreate.value = false
}

// Edit handlers
const onEdited = (payload: ComplementaryTechnique) => {
  if (!selected.value) return
  const index = items.value.findIndex(i => i.id === selected.value!.id)
  if (index !== -1) items.value[index] = { ...payload }
}

const onEditedFromModal = (payload: ComplementaryTechnique) => {
  if (!selected.value) { showEdit.value = false; return }
  const index = items.value.findIndex(i => i.id === selected.value!.id)
  if (index !== -1) items.value[index] = { ...payload }
  showEdit.value = false
}
</script>


