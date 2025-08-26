<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div class="p-3 sm:p-4 md:p-6">
      <div class="grid grid-cols-1 gap-4 md:gap-6 xl:grid-cols-2">
        <!-- Columna izquierda: Crear -->
        <div class="space-y-4">
                <UserCreationTabs @usuario-creado="onCreateUserFromTabs" @foto-seleccionada="onPhotoSelected" />
        </div>

        <!-- Columna derecha: Editar -->
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

// Componentes de creación
import UserCreationTabs from '../components/SeccionCreacion/UserCreationTabs.vue'

// Componentes de edición
import UserEditionTabs from '../components/SeccionEdicion/UserEditionTabs.vue'

// Estado local (visual-only)
const currentPageTitle = ref('Gestión de Usuarios')
// La creación se maneja dentro de UserCreationTabs



// La edición se maneja dentro de UserEditionTabs

// Handlers (solo visual)
const onPhotoSelected = (_file: File) => {}
const onCreateUserFromTabs = (payload: { tipo: string; data: any }) => {
  // La notificación ahora se maneja dentro de cada formulario individual
  console.log('Usuario creado:', payload)
}

// Eliminada la lógica local de edición en favor de UserEditionTabs
</script>


