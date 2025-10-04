<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="pageTitle" />
    <ComponentCard 
      title="Listado de Técnicas Complementarias"
      description="Consulta y filtrado de técnicas complementarias.">
      <ComplementaryTechniquesList />
    </ComponentCard>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb, ComponentCard } from '@/shared/components/common'
import ComplementaryTechniquesList from '../components/ComplementaryTechniquesList.vue'

const pageTitle = ref('Técnicas Complementarias - Listado')
</script>


