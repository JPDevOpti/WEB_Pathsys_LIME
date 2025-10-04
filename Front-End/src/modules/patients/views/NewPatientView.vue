<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Nuevo Paciente" />
    <NewPatient />
  </AdminLayout>
</template>

<script setup lang="ts">
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/common'
import { NewPatient } from '../components'
</script>


