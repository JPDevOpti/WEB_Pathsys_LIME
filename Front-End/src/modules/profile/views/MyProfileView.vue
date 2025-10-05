<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="p-3 sm:p-4 md:p-6">
      <div class="max-w-6xl mx-auto">
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

        <div v-else-if="userProfile" class="space-y-6">
          <ProfileHeader 
            :user="userProfile" 
            :is-editable="true"
            @edit="openEditModal"
          />
          <ProfileInfo :user="userProfile" />
          <SignatureManager
            v-if="userProfile.role === 'patologo'"
            :user-role="userProfile.role"
            :current-url="userProfile.roleSpecificData?.firmaUrl"
            :pathologist-code="getPathologistCode()"
            @change="handleSignatureChange"
          />
        </div>

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

    <EditModal
      v-if="userProfile"
      :is-open="isEditModalOpen"
      :user="userProfile"
      :is-loading="isSaving"
      :errors="editErrors"
      @close="closeEditModal"
      @submit="handleProfileUpdate"
    />

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
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import { ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import ProfileHeader from '../components/MyProfile/ProfileHeader.vue'
import ProfileInfo from '../components/MyProfile/ProfileInfo.vue'
import EditModal from '../components/MyProfile/EditModal.vue'
import SignatureManager from '../components/MyProfile/SignatureManager.vue'
import type { UserProfile, ValidationError, ProfileEditPayload, UserRole } from '../types/userProfile.types'
import { profileApiService } from '../services/profileApiService'
import { useAuthStore } from '@/stores/auth.store'
import type { BackendPatologo, BackendResidente, BackendAuxiliar, BackendFacturacion } from '../services/profileApiService'

const currentPageTitle = ref('Mi Perfil')
const isLoading = ref(true)
const isSaving = ref(false)
const error = ref<string | null>(null)
const userProfile = ref<UserProfile | null>(null)
const isEditModalOpen = ref(false)
const editErrors = ref<ValidationError[]>([])
const showSuccessToast = ref(false)

const loadUserProfile = async () => {
  try {
    isLoading.value = true
    error.value = null
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

    const role = mapAuthRoleToUserRole(authUser.role)
    const email = authUser.email
    const fullNameFromAuth = ((authUser as any).nombre || ((authUser as any).nombres && (authUser as any).apellidos ? `${(authUser as any).nombres} ${(authUser as any).apellidos}` : '')).toString().trim()
    const [firstName, ...rest] = (fullNameFromAuth || '').split(' ').filter(Boolean)
    const lastName = rest.join(' ')
    const fallbackFirst = firstName || (email?.split('@')[0] || 'Usuario')
    const base = {
      id: authUser.id,
      firstName: fallbackFirst,
      lastName: lastName || '',
      email,
      isActive: (authUser as any).activo ?? true,
      avatar: undefined,
      lastLogin: (authUser as any).ultimo_acceso ? new Date((authUser as any).ultimo_acceso) : undefined,
      createdAt: new Date(),
      updatedAt: new Date()
    }

    let patologoData = undefined
    if (role === 'patologo') {
      patologoData = await profileApiService.getByRoleAndEmail('patologo', email).catch(() => undefined)
    }
    
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

    const createProfile = (roleData: any, roleType: UserRole, nameField: string, initialsField?: string) => {
      const fullName = roleData?.[nameField] || base.firstName + ' ' + base.lastName
      const [firstName, ...rest] = fullName.split(' ').filter(Boolean)
      return {
        ...base,
        firstName: firstName || base.firstName,
        lastName: rest.join(' ') || base.lastName,
        document: '',
        documentType: 'CC',
        phone: '',
        role: roleType,
        roleSpecificData: {
          ...(initialsField && { iniciales: roleData?.[initialsField] || '' }),
          ...(roleData?.registro_medico && { registroMedico: roleData.registro_medico }),
          ...(roleData?.firma && { firmaUrl: roleData.firma }),
          ...(roleData?.observaciones && { observaciones: roleData.observaciones }),
          ...(roleData?.patologoCode && { patologoCode: roleData.patologoCode, pathologistCode: roleData.patologoCode })
        }
      }
    }

    if (effectiveRole === 'patologo') {
      if (!patologoData) {
        userProfile.value = {
          ...base,
          document: '',
          documentType: 'CC',
          phone: '',
          role: 'patologo',
          roleSpecificData: {
            iniciales: '',
            registroMedico: '',
            firmaUrl: '',
            observaciones: ''
          } as any
        }
        return
      }
      userProfile.value = createProfile(patologoData, 'patologo', 'patologoName', 'InicialesPatologo') as any
      return
    }

    if (effectiveRole === 'residente') {
      userProfile.value = createProfile(residenteData, 'residente', 'residenteName', 'InicialesResidente') as any
      return
    }

    if (effectiveRole === 'auxiliar') {
      userProfile.value = createProfile(auxiliarData, 'auxiliar', 'auxiliarName') as any
      return
    }

    if (effectiveRole === 'facturacion') {
      userProfile.value = createProfile(facturacionData, 'facturacion', 'facturacionName') as any
      return
    }

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
    
    if (userProfile.value) {
      const updateLocalProfile = (name: string, email: string, initials?: string) => {
        const [firstName, ...rest] = name.split(' ').filter(Boolean)
        userProfile.value!.firstName = firstName || userProfile.value!.firstName
        userProfile.value!.lastName = rest.join(' ') || userProfile.value!.lastName
        userProfile.value!.email = email
        if (initials) {
          userProfile.value!.roleSpecificData = {
            ...userProfile.value!.roleSpecificData,
            iniciales: initials,
            registroMedico: (formData as any).registro_medico,
            observaciones: (formData as any).observaciones || ''
          }
        } else {
          userProfile.value!.roleSpecificData = {
            ...userProfile.value!.roleSpecificData,
            observaciones: (formData as any).observaciones || ''
          }
        }
      }

      if (formData.role === 'admin') {
        userProfile.value.firstName = formData.firstName
        userProfile.value.lastName = formData.lastName
        userProfile.value.email = formData.email
      } else if (formData.role === 'patologo') {
        const p = await profileApiService.getByRoleAndEmail('patologo', userProfile.value.email) as BackendPatologo | undefined
        const code = p?.patologoCode || ''
        const updateData: any = {
          patologoName: formData.patologoName,
          InicialesPatologo: formData.InicialesPatologo,
          PatologoEmail: formData.PatologoEmail,
          registro_medico: formData.registro_medico,
          observaciones: formData.observaciones
        }
        if (formData.password && formData.password.trim()) {
          updateData.password = formData.password
        }
        await profileApiService.updateByRole('patologo', code, updateData)
        updateLocalProfile(formData.patologoName, formData.PatologoEmail, formData.InicialesPatologo)
      } else if (formData.role === 'residente') {
        const r = await profileApiService.getByRoleAndEmail('residente', userProfile.value.email) as BackendResidente | undefined
        const code = r?.residenteCode || ''
        const updateData: any = {
          residenteName: formData.residenteName,
          InicialesResidente: formData.InicialesResidente,
          ResidenteEmail: formData.ResidenteEmail,
          registro_medico: formData.registro_medico,
          observaciones: formData.observaciones
        }
        if (formData.password && formData.password.trim()) {
          updateData.password = formData.password
        }
        await profileApiService.updateByRole('residente', code, updateData)
        updateLocalProfile(formData.residenteName, formData.ResidenteEmail, formData.InicialesResidente)
      } else if (formData.role === 'auxiliar') {
        const a = await profileApiService.getByRoleAndEmail('auxiliar', userProfile.value.email) as BackendAuxiliar | undefined
        const code = a?.auxiliarCode || ''
        const updateData: any = {
          auxiliarName: formData.auxiliarName,
          AuxiliarEmail: formData.AuxiliarEmail,
          observaciones: formData.observaciones
        }
        if (formData.password && formData.password.trim()) {
          updateData.password = formData.password
        }
        await profileApiService.updateByRole('auxiliar', code, updateData)
        updateLocalProfile(formData.auxiliarName, formData.AuxiliarEmail)
      } else if (formData.role === 'facturacion') {
        const f = await profileApiService.getByRoleAndEmail('facturacion', userProfile.value.email) as BackendFacturacion | undefined
        const code = f?.facturacionCode || ''
        const updateData: any = {
          facturacionName: formData.facturacionName,
          FacturacionEmail: formData.FacturacionEmail,
          observaciones: formData.observaciones
        }
        if (formData.password && formData.password.trim()) {
          updateData.password = formData.password
        }
        await profileApiService.updateByRole('facturacion', code, updateData)
        updateLocalProfile(formData.facturacionName, formData.FacturacionEmail)
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

const getPathologistCode = (): string => {
  if (!userProfile.value || userProfile.value.role !== 'patologo') return ''
  const roleData = userProfile.value.roleSpecificData as any
  return roleData?.patologoCode || roleData?.pathologistCode || ''
}

const handleSignatureChange = async (payload: { file: File | null; previewUrl: string | null }) => {
  try {
    if (!userProfile.value || userProfile.value.role !== 'patologo') return

    const pathologistCode = getPathologistCode()
    if (!pathologistCode) {
      throw new Error('No se pudo obtener el código del patólogo')
    }

    await profileApiService.updateFirma(pathologistCode, payload.previewUrl || '')

    if (userProfile.value.roleSpecificData) {
      userProfile.value.roleSpecificData.firmaUrl = payload.previewUrl || undefined
    } else {
      userProfile.value.roleSpecificData = {
        firmaUrl: payload.previewUrl || undefined
      }
    }

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

    showSuccessMessage()
  } catch (error) {
    console.error('Error al actualizar la firma:', error)
  }
}

onMounted(() => {
  loadUserProfile()
})
</script>
