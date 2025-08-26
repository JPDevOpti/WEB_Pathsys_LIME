import type { Attachment, Patient, PreviewData, Sample, Template, CaseDetails } from '../types/results.types'

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export async function getSampleById(sampleId: string): Promise<Sample> {
  await delay(300)
  // Caso real de ejemplo proporcionado
  if (sampleId === '2025-00032') {
    return {
      id: '2025-00032',
      type: 'Caso (multi-muestra)',
      collectedAt: new Date('2025-08-13T15:32:34.208Z').toISOString(),
      status: 'pending',
      patientId: '123456'
    }
  }
  // Fallback demo
  return {
    id: sampleId,
    type: 'Biopsia',
    collectedAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    status: 'in-progress',
    patientId: 'P-1001'
  }
}

export async function getPatientById(patientId: string): Promise<Patient> {
  await delay(200)
  if (patientId === '123456') {
    return {
      id: '123456',
      fullName: 'Eqwewe',
      document: 'CC 123456',
      age: 31,
      entity: 'Clínica Norted1111ww',
      entityCode: 'CLINICA001',
      sexo: 'Femenino',
      tipoAtencion: 'Hospitalizado',
      observaciones: '',
      pruebasAnteriores: [
        {
          id: '1',
          codigo: 'BIO-001',
          nombre: 'Biopsia de piel',
          fecha: '2024-12-15',
          estado: 'Completado',
          resultado: 'Benigno'
        },
        {
          id: '2',
          codigo: 'CIT-002',
          nombre: 'Citología ginecológica',
          fecha: '2024-11-20',
          estado: 'Completado',
          resultado: 'Normal'
        },
        {
          id: '3',
          codigo: 'BIO-003',
          nombre: 'Biopsia de mama',
          fecha: '2024-10-10',
          estado: 'Completado',
          resultado: 'Fibroadenoma'
        }
      ]
    }
  }
  return {
    id: patientId,
    fullName: 'María Pérez',
    document: 'CC 1.234.567.890',
    age: 45,
    entity: 'Entidad Salud Demo',
    entityCode: 'ENT-01',
    sexo: 'Femenino',
    tipoAtencion: 'Ambulatorio',
    observaciones: '',
    pruebasAnteriores: []
  }
}

export async function listTemplates(query = ''): Promise<Template[]> {
  await delay(250)
  const templates: Template[] = [
    { id: 'T-1', name: 'Informe estándar', description: 'Estructura general', content: 'Hallazgos: ...\nDiagnóstico: ...' },
    { id: 'T-2', name: 'Informe dermatopatología', description: 'Piel y anexos', content: 'Microscopía: ...\nConclusión: ...' },
    { id: 'T-3', name: 'Informe citología', description: 'Citología ginecológica', content: 'Muestra adecuada: ...\nInterpretación: ...' }
  ]
  if (!query) return templates
  const q = query.toLowerCase()
  return templates.filter(t => t.name.toLowerCase().includes(q) || t.description?.toLowerCase().includes(q))
}

export async function saveDraft(_sampleId: string, _content: string, _templateId?: string, _attachments: Attachment[] = []): Promise<{ ok: boolean, savedAt: string }>{
  await delay(400)
  return { ok: true, savedAt: new Date().toISOString() }
}

export async function finalizeResult(_sampleId: string): Promise<{ ok: boolean }>{
  await delay(500)
  return { ok: true }
}

export async function generatePreview(_sampleId: string, htmlContent: string): Promise<PreviewData>{
  await delay(250)
  return { html: htmlContent }
}

export async function getCaseDetailsById(caseId: string): Promise<CaseDetails> {
  await delay(200)
  if (caseId === '2025-00032') {
    return {
      _id: '689cb0120022923d98f58186',
      CasoCode: '2025-00032',
      paciente: {
        codigo: '123456',
        nombre: 'Eqwewe',
        edad: 31,
        sexo: 'Femenino',
        entidad_info: { codigo: 'CLINICA001', nombre: 'Clínica Norted1111ww' },
        tipo_atencion: 'Hospitalizado',
        cedula: '123456',
        observaciones: '',
        fecha_actualizacion: new Date('2025-08-13T15:33:04.501Z').toISOString()
      },
      medico_solicitante: { nombre: 'asdadsasd' },
      muestras: [
        { region_cuerpo: 'cabeza', pruebas: [ { id: 'BIO-11', nombre: 'BIO-11' }, { id: '80000', nombre: '80000' } ] },
        { region_cuerpo: 'cuello', pruebas: [ { id: 'BIO-082', nombre: 'BIO-082' }, { id: 'BIO-082', nombre: 'BIO-082' } ] },
        { region_cuerpo: 'cabeza', pruebas: [ { id: 'BIO-13', nombre: 'BIO-13' } ] }
      ],
      estado: 'pendiente',
      fecha_creacion: new Date('2025-08-13T15:32:34.208Z').toISOString(),
      fecha_firma: null,
      fecha_actualizacion: new Date('2025-08-13T15:33:04.501Z').toISOString(),
      observaciones_generales: 'Probando que nada falle\n',
      fecha_creacion: new Date('2025-08-13T15:32:34.211Z').toISOString(),
      is_active: true,
      patologo_asignado: { codigo: '12345678', nombre: 'Patologo de Prueba' },
      actualizado_por: 'sistema',
      entidad_info: { codigo: 'CLINICA001', nombre: 'Clínica Norted1111ww' }
    }
  }
  // Fallback simple
  return {
    _id: 'demo',
    CasoCode: caseId,
    paciente: {
      codigo: 'P-1001', nombre: 'María Pérez', edad: 45, sexo: 'Femenino',
      entidad_info: { codigo: 'ENT-01', nombre: 'Entidad Salud Demo' }, tipo_atencion: 'Ambulatorio',
      cedula: '123456789', observaciones: '', fecha_actualizacion: new Date().toISOString()
    },
    medico_solicitante: { nombre: 'Dr. Demo' },
    muestras: [ { region_cuerpo: 'piel', pruebas: [ { id: 'BIO-01', nombre: 'Biopsia piel' } ] } ],
    estado: 'in-progress',
    fecha_creacion: new Date().toISOString(),
    fecha_firma: null,
    fecha_actualizacion: new Date().toISOString(),
    observaciones_generales: '',
    fecha_creacion: new Date().toISOString(),
    is_active: true,
    patologo_asignado: { codigo: '999', nombre: 'Patólogo Demo' },
    actualizado_por: 'sistema',
    entidad_info: { codigo: 'ENT-01', nombre: 'Entidad Salud Demo' }
  }
}
export async function searchSamples(query: string): Promise<Sample[]> {
  await delay(200)
  const all: Sample[] = [
    { id: '2025-00032', type: 'Caso (multi-muestra)', collectedAt: new Date('2025-08-13T15:32:34.208Z').toISOString(), status: 'pending', patientId: '123456' },
    { id: 'DEMO-001', type: 'Biopsia', collectedAt: new Date().toISOString(), status: 'in-progress', patientId: 'P-1001' },
    { id: 'DEMO-002', type: 'Citología', collectedAt: new Date().toISOString(), status: 'pending', patientId: 'P-1002' },
    { id: 'XYZ-123', type: 'Biopsia', collectedAt: new Date().toISOString(), status: 'finalized', patientId: 'P-1003' }
  ]
  const q = query.toLowerCase()
  return all.filter(s => s.id.toLowerCase().includes(q) || s.type.toLowerCase().includes(q))
}


