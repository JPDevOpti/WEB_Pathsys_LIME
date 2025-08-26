import { casesApiService } from '../modules/cases/services'
import { apiClient } from '@/core/config/axios.config'

/**
 * Función para probar la integración completa del sistema de casos
 */
export async function testCaseIntegration() {
  console.log('🧪 Iniciando pruebas de integración de casos...')

  try {
    // 1. Verificar conexión básica con el backend
    console.log('🔄 1. Verificando conexión con backend...')
    const healthResponse = await apiClient.get('/health')
    console.log('✅ Backend health check:', healthResponse)

    // 2. Probar obtener lista de casos (debería devolver lista vacía o con casos existentes)
    console.log('🔄 2. Probando obtener lista de casos...')
    const casesResponse = await casesApiService.getCases({ limit: 5 })
    console.log('✅ Lista de casos obtenida:', {
      total: casesResponse.total,
      count: casesResponse.casos.length,
      casos: casesResponse.casos.map(c => ({ codigo: c.CasoCode, estado: c.estado }))
    })

    // 3. Probar crear un caso de prueba
    console.log('🔄 3. Probando crear caso de prueba...')
    
    const testCaseData = {
      CasoCode: `2025-${Date.now().toString().slice(-5)}`,
      paciente: {
        codigo: `PAC_TEST_${Date.now()}`,
        cedula: `TEST${Date.now()}`,
        nombre: 'Paciente de Prueba',
        edad: 30,
        sexo: 'Masculino',
        entidad_info: {
          codigo: 'ENT_TEST',
          nombre: 'EPS de Prueba'
        },
        tipo_atencion: 'Ambulatorio'
      },
      medico_solicitante: {
        nombre: 'Dr. Médico de Prueba'
      },
      muestras: [
        {
          region_cuerpo: 'Brazo izquierdo',
          pruebas: [
            {
              id: 'HIST001',
              nombre: 'Histopatología'
            }
          ]
        }
      ],
      estado: 'pendiente' as any,
      observaciones_generales: 'Caso de prueba para verificar integración'
    }

    const createResponse = await casesApiService.createCase(testCaseData)
    console.log('✅ Caso de prueba creado:', {
      codigo: createResponse.CasoCode,
      paciente: createResponse.paciente.nombre,
      estado: createResponse.estado
    })

    // 4. Verificar que el caso se puede obtener por código
    console.log('🔄 4. Probando obtener caso por código...')
    const getCaseResponse = await casesApiService.getCaseByCode(createResponse.CasoCode)
    console.log('✅ Caso obtenido por código:', {
      codigo: getCaseResponse.CasoCode,
      paciente: getCaseResponse.paciente.nombre
    })

    console.log('🎉 ¡Todas las pruebas de integración pasaron exitosamente!')
    return {
      success: true,
      testCaseCode: createResponse.CasoCode,
      message: 'Integración de casos funcionando correctamente'
    }

  } catch (error: any) {
    console.error('❌ Error en pruebas de integración:', error)
    console.error('❌ Detalles del error:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url
    })

    return {
      success: false,
      error: error.message,
      details: error.response?.data
    }
  }
}

/**
 * Función para limpiar casos de prueba
 */
export async function cleanupTestCases() {
  try {
    console.log('🧹 Limpiando casos de prueba...')
    
    // Obtener casos que empiecen con códigos de prueba
    const cases = await casesApiService.getCases({ limit: 100 })
    const testCases = cases.casos.filter(c => 
      c.CasoCode.includes('TEST') || 
      (c.paciente as any).nombre?.includes('Prueba')
    )

    console.log(`🔄 Encontrados ${testCases.length} casos de prueba para limpiar`)

    for (const testCase of testCases) {
      try {
        await casesApiService.deleteCase(testCase.CasoCode)
        console.log(`✅ Caso de prueba eliminado: ${testCase.CasoCode}`)
      } catch (error) {
        console.warn(`⚠️ No se pudo eliminar caso: ${testCase.CasoCode}`, error)
      }
    }

    console.log('✅ Limpieza de casos de prueba completada')
    return { success: true, cleaned: testCases.length }

  } catch (error: any) {
    console.error('❌ Error en limpieza de casos de prueba:', error)
    return { success: false, error: error.message }
  }
}
