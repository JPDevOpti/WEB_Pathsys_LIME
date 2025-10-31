// import apiClient from '@/core/config/axios.config'
// import { API_CONFIG } from '@/core/config/api.config'
import type { UserRole } from '../types/userProfile.types'
import { PathologistApiService } from './pathologistApiService'
import { ResidentApiService } from './residentApiService'
import { AuxiliarApiService } from './auxiliaryApiService'
import { BillingApiService } from './billingApiService'

export interface BackendPatologo {
  patologoName: string
  InicialesPatologo?: string
  patologoCode: string
  PatologoEmail: string
  registro_medico: string
  firma?: string
  observaciones?: string
  isActive: boolean
  fecha_creacion?: string
  fecha_actualizacion?: string
}

export interface BackendResidente {
  residenteName: string
  InicialesResidente?: string
  residenteCode: string
  ResidenteEmail: string
  registro_medico: string
  observaciones?: string
  isActive: boolean
  fecha_creacion?: string
  fecha_actualizacion?: string
}

export interface BackendAuxiliar {
  auxiliarName: string
  auxiliarCode: string
  AuxiliarEmail: string
  observaciones?: string
  isActive: boolean
  fecha_creacion?: string
  fecha_actualizacion?: string
}

export interface BackendFacturacion {
  facturacionName: string
  facturacionCode: string
  FacturacionEmail: string
  observaciones?: string
  isActive: boolean
  fecha_creacion?: string
  fecha_actualizacion?: string
}

export const profileApiService = {
  async getByRoleAndEmail(role: UserRole, email: string) {
    switch (role) {
      case 'patologo': {
        // Usar el nuevo servicio de patólogos
        const pathologist = await PathologistApiService.getByEmail(email)
        if (!pathologist) return undefined
        
        // Mapear a la estructura esperada por el frontend
        const mapped = {
          patologoName: pathologist.pathologist_name,
          InicialesPatologo: pathologist.initials,
          patologoCode: pathologist.pathologist_code,
          PatologoEmail: pathologist.pathologist_email,
          registro_medico: pathologist.medical_license,
          firma: pathologist.signature,
          observaciones: pathologist.observations,
          isActive: pathologist.is_active,
          fecha_creacion: pathologist.created_at,
          fecha_actualizacion: pathologist.updated_at
        } as BackendPatologo
        return mapped
      }
      case 'residente': {
        // Usar el nuevo servicio de residentes
        const resident = await ResidentApiService.getByEmail(email)
        if (!resident) return undefined
        
        // Mapear a la estructura esperada por el frontend
        const mapped = {
          residenteName: resident.resident_name,
          InicialesResidente: resident.initials,
          residenteCode: resident.resident_code,
          ResidenteEmail: resident.resident_email,
          registro_medico: resident.medical_license,
          observaciones: resident.observations,
          isActive: resident.is_active,
          fecha_creacion: resident.created_at,
          fecha_actualizacion: resident.updated_at
        } as BackendResidente
        return mapped
      }
      case 'auxiliar': {
        // Usar el nuevo servicio de auxiliares
        const auxiliar = await AuxiliarApiService.getByEmail(email)
        if (!auxiliar) return undefined
        
        // Mapear a la estructura esperada por el frontend
        const mapped = {
          auxiliarName: auxiliar.auxiliar_name,
          auxiliarCode: auxiliar.auxiliar_code,
          AuxiliarEmail: auxiliar.auxiliar_email,
          observaciones: auxiliar.observations,
          isActive: auxiliar.is_active,
          fecha_creacion: auxiliar.created_at,
          fecha_actualizacion: auxiliar.updated_at
        } as BackendAuxiliar
        return mapped
      }
      case 'facturacion': {
        // Usar el nuevo servicio de facturación
        const billing = await BillingApiService.getByEmail(email)
        if (!billing) return undefined
        
        // Mapear a la estructura esperada por el frontend
        const mapped = {
          facturacionName: billing.billing_name,
          facturacionCode: billing.billing_code,
          FacturacionEmail: billing.billing_email,
          observaciones: billing.observations,
          isActive: billing.is_active,
          fecha_creacion: billing.created_at,
          fecha_actualizacion: billing.updated_at
        } as BackendFacturacion
        return mapped
      }
      case 'admin':
      default:
        return undefined
    }
  },

  async getPathologistByCode(code: string): Promise<BackendPatologo | undefined> {
    try {
      const pathologist = await PathologistApiService.getByCode(code)
      if (!pathologist) return undefined
      
      // Mapear a la estructura esperada por el frontend
      return {
        patologoName: pathologist.pathologist_name,
        InicialesPatologo: pathologist.initials,
        patologoCode: pathologist.pathologist_code,
        PatologoEmail: pathologist.pathologist_email,
        registro_medico: pathologist.medical_license,
        firma: pathologist.signature,
        observaciones: pathologist.observations,
        isActive: pathologist.is_active,
        fecha_creacion: pathologist.created_at,
        fecha_actualizacion: pathologist.updated_at
      } as BackendPatologo
    } catch {
      return undefined
    }
  },

  async getResidentByCode(code: string): Promise<BackendResidente | undefined> {
    try {
      const resident = await ResidentApiService.getByCode(code)
      if (!resident) return undefined
      
      // Mapear a la estructura esperada por el frontend
      return {
        residenteName: resident.resident_name,
        InicialesResidente: resident.initials,
        residenteCode: resident.resident_code,
        ResidenteEmail: resident.resident_email,
        registro_medico: resident.medical_license,
        observaciones: resident.observations,
        isActive: resident.is_active,
        fecha_creacion: resident.created_at,
        fecha_actualizacion: resident.updated_at
      } as BackendResidente
    } catch {
      return undefined
    }
  },

  async getAuxiliarByCode(code: string): Promise<BackendAuxiliar | undefined> {
    try {
      const auxiliar = await AuxiliarApiService.getByCode(code)
      if (!auxiliar) return undefined
      
      // Mapear a la estructura esperada por el frontend
      return {
        auxiliarName: auxiliar.auxiliar_name,
        auxiliarCode: auxiliar.auxiliar_code,
        AuxiliarEmail: auxiliar.auxiliar_email,
        observaciones: auxiliar.observations,
        isActive: auxiliar.is_active,
        fecha_creacion: auxiliar.created_at,
        fecha_actualizacion: auxiliar.updated_at
      } as BackendAuxiliar
    } catch {
      return undefined
    }
  },

  async getBillingByCode(code: string): Promise<BackendFacturacion | undefined> {
    try {
      const billing = await BillingApiService.getByCode(code)
      if (!billing) return undefined
      
      // Mapear a la estructura esperada por el frontend
      return {
        facturacionName: billing.billing_name,
        facturacionCode: billing.billing_code,
        FacturacionEmail: billing.billing_email,
        observaciones: billing.observations,
        isActive: billing.is_active,
        fecha_creacion: billing.created_at,
        fecha_actualizacion: billing.updated_at
      } as BackendFacturacion
    } catch {
      return undefined
    }
  },

  async updateByRole(role: UserRole, code: string, payload: any) {
    switch (role) {
      case 'patologo':
        // Usar el nuevo servicio de patólogos
        const patoPayload: any = {
          pathologist_name: payload.patologoName || payload.patologo_name,
          initials: payload.InicialesPatologo || payload.iniciales_patologo || payload.iniciales,
          pathologist_email: payload.PatologoEmail || payload.patologo_email,
          medical_license: payload.registro_medico,
          observations: payload.observaciones,
          is_active: payload.isActive !== undefined ? payload.isActive : true
        }
        // Include password if provided
        if (payload.password && payload.password.trim()) {
          patoPayload.password = payload.password
        }
        return PathologistApiService.update(code, patoPayload)
      case 'residente':
        // Usar el nuevo servicio de residentes
        const resPayload: any = {
          resident_name: payload.residenteName || payload.residente_name,
          initials: payload.InicialesResidente || payload.iniciales_residente || payload.iniciales,
          resident_email: payload.ResidenteEmail || payload.residente_email,
          medical_license: payload.registro_medico,
          observations: payload.observaciones,
          is_active: payload.isActive !== undefined ? payload.isActive : true
        }
        // Include password if provided
        if (payload.password && payload.password.trim()) {
          resPayload.password = payload.password
        }
        return ResidentApiService.update(code, resPayload)
      case 'auxiliar':
        // Usar el nuevo servicio de auxiliares
        const auxPayload: any = {
          auxiliar_name: payload.auxiliarName || payload.auxiliar_name,
          auxiliar_email: payload.AuxiliarEmail || payload.auxiliar_email,
          observations: payload.observaciones,
          is_active: payload.isActive !== undefined ? payload.isActive : true
        }
        // Include password if provided
        if (payload.password && payload.password.trim()) {
          auxPayload.password = payload.password
        }
        return AuxiliarApiService.update(code, auxPayload)
      case 'facturacion':
        // Usar el nuevo servicio de facturación
        const factPayload: any = {
          billing_name: payload.facturacionName || payload.facturacion_name,
          billing_email: payload.FacturacionEmail || payload.facturacion_email,
          observations: payload.observaciones,
          is_active: payload.isActive !== undefined ? payload.isActive : true
        }
        // Include password if provided
        if (payload.password && payload.password.trim()) {
          factPayload.password = payload.password
        }
        return BillingApiService.update(code, factPayload)
      default:
        return null
    }
  },

  async updateFirma(patologoCode: string, firmaUrl: string) {
    return PathologistApiService.updateSignature(patologoCode, firmaUrl)
  },

  async uploadFirma(patologoCode: string, file: File) {
    return PathologistApiService.uploadSignature(patologoCode, file)
  },

  async getFirma(patologoCode: string) {
    return PathologistApiService.getSignature(patologoCode)
  },

  async deleteFirma(patologoCode: string) {
    // Fallback para backends sin DELETE: enviar firma vacía por PUT
    return PathologistApiService.updateSignature(patologoCode, '')
  }
}


