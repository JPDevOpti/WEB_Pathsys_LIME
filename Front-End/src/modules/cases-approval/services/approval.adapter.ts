import type { ApprovalRequestResponse, ApprovalState, ComplementaryTestInfo } from '@/shared/services/approval.service'

export interface CaseToApproveViewModel {
  id: string
  approvalCode: string
  caseCode: string
  patientName: string
  pathologistName: string
  pathologistId?: string
  description?: string
  createdAt: string
  updatedAt: string
  status: ApprovalState
  complementaryTests: ComplementaryTestInfo[]
  // Estados de operación (para UI)
  approving?: boolean
  rejecting?: boolean
  managing?: boolean
}

export class ApprovalAdapter {
  /**
   * Convierte la respuesta del backend a un modelo de vista
   */
  static toViewModel(dto: ApprovalRequestResponse): CaseToApproveViewModel {
    return {
      id: dto.id,
      approvalCode: dto.approval_code,
      caseCode: dto.original_case_code,
      patientName: `Caso ${dto.original_case_code}`,
      pathologistName: dto.approval_info?.assigned_pathologist?.name || 'Sin asignar',
      pathologistId: dto.approval_info?.assigned_pathologist?.id || '',
      description: dto.approval_info?.reason || 'Sin motivo especificado',
      createdAt: dto.created_at,
      updatedAt: dto.updated_at,
      status: dto.approval_state,
      complementaryTests: dto.complementary_tests || [],
      // Inicializar estados de operación
      approving: false,
      rejecting: false,
      managing: false
    }
  }

  /**
   * Convierte un array de respuestas del backend a modelos de vista
   */
  static toViewModelList(dtos: ApprovalRequestResponse[]): CaseToApproveViewModel[] {
    return dtos.map(dto => this.toViewModel(dto))
  }

  /**
   * Formatea una fecha para mostrar
   */
  static formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  /**
   * Obtiene el texto del estado
   */
  static getStatusText(status: ApprovalState): string {
    const statusMap: Record<ApprovalState, string> = {
      'request_made': 'Solicitud Hecha',
      'pending_approval': 'Pendiente de Aprobación',
      'approved': 'Aprobado',
      'rejected': 'Rechazado'
    }
    return statusMap[status] || status
  }

  /**
   * Obtiene las clases CSS para el estado
   */
  static getStatusClasses(status: ApprovalState): string {
    const base = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
    const colors: Record<ApprovalState, string> = {
      'request_made': 'bg-blue-100 text-blue-800',
      'pending_approval': 'bg-yellow-100 text-yellow-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800'
    }
    return `${base} ${colors[status] || 'bg-gray-100 text-gray-800'}`
  }
}
