<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="p-3 sm:p-4 md:p-6">
      <div class="grid grid-cols-1 gap-4 md:gap-6 xl:grid-cols-2">
        <div class="space-y-4">
          <UserCreationTabs @usuario-creado="onCreateUserFromTabs" @foto-seleccionada="onPhotoSelected" />
        </div>
        <div>
          <UserEditionTabs />
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/common'
import UserCreationTabs from '../components/SeccionCreacion/UserCreationTabs.vue'
import UserEditionTabs from '../components/SeccionEdicion/UserEditionTabs.vue'

const currentPageTitle = ref('Gestión de Usuarios')

const onPhotoSelected = (_file: File) => {}
const onCreateUserFromTabs = (payload: { tipo: string; data: any }) => {
  console.log('Usuario creado:', payload)
}
</script>


