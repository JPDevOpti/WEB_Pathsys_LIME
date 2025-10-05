<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Nuevo Paciente" />
    <NewPatient />
  </AdminLayout>
</template>

<script setup lang="ts">
import { AdminLayout } from '@/shared'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import { NewPatient } from '../components'
</script>


