import { computed, ref } from 'vue'
import type { Attachment, Patient, PreviewData, Sample, CaseDetails } from '../types/results.types'
import type { CaseListItem } from '@/modules/cases/types/case'

import casesApiService from '@/modules/cases/services/casesApi.service'
import { mapCaseToPatient, mapCaseToCaseDetails } from '../services/results.mappers'
import resultsApiService from '../services/resultsApiService'
import { useDiseaseDiagnosis } from '@/shared/composables/useDiseaseDiagnosis'
import type { Disease } from '@/shared/services/disease.service'

export function usePerformResults(sampleId: string) {
  const loading = ref(false)
  const saving = ref(false)
  const finalizing = ref(false)
  const previewing = ref(false)

  // Composable para diagnóstico CIE-10
  const {
    primaryDisease,
    hasDisease,
    setPrimaryDisease,
    clearPrimaryDisease,
    clearDiagnosis,
    formatDiagnosisForReport,
    getDiagnosisData,
    validateDiagnosis
  } = useDiseaseDiagnosis()

  // Estado para diagnóstico CIEO
  const primaryDiseaseCIEO = ref<Disease | null>(null)
  const hasDiseaseCIEO = computed(() => !!primaryDiseaseCIEO.value)
  const showCIEODiagnosis = ref(false)

  const sample = ref<Sample | null>(null)
  const patient = ref<Patient | null>(null)
  const previousCases = ref<CaseListItem[]>([])
  const sampleSearchResults = ref<Sample[]>([])
  const caseDetails = ref<CaseDetails | null>(null)
  const selectedTemplateId = ref<string | undefined>(undefined)
  type EditorSectionKey = 'method' | 'macro' | 'micro' | 'diagnosis'
  const activeSection = ref<EditorSectionKey>('method')
  const sections = ref<{ method: string; macro: string; micro: string; diagnosis: string }>({
    method: '',
    macro: '',
    micro: '',
    diagnosis: ''
  })
  const attachments = ref<Attachment[]>([])

  const lastSavedAt = ref<string | undefined>(undefined)
  const errorMessage = ref<string | null>(null)
  const validationMessage = ref<string | null>(null)

  const previewData = ref<PreviewData | null>(null)
  const isPreviewOpen = ref(false)

  const selectedTemplate = computed(() => undefined)

  // Validaciones de campos requeridos
  const missingFields = computed<string[]>(() => {
    const faltantes: string[] = []
    if (!sections.value.method.trim()) faltantes.push('Método')
    if (!sections.value.macro.trim()) faltantes.push('Corte Macro')
    if (!sections.value.micro.trim()) faltantes.push('Corte Micro')
    if (!sections.value.diagnosis.trim()) faltantes.push('Diagnóstico')
    return faltantes
  })
  const canSave = computed<boolean>(() => missingFields.value.length === 0)

  // Snapshots para detectar cambios no guardados
  const savedSectionsSnapshot = ref<string>('')
  const savedTemplateIdSnapshot = ref<string | undefined>(undefined)
  const savedAttachmentsSnapshot = ref<string>('[]')
  const isDirty = computed(() => {
    const attachmentsJson = JSON.stringify(attachments.value)
    return (
      JSON.stringify(sections.value) !== savedSectionsSnapshot.value ||
      selectedTemplateId.value !== savedTemplateIdSnapshot.value ||
      attachmentsJson !== savedAttachmentsSnapshot.value
    )
  })

  async function initialize() {
    if (!sampleId) return
    loading.value = true
    errorMessage.value = null
    try {
      if (sampleId) {
        await loadCaseByCode(sampleId)
      }
      // Sin plantillas: se deja el contenido vacío para ingreso manual
      // Adjuntar un archivo demo para mostrar la UI
      if (attachments.value.length === 0) {
        attachments.value.push({ id: 'att-demo', fileName: 'macro-demo.png', fileType: 'image/png', sizeKb: 128 })
      }
      // Inicializar snapshots sin cambios
      savedSectionsSnapshot.value = JSON.stringify(sections.value)
      savedTemplateIdSnapshot.value = selectedTemplateId.value
      savedAttachmentsSnapshot.value = JSON.stringify(attachments.value)
    } catch (err) {
      errorMessage.value = 'No se pudo cargar la información inicial.'
    } finally {
      loading.value = false
    }
  }

  async function loadCaseByCode(casoCode: string) {
    loading.value = true
    errorMessage.value = null
    try {
      const beCase = await casesApiService.getCaseByCode(casoCode)
      patient.value = mapCaseToPatient(beCase)
      caseDetails.value = mapCaseToCaseDetails(beCase)
      sample.value = {
        id: beCase.caso_code,
        type: 'Caso',
        collectedAt: (beCase as any).fecha_creacion || beCase.fecha_ingreso,
        status: beCase.estado as any,
        patientId: beCase.paciente.paciente_code
      }
      // Cargar casos anteriores del paciente por paciente_code
      if (beCase.paciente?.paciente_code) {
        try {
          const list = await casesApiService.getCasesByPatient(beCase.paciente.paciente_code)
          previousCases.value = list
            .filter(c => c.caso_code !== beCase.caso_code)
            .map(c => ({
              _id: c._id || c.caso_code,
              caso_code: c.caso_code,
              paciente: { nombre: c.paciente?.nombre || '', cedula: c.paciente?.paciente_code || '' },
              estado: c.estado as any,
              fecha_ingreso: (c as any).fecha_creacion || c.fecha_ingreso,
              patologo_asignado: c.patologo_asignado ? { nombre: c.patologo_asignado.nombre } : undefined
            }))
        } catch (e) {
          previousCases.value = []
        }
      } else {
        previousCases.value = []
      }
      // Si en el futuro deseamos precargar secciones desde beCase.resultado, se mapea aquí
      if (beCase.resultado) {
        sections.value = {
          method: (beCase.resultado as any)?.metodo || '',
          macro: (beCase.resultado as any)?.resultado_macro || '',
          micro: (beCase.resultado as any)?.resultado_micro || '',
          diagnosis: (beCase.resultado as any)?.diagnostico || ''
        }
        savedSectionsSnapshot.value = JSON.stringify(sections.value)
        
        // NOTA: Los diagnósticos CIE-10 y CIE-O NO se cargan automáticamente en Transcribir Resultados
        // Solo se cargan en Firmar Resultados
        /*
        // Cargar diagnósticos CIE-10 y CIE-O existentes si los tiene
        const resultado = beCase.resultado as any
        if (resultado.diagnostico_cie10) {
          const diseaseData = {
            id: resultado.diagnostico_cie10.id,
            codigo: resultado.diagnostico_cie10.codigo,
            nombre: resultado.diagnostico_cie10.nombre,
            tabla: 'CIE-10',
            isActive: true
          }
          setPrimaryDisease(diseaseData)
        }
        
        if (resultado.diagnostico_cieo) {
          const diseaseDataCIEO = {
            id: resultado.diagnostico_cieo.id,
            codigo: resultado.diagnostico_cieo.codigo,
            nombre: resultado.diagnostico_cieo.nombre,
            tabla: 'CIE-O',
            isActive: true
          }
          setPrimaryDiseaseCIEO(diseaseDataCIEO)
        }
        */
      }
    } catch (err: any) {
      errorMessage.value = err.message || 'No se pudo cargar el caso'
    } finally {
      loading.value = false
    }
  }

  // Búsqueda y plantillas eliminadas en la limpieza

  function addAttachment(fileName: string, fileType: string, sizeKb: number) {
    attachments.value.push({ id: Math.random().toString(36).slice(2), fileName, fileType, sizeKb })
  }

  function removeAttachment(attachmentId: string) {
    attachments.value = attachments.value.filter(a => a.id !== attachmentId)
  }

  async function onSaveDraft() {
    validationMessage.value = null
    saving.value = true
    try {
      if (!canSave.value) {
        validationMessage.value = `Debe completar: ${missingFields.value.join(', ')}`
        return false
      }
      if (!sample.value?.id) throw new Error('No hay caso cargado')
      
      // Preparar datos del diagnóstico CIE-10
      const diagnosticoCie10 = hasDisease.value && primaryDisease.value ? {
        id: primaryDisease.value.id,
        codigo: primaryDisease.value.codigo,
        nombre: primaryDisease.value.nombre
      } : undefined

      // Preparar datos del diagnóstico CIEO
      const diagnosticoCIEO = hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
        id: primaryDiseaseCIEO.value.id,
        codigo: primaryDiseaseCIEO.value.codigo,
        nombre: primaryDiseaseCIEO.value.nombre
      } : undefined

      const requestData = {
        metodo: sections.value.method,
        resultado_macro: sections.value.macro,
        resultado_micro: sections.value.micro,
        diagnostico: sections.value.diagnosis,
        observaciones: undefined,
        diagnostico_cie10: diagnosticoCie10,
        diagnostico_cieo: diagnosticoCIEO
      }
      
      await resultsApiService.upsertResultado(sample.value.id, requestData)
      lastSavedAt.value = new Date().toISOString()
      
      // NO limpiar automáticamente aquí - dejar que el componente maneje cuándo limpiar
      // clearAfterSuccess()
      
      return true
    } catch (err) {
      errorMessage.value = 'No se pudo guardar el borrador.'
      return false
    } finally {
      saving.value = false
    }
  }

  async function onFinalize() {
    if (!sections.value.diagnosis.trim()) {
      validationMessage.value = 'El diagnóstico no puede estar vacío.'
      return false
    }
    finalizing.value = true
    try {
      // En integración real: firmar resultado en backend (endpoint específico)
      return true
    } catch (err) {
      errorMessage.value = 'No se pudo finalizar el resultado.'
      return false
    } finally {
      finalizing.value = false
    }
  }

  async function onPreview() {
    previewing.value = true
    try {
      const html = buildHtmlPreview()
      previewData.value = { html }
      isPreviewOpen.value = true
    } finally {
      previewing.value = false
    }
  }

  function closePreview() {
    isPreviewOpen.value = false
  }

  // Computed para editar la sección activa desde un solo editor
  const sectionContent = computed<string>({
    get: () => sections.value[activeSection.value],
    set: (val: string) => { sections.value[activeSection.value] = val }
  })

  // buildFullContent eliminado en limpieza de plantillas

  function buildHtmlPreview(): string {
    const sectionHtml = (title: string, body: string) => `
<h3 style=\"margin:16px 0 4px 0\">${title}</h3>
<div style=\"white-space:pre-wrap\">${body}</div>`
    const parts: string[] = []
    parts.push(`<h2 style=\"margin:0 0 8px 0\">Informe de Resultado</h2>`)
    parts.push(`<div><strong>Caso:</strong> ${sample.value?.id} (${sample.value?.type})</div>`)
    parts.push('<hr/>')
    if (sections.value.method.trim()) parts.push(sectionHtml('Método', sections.value.method))
    if (sections.value.macro.trim()) parts.push(sectionHtml('Corte Macro', sections.value.macro))
    if (sections.value.micro.trim()) parts.push(sectionHtml('Corte Micro', sections.value.micro))
    if (sections.value.diagnosis.trim()) parts.push(sectionHtml('Diagnóstico', sections.value.diagnosis))
    return parts.join('\n')
  }

  function onClear() {
    sections.value = { method: '', macro: '', micro: '', diagnosis: '' }
    // no tocar adjuntos ni plantilla seleccionada para no perder contexto
    validationMessage.value = null
    errorMessage.value = null
  }

  // Función para limpiar el formulario después de guardar/firmar exitosamente
  function clearAfterSuccess() {
    sections.value = { method: '', macro: '', micro: '', diagnosis: '' }
    activeSection.value = 'method'
    validationMessage.value = null
    errorMessage.value = null
    // Limpiar diagnósticos
    clearPrimaryDisease()
    clearPrimaryDiseaseCIEO()
    showCIEODiagnosis.value = false
    // Actualizar snapshots para que no aparezca como "dirty"
    savedSectionsSnapshot.value = JSON.stringify(sections.value)
    savedTemplateIdSnapshot.value = selectedTemplateId.value
    
    // Limpiar el buscador (resetear estado del caso)
    sample.value = null
    patient.value = null
    caseDetails.value = null
    previousCases.value = []
    
    // Emitir evento para limpiar el buscador en los componentes
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('clear-search'))
    }
    
    // Scroll hacia la notificación después de un pequeño delay para que se renderice
    setTimeout(() => {
      // Buscar la notificación por diferentes selectores
      const notificationElement = document.querySelector('[data-notification="success"], .notification-container, .notification') ||
                                 document.querySelector('.mt-3[data-notification]') ||
                                 document.querySelector('.bg-green-50, .bg-blue-50, .bg-yellow-50, .bg-red-50')
      
      if (notificationElement) {
        notificationElement.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center',
          inline: 'nearest'
        })
      }
    }, 150)
  }

  // Funciones para manejar diagnóstico CIEO
  function setPrimaryDiseaseCIEO(disease: Disease | null) {
    primaryDiseaseCIEO.value = disease
  }

  function clearPrimaryDiseaseCIEO() {
    primaryDiseaseCIEO.value = null
  }

  function toggleCIEODiagnosis() {
    showCIEODiagnosis.value = !showCIEODiagnosis.value
    if (!showCIEODiagnosis.value) {
      clearPrimaryDiseaseCIEO()
    }
  }

  return {
    // state
    loading, saving, finalizing, previewing,
    sample, patient, caseDetails,
    previousCases,
    selectedTemplateId, selectedTemplate,
    sampleSearchResults,
    activeSection, sections, sectionContent, attachments,
    lastSavedAt, errorMessage, validationMessage,
    previewData, isPreviewOpen,
    canSave, missingFields,
    // actions
    initialize, loadCaseByCode,
    addAttachment, removeAttachment,
    onSaveDraft, onFinalize, onPreview, closePreview, onClear, clearAfterSuccess,
    // meta
    isDirty,
    // CIE-10 diagnosis
    primaryDisease,
    hasDisease,
    setPrimaryDisease,
    clearPrimaryDisease,
    clearDiagnosis,
    formatDiagnosisForReport,
    getDiagnosisData,
    validateDiagnosis,
    // CIEO diagnosis
    primaryDiseaseCIEO,
    hasDiseaseCIEO,
    showCIEODiagnosis,
    setPrimaryDiseaseCIEO,
    clearPrimaryDiseaseCIEO,
    toggleCIEODiagnosis
  }
}


