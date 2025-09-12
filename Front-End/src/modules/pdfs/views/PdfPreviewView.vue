<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Previsualizador de PDFs'" />
    <div class="p-6">
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-xl font-semibold text-gray-800">Previsualizador de PDFs</h1>
          <div class="flex gap-2">
            <BaseButton variant="outline" size="sm" text="Volver" @click="goBack" />
            <BaseButton variant="primary" size="sm" text="Descargar" @click="download" />
          </div>
        </div>
        <div class="h-96 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg bg-gray-50">
          Próximamente: aquí se mostrará la vista previa del PDF
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { AdminLayout } from '@/shared/components/layout'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import { BaseButton } from '@/shared/components'

const router = useRouter()

function goBack() {
  router.back()
}

function download() {}
</script>
