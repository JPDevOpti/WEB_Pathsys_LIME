import { computed, ref } from 'vue'
import type { Attachment, Patient, PreviewData, Sample, CaseDetails } from '../types/results.types'
import type { CaseListItem } from '@/modules/cases/types/case'

import casesApiService from '@/modules/cases/services/casesApi.service'
import { mapCaseToPatient, mapCaseToCaseDetails } from '../services/results.mappers'
import resultsApiService, { type UpdateResultRequest } from '../services/resultsApiService'
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
  const sections = ref<{ method: string[]; macro: string; micro: string; diagnosis: string }>({
    method: [],
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

  // Validaciones de campos requeridos para completar (marcar como "Por firmar")
  const missingFields = computed<string[]>(() => {
    const faltantes: string[] = []
    if (!sections.value.method.length || sections.value.method.every(m => !m.trim())) faltantes.push('Método')
    if (!sections.value.macro.trim()) faltantes.push('Corte Macro')
    if (!sections.value.micro.trim()) faltantes.push('Corte Micro')
    if (!sections.value.diagnosis.trim()) faltantes.push('Diagnóstico')
    return faltantes
  })
  
  // Para guardar progreso - siempre se puede guardar si hay algún contenido
  const canSaveProgress = computed<boolean>(() => {
    return !!(
      (sections.value.method.length && sections.value.method.some(m => m.trim())) ||
      sections.value.macro.trim() ||
      sections.value.micro.trim() ||
      sections.value.diagnosis.trim()
    )
  })
  
  // Para marcar como completo - requiere todos los campos
  const canComplete = computed<boolean>(() => missingFields.value.length === 0)
  
  // Mantener canSave para compatibilidad, pero ahora permite guardar progreso
  const canSave = computed<boolean>(() => canSaveProgress.value)

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
        id: beCase.case_code,
        type: 'Caso',
        collectedAt: beCase.created_at || beCase.updated_at,
        status: beCase.state as any,
        patientId: beCase.patient_info?.patient_code || ''
      }
      // Cargar casos anteriores del paciente por patient_code
      if (beCase.patient_info?.patient_code) {
        try {
          const list = await casesApiService.getCasesByPatient(beCase.patient_info.patient_code)
          previousCases.value = list
            .filter(c => 
              c.case_code !== beCase.case_code && 
              c.patient_info?.patient_code === beCase.patient_info?.patient_code
            )
            .map(c => ({
              _id: c.id || c.case_code,
              case_code: c.case_code,
              patient: { name: c.patient_info?.name || '', patient_code: c.patient_info?.patient_code || '' },
              state: c.state as any,
              created_at: c.created_at || c.updated_at,
              assigned_pathologist: c.assigned_pathologist ? { name: c.assigned_pathologist.name || '' } : undefined
            }))
        } catch (e) {
          console.error('Error loading previous cases:', e)
          previousCases.value = []
        }
      } else {
        previousCases.value = []
      }
      // Cargar resultados existentes del nuevo backend
      if (beCase.result) {
        const resultData = beCase.result
        let methodArray: string[] = []
        
        // Mapear métodos (nuevo formato: method)
        if (resultData.method && Array.isArray(resultData.method)) {
          methodArray = resultData.method
        } else if ((resultData as any).metodo && Array.isArray((resultData as any).metodo)) {
          // Compatibilidad con formato legacy
          methodArray = (resultData as any).metodo
        }

        // Normalizar entradas para que coincidan con los option.value
        try {
          const { normalizeMethod } = await import('@/shared/data/methods')
          methodArray = methodArray.map(m => normalizeMethod(m))
        } catch (e) { /* ignore */ }
        
        sections.value = {
          method: methodArray,
          macro: resultData.macro_result || '',
          micro: resultData.micro_result || '',
          diagnosis: resultData.diagnosis || ''
        }
        savedSectionsSnapshot.value = JSON.stringify(sections.value)
        
        // NOTA: Los diagnósticos CIE-10 y CIE-O NO se cargan automáticamente en Transcribir Resultados
        // Solo se cargan en Firmar Resultados
        /*
        // Cargar diagnósticos CIE-10 y CIE-O existentes si los tiene
        const resultado = beCase.resultado as any
        if (resultado.diagnostico_cie10) {
          const diseaseData = {
            codigo: resultado.diagnostico_cie10.codigo,
            nombre: resultado.diagnostico_cie10.nombre,
            tabla: 'CIE-10',
            isActive: true
          }
          setPrimaryDisease(diseaseData)
        }
        
        if (resultado.diagnostico_cieo) {
          const diseaseDataCIEO = {
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

    // Función helper para convertir array de métodos a string
  function formatMethodsForBackend(methods: string[] | null | undefined): string {
    if (!methods || !Array.isArray(methods)) return ''
    const validMethods = methods.filter(m => m && typeof m === 'string' && m.trim())
    if (validMethods.length === 0) return ''
    if (validMethods.length === 1) {
      return `Método utilizado: ${validMethods[0]}.`
    } else {
      return `Métodos utilizados: ${validMethods.join(', ')}.`
    }
  }

  async function onSaveDraft(): Promise<boolean> {
    validationMessage.value = null
    saving.value = true
    try {
      if (!canSaveProgress.value) {
        validationMessage.value = 'Debe escribir al menos algo en uno de los campos para guardar'
        return false
      }
      if (!sample.value?.id) throw new Error('No hay caso cargado')
      
      // Preparar datos del diagnóstico CIE-10
      const diagnosticoCie10 = hasDisease.value && primaryDisease.value ? {
        id: primaryDisease.value.id,
        codigo: primaryDisease.value.code,
        nombre: primaryDisease.value.name
      } : undefined

      // Preparar datos del diagnóstico CIEO
      const diagnosticoCIEO = hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
        id: primaryDiseaseCIEO.value.id,
        codigo: primaryDiseaseCIEO.value.code,
        nombre: primaryDiseaseCIEO.value.name
      } : undefined

      // Preparar datos para el nuevo backend
      const requestData: UpdateResultRequest = {
        method: sections.value?.method || [],
        macro_result: sections.value?.macro || '',
        micro_result: sections.value?.micro || '',
        diagnosis: sections.value?.diagnosis || '',
        observations: undefined,
        diagnostico_cie10: diagnosticoCie10,
        diagnostico_cieo: diagnosticoCIEO
      }
      
      console.log('Enviando datos al nuevo backend:', requestData)
      
      await resultsApiService.updateCaseResult(sample.value.id, requestData)
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

  async function onCompleteForSigning() {
    validationMessage.value = null
    saving.value = true
    try {
      if (!canComplete.value) {
        validationMessage.value = `Para marcar como "Por firmar" debe completar: ${missingFields.value.join(', ')}`
        return false
      }
      if (!sample.value?.id) throw new Error('No hay caso cargado')
      
      // Preparar datos del diagnóstico CIE-10
      const diagnosticoCie10 = hasDisease.value && primaryDisease.value ? {
        id: primaryDisease.value.id,
        codigo: primaryDisease.value.code,
        nombre: primaryDisease.value.name
      } : undefined

      // Preparar datos del diagnóstico CIEO
      const diagnosticoCIEO = hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
        id: primaryDiseaseCIEO.value.id,
        codigo: primaryDiseaseCIEO.value.code,
        nombre: primaryDiseaseCIEO.value.name
      } : undefined

      // Preparar datos para el nuevo backend
      const requestData: UpdateResultRequest = {
        method: sections.value?.method || [],
        macro_result: sections.value?.macro || '',
        micro_result: sections.value?.micro || '',
        diagnosis: sections.value?.diagnosis || '',
        observations: undefined,
        diagnostico_cie10: diagnosticoCie10,
        diagnostico_cieo: diagnosticoCIEO
      }
      
      
      // Guardar resultado en el nuevo backend
      await resultsApiService.updateCaseResult(sample.value.id, requestData)
      
      // Cambiar estado del caso a "Por firmar"
      await casesApiService.updateCaseState(sample.value.id, 'Por firmar')
      
      lastSavedAt.value = new Date().toISOString()
      
      return true
    } catch (err) {
      errorMessage.value = 'No se pudo completar el caso para firma.'
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
  const sectionContent = computed({
    get: () => {
      const value = sections.value[activeSection.value]
      if (activeSection.value === 'method') {
        // Para método, convertir array a string para compatibilidad
        return Array.isArray(value) ? value : []
      }
      return value as string
    },
    set: (val: string | string[]) => { 
      if (activeSection.value === 'method') {
        sections.value.method = Array.isArray(val) ? val : []
      } else {
        (sections.value as any)[activeSection.value] = typeof val === 'string' ? val : ''
      }
    }
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
    if (sections.value.method.length && sections.value.method.some(m => m.trim())) {
      parts.push(sectionHtml('Método', formatMethodsForBackend(sections.value.method)))
    }
    if (sections.value.macro.trim()) parts.push(sectionHtml('Corte Macro', sections.value.macro))
    if (sections.value.micro.trim()) parts.push(sectionHtml('Corte Micro', sections.value.micro))
    if (sections.value.diagnosis.trim()) parts.push(sectionHtml('Diagnóstico', sections.value.diagnosis))
    return parts.join('\n')
  }

  function onClear() {
    sections.value = { method: [], macro: '', micro: '', diagnosis: '' }
    // no tocar adjuntos ni plantilla seleccionada para no perder contexto
    validationMessage.value = null
    errorMessage.value = null
  }

  // Función para limpiar el formulario después de guardar/firmar exitosamente
  function clearAfterSuccess() {
    sections.value = { method: [], macro: '', micro: '', diagnosis: '' }
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
    canSave, canSaveProgress, canComplete, missingFields,
    // actions
    initialize, loadCaseByCode,
    addAttachment, removeAttachment,
    onSaveDraft, onCompleteForSigning, onFinalize, onPreview, closePreview, onClear, clearAfterSuccess,
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


