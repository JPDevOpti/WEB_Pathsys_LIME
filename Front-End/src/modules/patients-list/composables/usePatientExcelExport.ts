import { ref } from 'vue'
import * as XLSX from 'xlsx'
import type { Patient } from '../types/patient.types'
import { formatDate, formatDateTime } from '../utils/dateUtils'
import { getIdentificationTypeLabel, getGenderLabel } from '../types/patient.types'

export function usePatientExcelExport() {
  const isExporting = ref(false)

  const exportPatientsToExcel = async (patients: Patient[], filename?: string) => {
    if (!patients || patients.length === 0) {
      throw new Error('No hay pacientes para exportar')
    }

    isExporting.value = true

    try {
      // Preparar los datos para Excel con los campos correctos del backend
      const excelData = patients.map((patient, index) => ({
        'No.': index + 1,
        'Código Paciente': patient.patient_code || '',
        'Tipo ID': getIdentificationTypeLabel(patient.identification_type),
        'Número ID': patient.identification_number || '',
        'Primer Nombre': patient.first_name || '',
        'Segundo Nombre': patient.second_name || '',
        'Primer Apellido': patient.first_lastname || '',
        'Segundo Apellido': patient.second_lastname || '',
        'Nombre Completo': patient.full_name || '',
        'Género': patient.gender || '',
        'Género (Corto)': getGenderLabel(patient.gender),
        'Fecha Nacimiento': patient.birth_date ? formatDate(patient.birth_date) : '',
        'Edad': patient.age || 0,
        'Municipio Código': patient.location?.municipality_code || '',
        'Municipio': patient.location?.municipality_name || '',
        'Subregión': patient.location?.subregion || '',
        'Dirección': patient.location?.address || '',
        'Entidad ID': patient.entity_info?.id || '',
        'Entidad': patient.entity_info?.name || '',
        'Tipo Atención': patient.care_type || '',
        'Observaciones': patient.observations || '',
        'Fecha Creación': patient.created_at ? formatDateTime(patient.created_at) : '',
        'Última Actualización': patient.updated_at ? formatDateTime(patient.updated_at) : ''
      }))

      // Crear el libro de trabajo
      const workbook = XLSX.utils.book_new()
      const worksheet = XLSX.utils.json_to_sheet(excelData)

      // Configurar el ancho de las columnas
      const columnWidths = [
        { wch: 5 },   // No.
        { wch: 15 },  // Código Paciente
        { wch: 10 },  // Tipo ID
        { wch: 15 },  // Número ID
        { wch: 15 },  // Primer Nombre
        { wch: 15 },  // Segundo Nombre
        { wch: 15 },  // Primer Apellido
        { wch: 15 },  // Segundo Apellido
        { wch: 30 },  // Nombre Completo
        { wch: 12 },  // Género
        { wch: 8 },   // Género (Corto)
        { wch: 15 },  // Fecha Nacimiento
        { wch: 8 },   // Edad
        { wch: 12 },  // Municipio Código
        { wch: 20 },  // Municipio
        { wch: 20 },  // Subregión
        { wch: 30 },  // Dirección
        { wch: 15 },  // Entidad ID
        { wch: 25 },  // Entidad
        { wch: 15 },  // Tipo Atención
        { wch: 40 },  // Observaciones
        { wch: 18 },  // Fecha Creación
        { wch: 18 }   // Última Actualización
      ]
      worksheet['!cols'] = columnWidths

      // Agregar la hoja al libro
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Pacientes')

      // Generar el nombre del archivo
      const defaultFilename = `pacientes_${new Date().toISOString().split('T')[0]}.xlsx`
      const finalFilename = filename || defaultFilename

      // Descargar el archivo
      XLSX.writeFile(workbook, finalFilename)

      return {
        success: true,
        filename: finalFilename,
        recordCount: patients.length
      }
    } catch (error) {
      console.error('Error al generar Excel:', error)
      throw new Error('Error al generar el archivo Excel')
    } finally {
      isExporting.value = false
    }
  }

  const exportSelectedPatients = async (selectedPatients: Patient[]) => {
    if (!selectedPatients || selectedPatients.length === 0) {
      throw new Error('No hay pacientes seleccionados para exportar')
    }

    const filename = `pacientes_seleccionados_${new Date().toISOString().split('T')[0]}.xlsx`
    return await exportPatientsToExcel(selectedPatients, filename)
  }

  const exportPatientStats = async (patients: Patient[]) => {
    if (!patients || patients.length === 0) {
      throw new Error('No hay datos de pacientes para generar estadísticas')
    }

    isExporting.value = true

    try {
      // Estadísticas por entidad
      const byEntity = patients.reduce((acc, patient) => {
        const entity = patient.entity_info?.name || 'Sin entidad'
        acc[entity] = (acc[entity] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      // Estadísticas por género
      const byGender = patients.reduce((acc, patient) => {
        const gender = patient.gender || 'No especificado'
        acc[gender] = (acc[gender] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      // Estadísticas por tipo de atención
      const byCareType = patients.reduce((acc, patient) => {
        const type = patient.care_type || 'No especificado'
        acc[type] = (acc[type] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      // Estadísticas por grupo de edad
      const byAgeGroup = patients.reduce((acc, patient) => {
        const age = patient.age || 0
        let group = 'No especificado'
        if (age >= 0 && age <= 17) group = '0-17 años'
        else if (age >= 18 && age <= 30) group = '18-30 años'
        else if (age >= 31 && age <= 50) group = '31-50 años'
        else if (age >= 51 && age <= 70) group = '51-70 años'
        else if (age > 70) group = '70+ años'
        
        acc[group] = (acc[group] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      // Estadísticas por subregión
      const bySubregion = patients.reduce((acc, patient) => {
        const subregion = patient.location?.subregion || 'No especificado'
        acc[subregion] = (acc[subregion] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      // Crear hojas de estadísticas
      const workbook = XLSX.utils.book_new()

      // Hoja de resumen
      const summaryData = [
        { Métrica: 'Total de Pacientes', Valor: patients.length },
        { Métrica: 'Pacientes con Dirección', Valor: patients.filter(p => p.location?.address).length },
        { Métrica: 'Pacientes con Observaciones', Valor: patients.filter(p => p.observations).length }
      ]
      const summarySheet = XLSX.utils.json_to_sheet(summaryData)
      XLSX.utils.book_append_sheet(workbook, summarySheet, 'Resumen')

      // Hoja por entidad
      const entityData = Object.entries(byEntity).map(([entity, count]) => ({
        Entidad: entity,
        'Cantidad de Pacientes': count,
        'Porcentaje': `${((count / patients.length) * 100).toFixed(1)}%`
      }))
      const entitySheet = XLSX.utils.json_to_sheet(entityData)
      XLSX.utils.book_append_sheet(workbook, entitySheet, 'Por Entidad')

      // Hoja por género
      const genderData = Object.entries(byGender).map(([gender, count]) => ({
        Género: gender,
        'Cantidad de Pacientes': count,
        'Porcentaje': `${((count / patients.length) * 100).toFixed(1)}%`
      }))
      const genderSheet = XLSX.utils.json_to_sheet(genderData)
      XLSX.utils.book_append_sheet(workbook, genderSheet, 'Por Género')

      // Hoja por tipo de atención
      const careData = Object.entries(byCareType).map(([type, count]) => ({
        'Tipo de Atención': type,
        'Cantidad de Pacientes': count,
        'Porcentaje': `${((count / patients.length) * 100).toFixed(1)}%`
      }))
      const careSheet = XLSX.utils.json_to_sheet(careData)
      XLSX.utils.book_append_sheet(workbook, careSheet, 'Por Tipo Atención')

      // Hoja por grupo de edad
      const ageData = Object.entries(byAgeGroup).map(([group, count]) => ({
        'Grupo de Edad': group,
        'Cantidad de Pacientes': count,
        'Porcentaje': `${((count / patients.length) * 100).toFixed(1)}%`
      }))
      const ageSheet = XLSX.utils.json_to_sheet(ageData)
      XLSX.utils.book_append_sheet(workbook, ageSheet, 'Por Edad')

      // Hoja por subregión
      const subregionData = Object.entries(bySubregion).map(([subregion, count]) => ({
        'Subregión': subregion,
        'Cantidad de Pacientes': count,
        'Porcentaje': `${((count / patients.length) * 100).toFixed(1)}%`
      }))
      const subregionSheet = XLSX.utils.json_to_sheet(subregionData)
      XLSX.utils.book_append_sheet(workbook, subregionSheet, 'Por Subregión')

      const filename = `estadisticas_pacientes_${new Date().toISOString().split('T')[0]}.xlsx`
      XLSX.writeFile(workbook, filename)

      return {
        success: true,
        filename,
        recordCount: patients.length
      }
    } catch (error) {
      console.error('Error al generar estadísticas:', error)
      throw new Error('Error al generar el archivo de estadísticas')
    } finally {
      isExporting.value = false
    }
  }

  return {
    isExporting,
    exportPatientsToExcel,
    exportSelectedPatients,
    exportPatientStats
  }
}
