import type { UserProfile, ProfileFormData, UserRole } from '../types/userProfile.types'

// Mock data for different user roles
const mockUsers: Record<UserRole, UserProfile> = {
  admin: {
    id: '1',
    firstName: 'Carlos',
    lastName: 'Administrador',
    email: 'carlos.admin@laboratorio.com',
    phone: '+57 300 123 4567',
    document: '12345678',
    documentType: 'CC',
    role: 'admin',
    avatar: '/images/user/admin.jpg',
    isActive: true,
    lastLogin: new Date('2024-01-15T14:30:00'),
    createdAt: new Date('2023-01-01T00:00:00'),
    updatedAt: new Date('2024-01-15T14:30:00'),
    roleSpecificData: {
      observaciones: 'Administrador del sistema'
    }
  },
  patologo: {
    id: '2',
    firstName: 'Juan Carlos',
    lastName: 'Pérez',
    email: 'juan.perez@laboratorio.com',
    phone: '+57 300 234 5678',
    document: '23456789',
    documentType: 'CC',
    role: 'patologo',
    avatar: '/images/user/patologo.jpg',
    isActive: true,
    lastLogin: new Date('2024-01-15T16:45:00'),
    createdAt: new Date('2023-02-15T00:00:00'),
    updatedAt: new Date('2024-01-15T16:45:00'),
    roleSpecificData: {
      iniciales: 'JCP',
      registroMedico: 'RM-12345',
      firmaUrl: '',
      observaciones: 'Especialista con 10 años de experiencia'
    }
  },
  residente: {
    id: '3',
    firstName: 'María',
    lastName: 'González',
    email: 'maria.gonzalez@laboratorio.com',
    phone: '+57 300 345 6789',
    document: '34567890',
    documentType: 'CC',
    role: 'residente',
    avatar: '/images/user/residente.jpg',
    isActive: true,
    lastLogin: new Date('2024-01-15T09:15:00'),
    createdAt: new Date('2023-06-01T00:00:00'),
    updatedAt: new Date('2024-01-15T09:15:00'),
    roleSpecificData: {
      iniciales: 'MG',
      registroMedico: 'RM-2024-001',
      observaciones: 'Residente de segundo año en patología'
    }
  },
  auxiliar: {
    id: '5',
    firstName: 'Pedro',
    lastName: 'López',
    email: 'pedro.lopez@laboratorio.com',
    phone: '+57 300 567 8901',
    document: '56789012',
    documentType: 'CC',
    role: 'auxiliar',
    avatar: '/images/user/auxiliar.jpg',
    isActive: true,
    lastLogin: new Date('2024-01-15T07:30:00'),
    createdAt: new Date('2023-04-20T00:00:00'),
    updatedAt: new Date('2024-01-15T07:30:00'),
    roleSpecificData: {
      observaciones: 'Auxiliar con experiencia en laboratorio'
    }
  }
}

// Simulate current logged user (defaults to patólogo if no auth user)
let currentUser: UserProfile = mockUsers.patologo

export class MockProfileService {
  /**
   * Get current user profile
   */
  static async getCurrentUserProfile(): Promise<UserProfile> {
    await new Promise(resolve => setTimeout(resolve, 200))
    return { ...currentUser }
  }

  /**
   * Update user profile
   */
  static async updateUserProfile(data: ProfileFormData): Promise<UserProfile> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Simulate potential API error (5% chance)
    if (Math.random() < 0.05) {
      throw new Error('Error de conexión. Por favor, intente nuevamente.')
    }

    // Update current user data
    currentUser = {
      ...currentUser,
      firstName: data.firstName,
      lastName: data.lastName,
      email: data.email,
      phone: data.phone,
      document: data.document,
      documentType: data.documentType,
      updatedAt: new Date()
    }

    return { ...currentUser }
  }

  /**
   * Change current user for demo purposes
   */
  static setCurrentUser(role: UserRole): void {
    currentUser = mockUsers[role]
  }

  // Eliminado selector de roles de demo

  /**
   * Validate profile data
   */
  static validateProfileData(data: ProfileFormData): string[] {
    const errors: string[] = []

    if (!data.firstName.trim()) {
      errors.push('El nombre es requerido')
    }

    if (!data.lastName.trim()) {
      errors.push('El apellido es requerido')
    }

    if (!data.email.trim()) {
      errors.push('El email es requerido')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.push('El email no tiene un formato válido')
    }

    if (!data.document.trim()) {
      errors.push('El documento es requerido')
    } else if (!/^\d{8,12}$/.test(data.document)) {
      errors.push('El documento debe tener entre 8 y 12 dígitos')
    }

    if (data.phone && !/^\+?[\d\s-()]{10,}$/.test(data.phone)) {
      errors.push('El teléfono no tiene un formato válido')
    }

    return errors
  }
}