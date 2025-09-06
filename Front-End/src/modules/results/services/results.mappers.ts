import type { CaseModel, CaseListItem } from '@/modules/cases/types/case'
import type { Patient, CaseDetails } from '../types/results.types'

export function mapCaseToPatient(beCase: CaseModel): Patient {
  const p = beCase.paciente
  return {
    id: p.paciente_code,
    fullName: p.nombre,
    document: p.paciente_code,
    age: p.edad,
    entity: beCase.entidad_info?.nombre || p.entidad_info?.nombre,
    entityCode: beCase.entidad_info?.codigo || p.entidad_info?.codigo,
    sexo: p.sexo,
    tipoAtencion: p.tipo_atencion,
    observaciones: p.observaciones || ''
  }
}

export function mapCaseToCaseDetails(beCase: CaseModel): CaseDetails {
  return {
    _id: beCase._id || '',
    caso_code: beCase.caso_code,
    paciente: {
      paciente_code: beCase.paciente.paciente_code,
      nombre: beCase.paciente.nombre,
      edad: beCase.paciente.edad,
      sexo: beCase.paciente.sexo,
      entidad_info: {
        codigo: beCase.paciente.entidad_info?.codigo,
        nombre: beCase.paciente.entidad_info?.nombre
      },
      tipo_atencion: beCase.paciente.tipo_atencion,
      observaciones: beCase.paciente.observaciones || '',
      fecha_actualizacion: beCase.paciente.fecha_actualizacion
    },
    medico_solicitante: beCase.medico_solicitante
      ? { nombre: beCase.medico_solicitante }
      : undefined,
    muestras: (beCase.muestras || []).map(m => ({
      region_cuerpo: m.region_cuerpo,
      pruebas: (m.pruebas || []).map(p => ({ id: p.id, nombre: p.nombre }))
    })),
    estado: beCase.estado,
    fecha_creacion: (beCase as any).fecha_creacion || beCase.fecha_ingreso,
    fecha_firma: beCase.fecha_firma || null,
    fecha_actualizacion: beCase.fecha_actualizacion,
    observaciones_generales: beCase.observaciones_generales || '',
    is_active: beCase.activo ?? true,
    patologo_asignado: beCase.patologo_asignado
      ? { codigo: beCase.patologo_asignado.codigo, nombre: beCase.patologo_asignado.nombre }
      : undefined,
    actualizado_por: beCase.actualizado_por,
    entidad_info: beCase.entidad_info
      ? { codigo: beCase.entidad_info.codigo, nombre: beCase.entidad_info.nombre }
      : undefined,
    servicio: (beCase as any).servicio
  }
}

export function mapCaseToListItem(beCase: CaseModel): CaseListItem {
  return {
    _id: beCase._id || beCase.caso_code,
    caso_code: beCase.caso_code,
    paciente: {
      nombre: beCase.paciente?.nombre || '',
      cedula: beCase.paciente?.paciente_code || ''
    },
    estado: beCase.estado as any,
    fecha_ingreso: (beCase as any).fecha_creacion || beCase.fecha_ingreso,
    patologo_asignado: beCase.patologo_asignado ? { nombre: beCase.patologo_asignado.nombre } : undefined
  }
}


