import { testCaseIntegration, cleanupTestCases } from './testCaseIntegration'

/**
 * Función global para probar la integración desde la consola del navegador
 * 
 * Para usar en la consola del navegador:
 * 1. Abrir DevTools (F12)
 * 2. Ir a la pestaña Console
 * 3. Ejecutar: window.testCaseBackend()
 */
export async function initializeTestConsole() {
  // Hacer las funciones disponibles globalmente
  (window as any).testCaseBackend = testCaseIntegration;
  (window as any).cleanupTestCases = cleanupTestCases;
  

}

// Auto-inicializar en desarrollo
if (import.meta.env.DEV) {
  initializeTestConsole()
}
