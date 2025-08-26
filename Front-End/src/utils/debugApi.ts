import { apiClient } from '@/core/config/axios.config'

/**
 * Función temporal para testear la conexión con el backend
 */
export async function testBackendConnection() {
  try {
    console.log('🔄 Probando conexión con el backend...')
    
    // Test simple: obtener casos (endpoint que sabemos que funciona)
    const response = await apiClient.get('/casos')
    console.log('✅ Backend conectado correctamente:', response)
    
    // Test específico: endpoint de pacientes
    const patientsResponse = await apiClient.get('/pacientes')
    console.log('✅ Endpoint de pacientes disponible:', patientsResponse)
    
    return true
  } catch (error: any) {
    console.error('❌ Error de conexión con backend:', error)
    console.error('❌ Detalles del error:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      baseURL: error.config?.baseURL
    })
    return false
  }
}

// Función para testear crear paciente con datos mínimos
export async function testCreatePatient() {
  try {
    console.log('🔄 Probando crear paciente...')
    
    const testPatient = {
      nombre: "Test Patient " + Date.now(),
      edad: 30,
      sexo: "Masculino",
      entidad_info: {
        id: "ent_001",
        nombre: "EPS Sanitas"
      },
      tipo_atencion: "Ambulatorio",
      cedula: "TEST" + Date.now()
    }
    
    const response = await apiClient.post('/pacientes', testPatient)
    console.log('✅ Paciente de prueba creado exitosamente:', response)
    
    return response
  } catch (error: any) {
    console.error('❌ Error al crear paciente de prueba:', error)
    console.error('❌ Detalles:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url
    })
    return null
  }
}
