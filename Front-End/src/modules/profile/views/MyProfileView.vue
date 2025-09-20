<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div class="p-3 sm:p-4 md:p-6">
      <div class="max-w-6xl mx-auto">
        <!-- Loading State -->
        <div v-if="isLoading" class="space-y-6">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="animate-pulse">
              <div class="flex items-center space-x-4 mb-6">
                <div class="w-24 h-24 bg-gray-200 rounded-full"></div>
                <div class="space-y-2">
                  <div class="h-6 bg-gray-200 rounded w-48"></div>
                  <div class="h-4 bg-gray-200 rounded w-32"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile Content -->
        <div v-else-if="userProfile" class="space-y-6">
          <!-- Profile Header -->
          <ProfileHeader 
            :user="userProfile" 
            :is-editable="true"
            @edit="openEditModal"
          />

          <!-- Profile Information Cards -->
          <ProfileInfoCards :user="userProfile" />

          <!-- Firma Digital - Solo para Patólogos -->
          <SignatureUploader
            v-if="userProfile.role === 'patologo'"
            :user-role="userProfile.role"
            :current-url="userProfile.roleSpecificData?.firmaUrl"
            :pathologist-code="getPathologistCode()"
            @change="handleSignatureChange"
          />
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="text-center">
            <ExclamationTriangleIcon class="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Error al cargar el perfil</h3>
            <p class="text-gray-600 mb-4">{{ error }}</p>
            <button
              @click="loadUserProfile"
              class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <ProfileEditModal
      v-if="userProfile"
      :is-open="isEditModalOpen"
      :user="userProfile"
      :is-loading="isSaving"
      :errors="editErrors"
      @close="closeEditModal"
      @submit="handleProfileUpdate"
    />

    <!-- Success Toast -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-300"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div
        v-if="showSuccessToast"
        class="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50"
      >
        <div class="flex items-center gap-2">
          <CheckCircleIcon class="w-5 h-5" />
          <span>Perfil actualizado correctamente</span>
        </div>
      </div>
    </Transition>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/common'
import { 
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

// Components
import ProfileHeader from '../components/MyProfile/ProfileHeader.vue'
import ProfileInfoCards from '../components/MyProfile/ProfileInfoCards.vue'
import ProfileEditModal from '../components/MyProfile/ProfileEditModal.vue'
import SignatureUploader from '../components/MyProfile/SignatureUploader.vue'

// Types and Services
import type { UserProfile, ValidationError, ProfileEditPayload, UserRole } from '../types/userProfile.types'
import { profileApiService } from '../services/profileApiService'
import { useAuthStore } from '@/stores/auth.store'
import type { BackendPatologo, BackendResidente, BackendAuxiliar, BackendFacturacion } from '../services/profileApiService'

const currentPageTitle = ref('Mi Perfil')

// State
const isLoading = ref(true)
const isSaving = ref(false)
const error = ref<string | null>(null)
const userProfile = ref<UserProfile | null>(null)
const isEditModalOpen = ref(false)
const editErrors = ref<ValidationError[]>([])
const showSuccessToast = ref(false)

// Methods
const loadUserProfile = async () => {
  try {
    isLoading.value = true
    error.value = null
    // Obtener usuario autenticado desde el store
    const authStore = useAuthStore()
    if (!authStore.user) {
      await authStore.initializeAuth()
    }
    const authUser = authStore.user
    if (!authUser) {
      throw new Error('No hay usuario autenticado')
    }

    const mapAuthRoleToUserRole = (rol?: string): UserRole => {
      const r = (rol || '').toString().trim().toLowerCase()
      console.log('🔍 Mapeando rol del token:', { original: rol, normalized: r })
      
      // Mapeo exacto primero
      if (r === 'pathologist' || r === 'patologo') return 'patologo'
      if (r === 'admin' || r === 'administrator' || r === 'administrador') return 'admin'
      if (r === 'resident' || r === 'residente') return 'residente'
      if (r === 'auxiliar' || r === 'auxiliary') return 'auxiliar'
      if (r === 'facturacion' || r === 'facturación' || r === 'billing') return 'facturacion'
      
      // Mapeo por contenido
      if (r.includes('admin')) return 'admin'
      if (r.includes('patolog')) return 'patologo'
      if (r.includes('resident')) return 'residente'
      if (r.includes('auxiliar')) return 'auxiliar'
      if (r.includes('facturacion') || r.includes('billing')) return 'facturacion'
      
      // Si no se reconoce el rol, intentar detectar por email o datos del usuario
      console.log('⚠️ Rol no reconocido, usando admin como fallback:', r)
      return 'admin'
    }

    const role = mapAuthRoleToUserRole(authUser.role)
    const email = authUser.email
    
    console.log('🔍 Información del usuario autenticado:', {
      authUser,
      roleFromAuth: authUser.role,
      mappedRole: role,
      email
    })

    // Base para UserProfile a partir del usuario autenticado
    const fullNameFromAuth = (authUser.nombre || ((authUser as any).nombres && (authUser as any).apellidos ? `${(authUser as any).nombres} ${(authUser as any).apellidos}` : '')).toString().trim()
    const [firstName, ...rest] = (fullNameFromAuth || '').split(' ').filter(Boolean)
    const lastName = rest.join(' ')
    const fallbackFirst = firstName || (email?.split('@')[0] || 'Usuario')
    const base = {
      id: authUser.id,
      firstName: fallbackFirst,
      lastName: lastName || '',
      email,
      isActive: authUser.activo ?? true,
      avatar: undefined,
      lastLogin: authUser.ultimo_acceso ? new Date(authUser.ultimo_acceso) : undefined,
      createdAt: new Date(),
      updatedAt: new Date()
    }

    // Buscar patólogo primero si el rol del token es patólogo
    let patologoData = undefined
    if (role === 'patologo') {
      console.log('🔍 Buscando datos de patólogo para:', email)
      patologoData = await profileApiService.getByRoleAndEmail('patologo', email).catch((error) => {
        console.error('Error al buscar patólogo:', error)
        return undefined
      })
      console.log('📋 Datos de patólogo encontrados:', patologoData)
    }
    
    // Si no se encontró patólogo, buscar en otros roles
    let residenteData, auxiliarData, facturacionData
    if (!patologoData) {
      [residenteData, auxiliarData, facturacionData] = await Promise.all([
        profileApiService.getByRoleAndEmail('residente', email).catch(() => undefined),
        profileApiService.getByRoleAndEmail('auxiliar', email).catch(() => undefined),
        profileApiService.getByRoleAndEmail('facturacion', email).catch(() => undefined)
      ])
    }

    const hasResidente = !!(residenteData && (residenteData as any).residenteCode)
    const hasAuxiliar = !!(auxiliarData && (auxiliarData as any).auxiliarCode)
    const hasPatologo = !!(patologoData && (patologoData as any).patologoCode)
    const hasFacturacion = !!(facturacionData && (facturacionData as BackendFacturacion).facturacionCode)
    
    console.log('🔍 Verificación de datos encontrados:', {
      role,
      hasPatologo,
      hasResidente,
      hasAuxiliar,
      hasFacturacion,
      patologoData: patologoData ? 'encontrado' : 'no encontrado'
    })

    console.log('🔍 Detección de roles:', {
      email,
      roleFromToken: role,
      hasResidente,
      hasAuxiliar,
      hasPatologo,
      hasFacturacion,
      facturacionData
    })

    // Determinar rol efectivo: priorizar patólogo si el token lo indica
    let effectiveRole: UserRole
    if (role === 'patologo' && hasPatologo) {
      effectiveRole = 'patologo'
    } else if (hasResidente) {
      effectiveRole = 'residente'
    } else if (hasFacturacion) {
      effectiveRole = 'facturacion'
    } else if (hasAuxiliar) {
      effectiveRole = 'auxiliar'
    } else if (hasPatologo) {
      effectiveRole = 'patologo'
    } else {
      effectiveRole = role
    }

    console.log('✅ Rol efectivo detectado:', effectiveRole)

    if (effectiveRole === 'patologo') {
      if (!patologoData) {
        console.warn('⚠️ No se encontraron datos específicos de patólogo, usando perfil básico')
        // Usar perfil básico si no se encuentran datos específicos
        userProfile.value = {
          ...base,
          role: 'patologo',
          roleSpecificData: {
            iniciales: '',
            registroMedico: '',
            firmaUrl: '',
            observaciones: '',
            patologoCode: '',
            pathologistCode: ''
          }
        }
        return
      }
      const pb = patologoData as BackendPatologo | undefined
      // Separar el nombre completo del patólogo
      const fullName = pb?.patologoName || base.firstName + ' ' + base.lastName
      const [firstName, ...rest] = fullName.split(' ').filter(Boolean)
      userProfile.value = {
        ...base,
        firstName: firstName || base.firstName,
        lastName: rest.join(' ') || base.lastName,
        document: '',
        documentType: 'CC',
        phone: '',
        role: 'patologo',
        roleSpecificData: {
          iniciales: (pb as any)?.InicialesPatologo || (pb as any)?.iniciales || '',
          registroMedico: pb?.registro_medico || '',
          firmaUrl: pb?.firma || '',
          observaciones: pb?.observaciones || '',
          patologoCode: pb?.patologoCode || '',
          pathologistCode: pb?.patologoCode || ''
        }
      } as any
      return
    }

    if (effectiveRole === 'residente') {
      const rb = residenteData as BackendResidente | undefined
      // Separar el nombre completo del residente
      const fullName = rb?.residenteName || base.firstName + ' ' + base.lastName
      const [firstName, ...rest] = fullName.split(' ').filter(Boolean)
      userProfile.value = {
        ...base,
        firstName: firstName || base.firstName,
        lastName: rest.join(' ') || base.lastName,
        document: '',
        documentType: 'CC',
        phone: '',
        role: 'residente',
        roleSpecificData: {
          iniciales: (rb as any)?.InicialesResidente || (rb as any)?.iniciales || (rb as any)?.inicialesResidente || '',
          registroMedico: rb?.registro_medico || '',
          observaciones: rb?.observaciones || ''
        }
      } as any
      return
    }

    if (effectiveRole === 'auxiliar') {
      const ab = auxiliarData as BackendAuxiliar | undefined
      // Separar el nombre completo del auxiliar
      const fullName = ab?.auxiliarName || base.firstName + ' ' + base.lastName
      const [firstName, ...rest] = fullName.split(' ').filter(Boolean)
      userProfile.value = {
        ...base,
        firstName: firstName || base.firstName,
        lastName: rest.join(' ') || base.lastName,
        document: '',
        documentType: 'CC',
        phone: '',
        role: 'auxiliar',
        roleSpecificData: {
          observaciones: ab?.observaciones || ''
        }
      } as any
      return
    }

    if (effectiveRole === 'facturacion') {
      const fb = facturacionData as BackendFacturacion | undefined
      // Separar el nombre completo del usuario de facturación
      const fullName = fb?.facturacionName || base.firstName + ' ' + base.lastName
      const [firstName, ...rest] = fullName.split(' ').filter(Boolean)
      userProfile.value = {
        ...base,
        firstName: firstName || base.firstName,
        lastName: rest.join(' ') || base.lastName,
        document: '',
        documentType: 'CC',
        phone: '',
        role: 'facturacion',
        roleSpecificData: {
          observaciones: fb?.observaciones || ''
        }
      } as any
      return
    }

    // Default a admin si no se encuentra en ninguna colección
    userProfile.value = {
      ...base,
      document: '',
      documentType: 'CC',
      phone: '',
      role: 'admin',
      roleSpecificData: {}
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error desconocido'
  } finally {
    isLoading.value = false
  }
}

const openEditModal = () => {
  isEditModalOpen.value = true
  editErrors.value = []
}

const closeEditModal = () => {
  isEditModalOpen.value = false
  editErrors.value = []
}

const handleProfileUpdate = async (formData: ProfileEditPayload) => {
  try {
    isSaving.value = true
    editErrors.value = []
    
  // Integración backend por rol: se obtienen datos por email y luego se hace PUT usando el código detectado.
    if (userProfile.value) {
      if (formData.role === 'admin') {
        userProfile.value.firstName = formData.firstName
        userProfile.value.lastName = formData.lastName
        userProfile.value.email = formData.email
      } else if (formData.role === 'patologo') {
        const p = await profileApiService.getByRoleAndEmail('patologo', userProfile.value.email) as BackendPatologo | undefined
        const code = p?.patologoCode || ''
        await profileApiService.updateByRole('patologo', code, {
          patologoName: formData.patologoName,
          InicialesPatologo: formData.InicialesPatologo,
          PatologoEmail: formData.PatologoEmail,
          registro_medico: formData.registro_medico,
          observaciones: formData.observaciones,
          password: formData.password
        })
        // Actualización local
        const [firstName, ...rest] = formData.patologoName.split(' ').filter(Boolean)
        userProfile.value.firstName = firstName || userProfile.value.firstName
        userProfile.value.lastName = rest.join(' ') || userProfile.value.lastName
        userProfile.value.email = formData.PatologoEmail
        userProfile.value.roleSpecificData = {
          ...userProfile.value.roleSpecificData,
          iniciales: formData.InicialesPatologo || '',
          registroMedico: formData.registro_medico,
          observaciones: formData.observaciones || ''
        }
      } else if (formData.role === 'residente') {
        const r = await profileApiService.getByRoleAndEmail('residente', userProfile.value.email) as BackendResidente | undefined
        const code = r?.residenteCode || ''
        await profileApiService.updateByRole('residente', code, {
          residenteName: formData.residenteName,
          InicialesResidente: formData.InicialesResidente,
          ResidenteEmail: formData.ResidenteEmail,
          registro_medico: formData.registro_medico,
          observaciones: formData.observaciones,
          password: formData.password
        })
        // Actualización local
        const [firstName, ...rest] = formData.residenteName.split(' ').filter(Boolean)
        userProfile.value.firstName = firstName || userProfile.value.firstName
        userProfile.value.lastName = rest.join(' ') || userProfile.value.lastName
        userProfile.value.email = formData.ResidenteEmail
        userProfile.value.roleSpecificData = {
          ...userProfile.value.roleSpecificData,
          iniciales: formData.InicialesResidente || '',
          registroMedico: formData.registro_medico,
          observaciones: formData.observaciones || ''
        }
      } else if (formData.role === 'auxiliar') {
        const a = await profileApiService.getByRoleAndEmail('auxiliar', userProfile.value.email) as BackendAuxiliar | undefined
        const code = a?.auxiliarCode || ''
        await profileApiService.updateByRole('auxiliar', code, {
          auxiliarName: formData.auxiliarName,
          AuxiliarEmail: formData.AuxiliarEmail,
          observaciones: formData.observaciones,
          password: formData.password
        })
        // Actualizar datos locales
        const [firstName, ...rest] = formData.auxiliarName.split(' ').filter(Boolean)
        userProfile.value.firstName = firstName || userProfile.value.firstName
        userProfile.value.lastName = rest.join(' ') || userProfile.value.lastName
        userProfile.value.email = formData.AuxiliarEmail
        userProfile.value.roleSpecificData = {
          ...userProfile.value.roleSpecificData,
          observaciones: formData.observaciones || ''
        }
      } else if (formData.role === 'facturacion') {
        const f = await profileApiService.getByRoleAndEmail('facturacion', userProfile.value.email) as BackendFacturacion | undefined
        const code = f?.facturacionCode || ''
        await profileApiService.updateByRole('facturacion', code, {
          facturacionName: formData.facturacionName,
          FacturacionEmail: formData.FacturacionEmail,
          observaciones: formData.observaciones,
          password: formData.password
        })
        // Actualización local
        const [firstName, ...rest] = formData.facturacionName.split(' ').filter(Boolean)
        userProfile.value.firstName = firstName || userProfile.value.firstName
        userProfile.value.lastName = rest.join(' ') || userProfile.value.lastName
        userProfile.value.email = formData.FacturacionEmail
        userProfile.value.roleSpecificData = {
          ...userProfile.value.roleSpecificData,
          observaciones: formData.observaciones || ''
        }
      }
    }
    
    closeEditModal()
    showSuccessMessage()
  } catch (err) {
    if (err instanceof Error) {
      editErrors.value = [{ field: 'general', message: err.message }]
    }
  } finally {
    isSaving.value = false
  }
}

const showSuccessMessage = () => {
  showSuccessToast.value = true
  setTimeout(() => {
    showSuccessToast.value = false
  }, 3000)
}

// Obtener código del patólogo
const getPathologistCode = (): string => {
  if (!userProfile.value || userProfile.value.role !== 'patologo') return ''
  
  // Buscar el código en los datos específicos del rol
  const roleData = userProfile.value.roleSpecificData as any
  return roleData?.patologoCode || roleData?.pathologistCode || ''
}

// Manejo de la firma digital
const handleSignatureChange = async (payload: { file: File | null; previewUrl: string | null }) => {
  try {
    if (!userProfile.value || userProfile.value.role !== 'patologo') return

    const pathologistCode = getPathologistCode()
    if (!pathologistCode) {
      throw new Error('No se pudo obtener el código del patólogo')
    }

    // Actualizar la firma en el backend
    await profileApiService.updateFirma(pathologistCode, payload.previewUrl || '')

    // Actualizar localmente
    if (userProfile.value.roleSpecificData) {
      userProfile.value.roleSpecificData.firmaUrl = payload.previewUrl || undefined
    } else {
      userProfile.value.roleSpecificData = {
        firmaUrl: payload.previewUrl || undefined
      }
    }

    // Sincronizar con el store para que otras vistas (p.ej. SignResults) detecten la firma
    try {
      const auth = useAuthStore()
      if (auth.user) {
        ;(auth.user as any).firma = payload.previewUrl || ''
        ;(auth.user as any).firma_url = payload.previewUrl || ''
        ;(auth.user as any).signatureUrl = payload.previewUrl || ''
        ;(auth.user as any).firmaDigital = payload.previewUrl || ''
      }
      try { localStorage.setItem('signature_url', payload.previewUrl || '') } catch {}
      try { sessionStorage.setItem('signature_url', payload.previewUrl || '') } catch {}
    } catch {}

    // Mostrar mensaje de éxito
    showSuccessMessage()
  } catch (error) {
    console.error('Error al actualizar la firma:', error)
    // TODO: Mostrar mensaje de error al usuario
  }
}

// No hay selector de rol: se usa el rol del usuario autenticado


// Lifecycle
onMounted(() => {
  loadUserProfile()
})
</script>
