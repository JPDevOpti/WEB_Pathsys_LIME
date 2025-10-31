import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth.store'

// Manejador simple para notificación centrada de firma faltante
// Comentario: Verifica sesión y rol, muestra alerta una vez por sesión.
const visible = ref(false)

function hasSignature(u: any): boolean {
  try {
    // Comentario: Detectar firma solo con datos actuales del usuario y sesión;
    // evitar usar localStorage para no arrastrar valores de sesiones previas.
    let sig: string | null = u?.firma || u?.firma_url || u?.signatureUrl || u?.firmaDigital || null
    // Priorizar sesión actual; no consultar localStorage para prevenir falsos positivos.
    sig = sig || sessionStorage.getItem('signature_url')
    return !!(sig && sig.toString().trim())
  } catch {
    return false
  }
}

function checkAndShowOncePerSession(): void {
  const authStore = useAuthStore()
  try {
    const shownKey = 'signature_missing_notified'
    const alreadyShown = sessionStorage.getItem(shownKey)
    const isPatologist = authStore.isPathologist
    const isAuth = authStore.isAuthenticated
    const user = authStore.user as any
    if (!alreadyShown && isAuth && isPatologist && !hasSignature(user)) {
      visible.value = true
      sessionStorage.setItem(shownKey, '1')
    }
  } catch {}
}

function close(): void {
  visible.value = false
}

export function useSignatureNotifier() {
  return { visible, checkAndShowOncePerSession, close }
}