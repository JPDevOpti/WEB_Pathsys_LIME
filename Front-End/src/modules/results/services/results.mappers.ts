import type { CaseModel, CaseListItem } from '@/modules/cases/types/case'
import type { Patient, CaseDetails } from '../types/results.types'

export function mapCaseToPatient(beCase: CaseModel): Patient {
  const p = beCase.patient_info
  return {
    id: p?.patient_code || '',
    fullName: p?.name || '',
    document: p?.patient_code || '',
    age: p?.age || 0,
    entity: p?.entity_info?.name || '',
    entityCode: p?.entity_info?.id || '',
    sexo: p?.gender || '',
    tipoAtencion: p?.care_type || '',
    observaciones: p?.observations || ''
  }
}

export function mapCaseToCaseDetails(beCase: CaseModel): CaseDetails {
  return {
    _id: beCase.id || '',
    case_code: beCase.case_code,
    patient_info: {
      patient_code: beCase.patient_info?.patient_code || '',
      name: beCase.patient_info?.name || '',
      age: beCase.patient_info?.age || 0,
      gender: beCase.patient_info?.gender || '',
      entity_info: {
        id: beCase.patient_info?.entity_info?.id || '',
        name: beCase.patient_info?.entity_info?.name || ''
      },
      care_type: beCase.patient_info?.care_type || '',
      observations: beCase.patient_info?.observations || '',
      updated_at: beCase.updated_at || ''
    },
    requesting_physician: beCase.requesting_physician || undefined,
    samples: (beCase.samples || []).map(m => ({
      body_region: m.body_region,
      tests: (m.tests || []).map(p => ({ id: p.id, name: p.name }))
    })),
    state: beCase.state,
    created_at: beCase.created_at,
    updated_at: beCase.updated_at,
    observations: beCase.observations || '',
    active: true,
    assigned_pathologist: beCase.assigned_pathologist
      ? { id: beCase.assigned_pathologist.id || '', name: beCase.assigned_pathologist.name || '' }
      : undefined,
    updated_by: undefined,
    entity_info: beCase.patient_info?.entity_info
      ? { id: beCase.patient_info.entity_info.id || '', name: beCase.patient_info.entity_info.name || '' }
      : undefined,
    service: beCase.service,
    result: beCase.result ? {
      diagnosis: beCase.result.diagnosis || '',
      macro_result: beCase.result.macro_result || '',
      micro_result: beCase.result.micro_result || '',
      observations: beCase.result.observations || null
    } : undefined
  }
}

export function mapCaseToListItem(beCase: CaseModel): CaseListItem {
  return {
    _id: beCase.id || beCase.case_code,
    case_code: beCase.case_code,
    patient: {
      name: beCase.patient_info?.name || '',
      patient_code: beCase.patient_info?.patient_code || ''
    },
    state: beCase.state as any,
    created_at: beCase.created_at,
    assigned_pathologist: beCase.assigned_pathologist ? { name: beCase.assigned_pathologist.name || '' } : undefined
  }
}


