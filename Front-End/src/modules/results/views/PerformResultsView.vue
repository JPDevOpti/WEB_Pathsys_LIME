<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="pageTitle" />
    <PerformResults :sample-id="sampleId" :auto-search="autoSearch" />
  </AdminLayout>
  
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { AdminLayout } from '@/shared/components/layout'
import PageBreadcrumb from '@/shared/components/ui/navigation/PageBreadcrumb.vue'
import { PerformResults } from '../components'

const pageTitle = 'Realizar Resultados'

const route = useRoute()
const sampleId = computed(() => {
  // Aceptar tanto 'muestraId' como 'case' para compatibilidad
  return (route.query.muestraId as string) || (route.query.case as string) || ''
})

const autoSearch = computed(() => {
  // Detectar si debe hacer búsqueda automática
  return route.query.auto === '1' && !!sampleId.value
})
</script>


