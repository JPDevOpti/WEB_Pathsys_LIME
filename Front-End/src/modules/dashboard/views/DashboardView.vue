<template>
  <!-- Dashboard layout: KPIs + charts + urgent list -->
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6 p-4 md:p-6 bg-gray-50">
      <!-- Left column: KPIs and monthly cases -->
      <div class="col-span-12 space-y-4 xl:col-span-7">
        <MetricsBlocks />
        <CasesByMonth />
      </div>

      <!-- Right column: opportunity percentage -->
      <div class="col-span-12 xl:col-span-5">
        <OportunityPercentage />
      </div>

      <!-- Full width: urgent cases list -->
      <div class="col-span-12">
        <UrgentCases @show-details="handleShowDetails" />
      </div>
    </div>

    <!-- Details modal controlled by selectedUrgentCase -->
    <UrgentCaseDetailsModal :case-item="selectedUrgentCase" @close="closeUrgentCaseDetails" />
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AdminLayout from '@/shared/layouts/AdminLayout.vue'
import MetricsBlocks from '../components/MetricsBlocks.vue'
import CasesByMonth from '../components/CasesByMonth.vue'
import UrgentCases from '../components/UrgentCases.vue'
import OportunityPercentage from '../components/OportunityPercentage.vue'
import UrgentCaseDetailsModal from '../components/UrgentCaseDetailsModal.vue'
import type { CasoUrgente } from '../types/dashboard.types'
import { useAuthStore } from '@/stores/auth.store'
import { profileApiService } from '@/modules/profile/services/profileApiService'
import { useToasts } from '@/shared/composables/useToasts'
import { useSignatureNotifier } from '@/shared/composables/useSignatureNotifier'

// Currently selected urgent case for the details modal
const selectedUrgentCase = ref<CasoUrgente | null>(null)

const authStore = useAuthStore()
const { warning } = useToasts()
const { checkAndShowOncePerSession, close: closeSignatureNotice } = useSignatureNotifier()

// Open modal with selected urgent case
function handleShowDetails(caso: CasoUrgente) {
  selectedUrgentCase.value = caso
}

// Close modal and clear selection
function closeUrgentCaseDetails() {
  selectedUrgentCase.value = null
}

let isCheckingSignature = false

async function ensureSignatureStatus() {
  if (isCheckingSignature) return
  const user = authStore.user as any
  const isPathologistRef = authStore.isPathologist as any
  const isPathologist = typeof isPathologistRef === 'object' && isPathologistRef !== null && 'value' in isPathologistRef
    ? Boolean(isPathologistRef.value)
    : Boolean(isPathologistRef)
  if (!isPathologist || !user?.pathologist_code) return

  isCheckingSignature = true
  try {
    console.log('[Dashboard] Verificando firma digital', {
      pathologistCode: user.pathologist_code,
      hasSignatureLocal: !!(user?.firma || user?.firma_url || user?.signatureUrl || user?.firmaDigital)
    })
    const profile = await profileApiService.getPathologistByCode(user.pathologist_code)
    console.log('[Dashboard] Respuesta profileApiService.getPathologistByCode', profile)
    const rawSignature = (profile?.firma || (profile as any)?.signature || '').toString().trim()

    if (rawSignature) {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const absoluteUrl = rawSignature.startsWith('http') ? rawSignature : `${baseUrl}${rawSignature}`
      user.firma = absoluteUrl
      user.firma_url = absoluteUrl
      user.signatureUrl = absoluteUrl
      user.firmaDigital = absoluteUrl
      try {
        sessionStorage.setItem('signature_url', absoluteUrl)
        localStorage.setItem('signature_url', absoluteUrl)
        sessionStorage.setItem('signature_missing_notified', '1')
      } catch {}
      console.log('[Dashboard] Firma encontrada y sincronizada', absoluteUrl)
      closeSignatureNotice()
    } else {
      console.warn('[Dashboard] Firma no encontrada para el patólogo', user.pathologist_code)
      const alreadyWarned = sessionStorage.getItem('signature_missing_notified')
      delete user.firma
      delete user.firma_url
      delete user.signatureUrl
      delete user.firmaDigital
      try {
        sessionStorage.removeItem('signature_url')
        localStorage.removeItem('signature_url')
        sessionStorage.removeItem('signature_missing_notified')
      } catch {}
      if (!alreadyWarned) {
        warning('generic', 'Firma digital requerida', 'Sube tu firma digital desde tu perfil para poder firmar informes.', 6000)
      }
      checkAndShowOncePerSession()
    }
  } catch (error) {
    console.error('Error verificando firma del patólogo:', error)
  } finally {
    isCheckingSignature = false
  }
}

onMounted(() => {
  console.log('[Dashboard] Mounted, iniciando verificación de firma')
  ensureSignatureStatus()
})

watch(
  () => [
    (authStore.isAuthenticated as any)?.value ?? authStore.isAuthenticated,
    (authStore.user as any)?.pathologist_code,
    authStore.user?.role
  ],
  ([ready, code, role]) => {
    console.log('[Dashboard] Watch auth changes', { ready, code, role })
    if (ready && code && role) ensureSignatureStatus()
  },
  { immediate: true }
)
</script>

<style scoped>
@media (max-width: 768px) {
  .grid {
    gap: 1rem;
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .grid {
    gap: 0.75rem;
    padding: 0.75rem;
  }
}
</style>