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
      <EditPatientForm />
    </ComponentCard>
  </AdminLayout>
</template>

<script setup lang="ts">
import { AdminLayout } from '@/shared'
import { PageBreadcrumb, ComponentCard } from '@/shared/components/common'
import { SearchPatientIcon } from '@/assets/icons'
import { EditPatientForm } from '../components'
</script>


