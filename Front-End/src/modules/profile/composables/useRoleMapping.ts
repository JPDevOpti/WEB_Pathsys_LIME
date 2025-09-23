import type { UserRole } from '../types/userProfile.types'

/**
 * Composable for role mapping and normalization
 */
export function useRoleMapping() {
  /**
   * Map authentication role to internal user role
   */
  const mapAuthRoleToUserRole = (rol?: string): UserRole => {
    const r = (rol || '').toString().trim().toLowerCase()
    if (r === 'pathologist' || r === 'patologo') return 'patologo'
    if (r === 'admin' || r === 'administrator' || r === 'administrador') return 'admin'
    if (r === 'resident' || r === 'residente') return 'residente'
    if (r === 'auxiliar' || r === 'auxiliary') return 'auxiliar'
    if (r === 'facturacion' || r === 'facturación' || r === 'billing') return 'facturacion'
    if (r.includes('admin')) return 'admin'
    if (r.includes('patolog')) return 'patologo'
    if (r.includes('resident')) return 'residente'
    if (r.includes('auxiliar')) return 'auxiliar'
    if (r.includes('facturacion') || r.includes('billing')) return 'facturacion'
    return 'admin'
  }

  /**
   * Normalize role for display purposes
   */
  const normalizeRole = (role: string): UserRole => {
    const r = String(role || '').toLowerCase()
    if ([ 'admin', 'administrator' ].includes(r)) return 'admin'
    if ([ 'patologo', 'pathologist', 'patólogo' ].includes(r)) return 'patologo'
    if ([ 'residente', 'resident' ].includes(r)) return 'residente'
    if ([ 'auxiliar', 'assistant', 'auxiliary' ].includes(r)) return 'auxiliar'
    if ([ 'facturacion', 'facturación', 'billing' ].includes(r)) return 'facturacion'
    return 'auxiliar'
  }

  /**
   * Get role label for display
   */
  const getRoleLabel = (role: UserRole): string => {
    const roleLabels: Record<UserRole, string> = {
      admin: 'Administrador',
      patologo: 'Patólogo',
      residente: 'Residente',
      auxiliar: 'Auxiliar',
      facturacion: 'Usuario de Facturación'
    }
    return roleLabels[role]
  }

  /**
   * Get role styles for UI
   */
  const getRoleStyles = (role: UserRole): string => {
    const roleStyles: Record<UserRole, string> = {
      admin: 'bg-purple-100 text-purple-800',
      patologo: 'bg-blue-100 text-blue-800',
      residente: 'bg-green-100 text-green-800',
      auxiliar: 'bg-gray-100 text-gray-800',
      facturacion: 'bg-orange-100 text-orange-800'
    }
    return roleStyles[role]
  }

  return {
    mapAuthRoleToUserRole,
    normalizeRole,
    getRoleLabel,
    getRoleStyles
  }
}

