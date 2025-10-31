import { ref, computed } from 'vue'
import { profileApiService } from '../services/profileApiService'

/**
 * Composable for signature management functionality
 */
export function useSignatureManager(userRole?: string, pathologistCode?: string) {
  const isDragOver = ref(false)
  const isUploading = ref(false)
  const selectedFile = ref<File | null>(null)
  const previewUrl = ref<string | null>(null)

  // Only allow functionality if user is pathologist
  const isPatologo = computed(() => userRole?.toLowerCase() === 'patologo')

  /**
   * Handle drag over event
   */
  const onDragOver = () => {
    isDragOver.value = true
  }

  /**
   * Handle drag leave event
   */
  const onDragLeave = () => {
    isDragOver.value = false
  }

  /**
   * Handle drop event
   */
  const onDrop = (event: DragEvent) => {
    isDragOver.value = false
    const files = event.dataTransfer?.files
    if (files && files.length > 0) {
      handleFile(files[0])
    }
  }

  /**
   * Handle file input change
   */
  const onFileChange = (event: Event) => {
    const input = event.target as HTMLInputElement
    const files = input.files
    if (files && files.length > 0) {
      handleFile(files[0])
    }
  }

  /**
   * Handle file processing
   */
  const handleFile = async (file: File) => {
    if (!isPatologo.value || !pathologistCode) return
    
    const isValidType = ['image/png', 'image/jpeg', 'image/svg+xml'].includes(file.type)
    const isValidSize = file.size <= 1024 * 1024 // 1MB
    
    if (!isValidType) {
      throw new Error('Formato de archivo no válido. Solo se permiten PNG, JPG y SVG.')
    }
    
    if (!isValidSize) {
      throw new Error('El archivo es demasiado grande. El tamaño máximo es 1MB.')
    }
    
    isUploading.value = true
    selectedFile.value = file
    
    try {
      // Upload file to backend
      const response = await profileApiService.uploadFirma(pathologistCode, file)
      if (response) {
        // Get signature URL from response
        const signatureUrl = response.signature
        if (signatureUrl) {
          previewUrl.value = signatureUrl.startsWith('http') 
            ? signatureUrl 
            : `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${signatureUrl}`
        } else {
          // Fallback: show local preview
          const reader = new FileReader()
          reader.onload = () => {
            previewUrl.value = typeof reader.result === 'string' ? reader.result : null
          }
          reader.readAsDataURL(file)
        }
      } else {
        throw new Error('No se pudo subir la firma')
      }
    } catch (error) {
      console.error('Error al subir firma:', error)
      // Fallback: show local preview
      const reader = new FileReader()
      reader.onload = () => {
        previewUrl.value = typeof reader.result === 'string' ? reader.result : null
      }
      reader.readAsDataURL(file)
      throw error
    } finally {
      isUploading.value = false
    }
  }

  /**
   * Remove signature
   */
  const remove = async () => {
    if (!isPatologo.value || !pathologistCode) return
    
    try {
      // Remove signature from backend
      await profileApiService.deleteFirma(pathologistCode)
      selectedFile.value = null
      previewUrl.value = null
    } catch (error) {
      console.error('Error al eliminar firma:', error)
      throw error
    }
  }

  /**
   * Set current URL (for initialization)
   */
  const setCurrentUrl = (url: string | null) => {
    if (url && isPatologo.value) {
      previewUrl.value = url
    } else if (!url) {
      previewUrl.value = null
    }
  }

  /**
   * Handle image load error
   */
  const handleImageError = (event: Event) => {
    const img = event.target as HTMLImageElement
    console.error('Error al cargar la imagen de firma:', img.src)
  }

  /**
   * Handle image load success
   */
  const handleImageLoad = (event: Event) => {
    const img = event.target as HTMLImageElement
    console.log('Imagen de firma cargada correctamente:', {
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      src: img.src.substring(0, 50) + '...'
    })
    
    // If image is too small, adjust size for better visualization
    if (img.naturalWidth < 100 || img.naturalHeight < 100) {
      const containerWidth = 200 // min-w-[200px] - padding
      const containerHeight = 120 // min-h-[120px] - padding
      const scaleX = containerWidth / img.naturalWidth
      const scaleY = containerHeight / img.naturalHeight
      const scale = Math.min(scaleX, scaleY, 5) // Maximum 5x to avoid distortion
      
      img.style.transform = `scale(${scale})`
      img.style.transformOrigin = 'center'
    }
  }

  return {
    // State
    isDragOver,
    isUploading,
    selectedFile,
    previewUrl,
    isPatologo,
    
    // Methods
    onDragOver,
    onDragLeave,
    onDrop,
    onFileChange,
    handleFile,
    remove,
    setCurrentUrl,
    handleImageError,
    handleImageLoad
  }
}
