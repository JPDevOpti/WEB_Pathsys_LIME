<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Editar Paciente" />
    <ComponentCard 
      title="Buscar paciente para editar"
      description="Ingrese documento de identidad del paciente para comenzar a editar"
    >
      <template #icon>
        <SearchPatientIcon class="w-5 h-5 mr-2 text-blue-600" />
      </template>
      <EditPatientForm :case-code-prop="(route.params.code as string) || undefined" />
    </ComponentCard>
  </AdminLayout>
</template>

<script setup lang="ts">
import { AdminLayout } from '@/shared'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import { SearchPatientIcon } from '@/assets/icons'
import { EditPatientForm } from '../components'
import { useRoute } from 'vue-router'

const route = useRoute()
</script>


