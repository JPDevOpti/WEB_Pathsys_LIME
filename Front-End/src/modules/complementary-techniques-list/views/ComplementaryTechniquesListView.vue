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
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import ComplementaryTechniquesList from '../components/ComplementaryTechniquesList.vue'

const pageTitle = ref('Técnicas Complementarias - Listado')
</script>


