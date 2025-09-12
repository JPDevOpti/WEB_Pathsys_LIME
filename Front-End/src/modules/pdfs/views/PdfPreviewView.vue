<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="`Previsualizador de PDF - ${caseCode || 'Caso'}`" />
    <div class="p-6">
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-xl font-semibold text-gray-800">
            Previsualizador de PDF - {{ caseCode || 'Caso' }}
          </h1>
          <div class="flex gap-2">
            <BaseButton 
              variant="outline" 
              size="sm" 
              text="Volver" 
              @click="goBack"
              :disabled="loading"
            />
            <BaseButton 
              variant="primary" 
              size="sm" 
              :text="loading ? 'Cargando...' : 'Descargar'"
              @click="downloadPdf"
              :disabled="loading || !caseCode"
            />
          </div>
        </div>
        
        <!-- Loading state -->
        <div v-if="loading" class="h-[calc(100vh-260px)] flex items-center justify-center">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Generando PDF...</p>
          </div>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="h-[calc(100vh-260px)] flex items-center justify-center text-red-600 border border-red-200 rounded-lg bg-red-50">
          <div class="text-center">
            <svg class="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="font-medium">{{ error }}</p>
            <button 
              @click="loadPdf" 
              class="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Reintentar
            </button>
          </div>
        </div>
        
        <!-- PDF viewer -->
        <div v-else-if="pdfUrl" class="border border-gray-300 rounded-lg overflow-hidden">
          <iframe 
            :src="pdfUrl" 
            class="w-full h-[calc(100vh-260px)]"
            frameborder="0"
          ></iframe>
        </div>
        
        <!-- No case code -->
        <div v-else class="h-96 flex items-center justify-center text-gray-400 border border-dashed border-gray-300 rounded-lg bg-gray-50">
          <div class="text-center">
            <svg class="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>No se ha especificado un código de caso</p>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { AdminLayout } from '@/shared/components/layout'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import { BaseButton } from '@/shared/components'
import { PdfService } from '../services/pdfService'

const router = useRouter()
const route = useRoute()

const caseCode = ref<string | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const pdfUrl = ref<string | null>(null)

onMounted(() => {
  caseCode.value = route.params.caseCode as string || null
  if (caseCode.value) {
    loadPdf()
  }
})

onUnmounted(() => {
  if (pdfUrl.value) {
    URL.revokeObjectURL(pdfUrl.value)
  }
})

async function loadPdf() {
  if (!caseCode.value) return
  
  loading.value = true
  error.value = null
  
  try {
    const pdfBlob = await PdfService.getCasePdf(caseCode.value)
    
    // Revoke previous URL if exists
    if (pdfUrl.value) {
      URL.revokeObjectURL(pdfUrl.value)
    }
    
    // Create new URL for the PDF blob
    pdfUrl.value = URL.createObjectURL(pdfBlob)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error al cargar el PDF'
  } finally {
    loading.value = false
  }
}

async function downloadPdf() {
  if (!caseCode.value) return
  
  try {
    await PdfService.downloadCasePdf(caseCode.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error al descargar el PDF'
  }
}

function goBack() {
  router.back()
}
</script>