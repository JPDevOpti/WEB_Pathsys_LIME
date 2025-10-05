<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div class="space-y-6">
        <ComponentCard 
          title="Modificar técnica complementaria"
          description="Modifique técnicas complementarias existentes en el sistema."
        >
          <template #icon>
            <EditIcon class="w-5 h-5 mr-2 text-blue-600" />
          </template>
          <EditComplementaryTechnique />
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
          <CreateComplementaryTechnique />
        </ComponentCard>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import { DocumentNewIcon, EditIcon } from '@/assets/icons'
import { CreateComplementaryTechnique, EditComplementaryTechnique } from '../components'

const currentPageTitle = ref('Técnicas Complementarias')
</script>


