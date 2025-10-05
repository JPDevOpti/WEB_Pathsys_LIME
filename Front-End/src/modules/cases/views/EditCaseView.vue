<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="pb-6">
      <EditCase 
        :case-code-prop="caseCodeFromRoute"
        @case-updated="handleCaseUpdated"
      />
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { AdminLayout } from '@/shared'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import { EditCase } from '../components'
import type { CaseModel } from '../types'

const currentPageTitle = ref('Modificar Caso Médico')
const route = useRoute()
const caseCodeFromRoute = computed(() => (Array.isArray(route.params.code) ? route.params.code[0] || '' : (route.params.code as string) || ''))
const currentCase = ref<CaseModel | null>(null)
const handleCaseUpdated = (updatedCase: CaseModel) => { currentCase.value = updatedCase }
</script> 