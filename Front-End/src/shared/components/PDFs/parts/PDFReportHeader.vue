<template>
  <div class="report-header">
    <table class="w-full text-sm border border-gray-900" style="border-collapse: collapse;">
      <tbody>
        <tr>
          <td class="border border-gray-900 p-2" style="width: 75%; vertical-align: middle;">
            <div class="flex items-center space-x-6">
              <img src="/images/logo/Logo-LIME-NoFondo.png" alt="LIME" class="h-16" />
              <img src="/images/logo/Baner-udea.png" alt="Universidad de Antioquia" class="h-16" />
              <img src="/images/logo/banner_huam.png" alt="Hospital AlmaMáter" class="h-16" />
            </div>
          </td>
          <td class="border border-gray-900 p-2" style="width: 25%; vertical-align: middle;">
            <div class="header-info"><span class="font-semibold">Código:</span> F-025-LIME</div>
            <div class="header-info"><span class="font-semibold">Versión:</span> 05</div>
          </td>
        </tr>
        <tr>
          <td colspan="2" class="border border-gray-900 p-1" style="text-align:center;">
            <div class="header-title">INFORME DE RESULTADOS ANATOMOPATOLÓGICOS</div>
          </td>
        </tr>
      </tbody>
    </table>

    <table class="w-full text-sm border border-gray-900" style="border-collapse: collapse;">
      <tbody>
        <tr>
          <td class="border border-gray-900 p-1" style="width: 70%;">
            <div style="display:flex; align-items:center; gap:8px;">
              <svg class="location-pin" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
              </svg>
              <div class="dept-info">
                <div class="dept-title">Departamento de Patología</div>
                <div class="dept-text">Hospital San Vicente Fundación</div>
                <div class="dept-text">Calle 64 Carrera 51D. Bloque 13</div>
                <div class="dept-text">Tel. 6042192400</div>
              </div>
            </div>
          </td>
          <td class="border border-gray-900 p-0" style="width: 30%; vertical-align: top;">
            <div class="right-info">
              <div class="right-title">Informe No {{ caseItem?.caseDetails?.caso_code || caseItem?.sampleId || '—' }}.</div>
              <div class="right-row"><span class="right-label">Fecha de recibo:</span> {{ formatDate(caseItem?.caseDetails?.fecha_creacion) || '—' }}</div>
              <div class="right-row"><span class="right-label">Fecha de firma:</span> {{ formatDate(caseItem?.caseDetails?.fecha_firma) || '—' }}</div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
interface CaseItem {
  caseDetails?: {
    caso_code?: string
    fecha_ingreso?: string
    fecha_creacion?: string
    fecha_firma?: string
  }
  sampleId?: string
}

defineProps<{
  caseItem?: CaseItem
}>()

const formatDate = (dateString?: string | Date): string => {
  if (!dateString) return '—'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
  } catch {
    return '—'
  }
}
</script>

<style scoped>
.report-header { margin-bottom: 1rem; }
.report-header table { width: 100%; border-collapse: collapse; }
.report-header td { border: 1px solid #111; padding: 0.5rem; vertical-align: middle; }
.report-header img { max-height: 48px; object-fit: contain; }

.location-pin { width: 16px; height: 16px; color: #000; }
.dept-info { line-height: 1.2; }
.dept-title { font-weight: 800; font-size: 12px; color: #0f172a; margin-bottom: 2px; }
.dept-text { font-size: 12px; color: #0f172a; margin-bottom: 1px; }

.header-info { font-size: 12px; color: #0f172a; }
.right-info { display: flex; flex-direction: column; }
.right-title { font-weight: 800; font-size: 12px; padding: 8px 10px; }
.right-row { border-top: 1px solid #111; padding: 8px 10px; font-size: 12px; }
.right-label { font-weight: 700; color: #000; }
.header-title { font-weight: 900; font-size: 16px; letter-spacing: 0.5px; padding: 4px 0; }
</style>
