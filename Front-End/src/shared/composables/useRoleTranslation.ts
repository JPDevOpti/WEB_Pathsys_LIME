/**
 * Composable para traducir roles del backend (inglés) al frontend (español)
 */

export function useRoleTranslation() {
  const roleMap: Record<string, string> = {
    administrator: 'Administrador',
    admin: 'Administrador',
    pathologist: 'Patólogo',
    auxiliary: 'Auxiliar',
    receptionist: 'Auxiliar',
    resident: 'Residente',
    billing: 'Usuario de Facturación',
    patient: 'Paciente',
    receptionist: 'Recepcionista'
  }

  const translateRole = (role: string): string => {
    const normalizedRole = role?.toString().trim().toLowerCase() || ''
    return roleMap[normalizedRole] || (normalizedRole.charAt(0).toUpperCase() + normalizedRole.slice(1))
  }

  const getRoleIcon = (role: string) => {
    const normalizedRole = role?.toString().trim().toLowerCase() || ''
    
    if (normalizedRole.includes('admin')) return 'SettingsIcon'
    if (normalizedRole.includes('pathologist')) return 'DoctorIcon'
    if (normalizedRole.includes('resident')) return 'ResidenteIcon'
    if (normalizedRole.includes('auxiliary') || normalizedRole.includes('auxiliar') || normalizedRole.includes('receptionist')) return 'AuxiliarIcon'
    if (normalizedRole.includes('billing') || normalizedRole.includes('user')) return 'DolarIcon'
    
    return 'UserCircleIcon'
  }

  return {
    roleMap,
    translateRole,
    getRoleIcon
  }
}
