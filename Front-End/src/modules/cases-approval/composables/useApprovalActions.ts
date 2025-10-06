import { ref } from 'vue'
import approvalService from '@/shared/services/approval.service'
import { useToasts } from '@/shared/composables/useToasts'

export function useApprovalActions() {
  const { success, error: showError } = useToasts()
  const processing = ref(false)

  const manageRequest = async (approvalCode: string) => {
    processing.value = true
    try {
      const result = await approvalService.manageApprovalRequest(approvalCode)
      success('generic', 'Solicitud gestionada', 'La solicitud ha sido marcada como "Pendiente de Aprobación"')
      return result
    } catch (error: any) {
      console.error('Error al gestionar solicitud:', error)
      showError('generic', 'Error al gestionar', error.message || 'No se pudo gestionar la solicitud')
      throw error
    } finally {
      processing.value = false
    }
  }

  const approveRequest = async (approvalCode: string) => {
    processing.value = true
    try {
      const result = await approvalService.approveRequest(approvalCode)
      success('generic', 'Solicitud aprobada', 'La solicitud ha sido aprobada y se ha creado el caso')
      return result
    } catch (error: any) {
      console.error('Error al aprobar solicitud:', error)
      showError('generic', 'Error al aprobar', error.message || 'No se pudo aprobar la solicitud')
      throw error
    } finally {
      processing.value = false
    }
  }

  const rejectRequest = async (approvalCode: string) => {
    processing.value = true
    try {
      const result = await approvalService.rejectRequest(approvalCode)
      success('generic', 'Solicitud rechazada', 'La solicitud ha sido rechazada')
      return result
    } catch (error: any) {
      console.error('Error al rechazar solicitud:', error)
      showError('generic', 'Error al rechazar', error.message || 'No se pudo rechazar la solicitud')
      throw error
    } finally {
      processing.value = false
    }
  }

  const updateTests = async (approvalCode: string, tests: any[]) => {
    processing.value = true
    try {
      const result = await approvalService.updateApprovalRequest(approvalCode, {
        complementary_tests: tests
      })
      success('generic', 'Pruebas actualizadas', 'Las pruebas complementarias se han actualizado exitosamente')
      return result
    } catch (error: any) {
      console.error('Error al actualizar pruebas:', error)
      showError('generic', 'Error al actualizar', error.message || 'No se pudieron actualizar las pruebas')
      throw error
    } finally {
      processing.value = false
    }
  }

  return {
    processing,
    manageRequest,
    approveRequest,
    rejectRequest,
    updateTests
  }
}
