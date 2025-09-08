import type { Case } from '../types/case.types'
import JSZip from 'jszip'
import html2pdf from 'html2pdf.js'
import { useMultiplePDFPreview } from './useMultiplePDFPreview'

export function useBatchDownload() {
  
  // Usar el composable específico para vista previa múltiple
  const multiplePDFPreview = useMultiplePDFPreview()
  
  // Función para generar PDF de un caso individual
  async function generateCasePDF(c: Case): Promise<Blob> {
    return new Promise((resolve, reject) => {
      try {
        // Crear el HTML del informe basado en la estructura de PreviewReportView
        const html = generateCaseHTML(c)
        
        // Crear un elemento temporal para generar el PDF
        const tempDiv = document.createElement('div')
        tempDiv.innerHTML = html
        tempDiv.style.position = 'absolute'
        tempDiv.style.left = '-9999px'
        tempDiv.style.top = '-9999px'
        document.body.appendChild(tempDiv)
        
        const options = {
          margin: [10, 10, 10, 10],
          filename: `caso_${c.caseCode || c.id}.pdf`,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true },
          jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        }
        
        html2pdf()
          .from(tempDiv)
          .set(options)
          .toPdf()
          .get('pdf')
          .then((pdf: any) => {
            const pdfBlob = pdf.output('blob')
            document.body.removeChild(tempDiv)
            resolve(pdfBlob)
          })
          .catch((error: any) => {
            document.body.removeChild(tempDiv)
            reject(error)
          })
      } catch (error) {
        reject(error)
      }
    })
  }
  
  // Función para generar HTML del informe de un caso
  function generateCaseHTML(c: Case): string {
    const currentDate = new Date().toLocaleDateString('es-CO')
    const receivedDate = c.receivedAt ? new Date(c.receivedAt).toLocaleDateString('es-CO') : 'N/A'
    
    return `
      <!DOCTYPE html>
      <html lang="es">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Informe Caso ${c.caseCode || c.id}</title>
        <style>
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          
          body {
            font-family: Arial, sans-serif;
            background: white;
            color: #333;
            line-height: 1.4;
            padding: 20mm;
            font-size: 12px;
          }
          
          .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #333;
          }
          
          .logo {
            height: 40px;
            max-width: 150px;
            object-fit: contain;
          }
          
          .title-section {
            flex: 1;
            text-align: center;
          }
          
          .title {
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
          }
          
          .subtitle {
            font-size: 14px;
            font-weight: 600;
            color: #666;
          }
          
          .date {
            font-size: 10px;
            color: #666;
            white-space: nowrap;
          }
          
          .info-section {
            margin-bottom: 20px;
          }
          
          .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
          }
          
          .info-item {
            border: 1px solid #ddd;
            padding: 8px;
            background-color: #f9f9f9;
          }
          
          .info-label {
            font-weight: bold;
            color: #555;
            font-size: 10px;
            text-transform: uppercase;
          }
          
          .info-value {
            font-size: 11px;
            margin-top: 3px;
          }
          
          .tests-section {
            margin-bottom: 20px;
          }
          
          .test-item {
            background-color: #f0f0f0;
            padding: 5px 8px;
            margin: 2px 0;
            border-radius: 3px;
            font-size: 10px;
            font-family: monospace;
          }
          
          .status-section {
            margin-bottom: 20px;
          }
          
          .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 10px;
            font-weight: bold;
            text-transform: uppercase;
          }
          
          .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 9px;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 10px;
          }
          
          @media print {
            body { padding: 0; }
            @page { margin: 15mm; }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <img src="/images/logo/Baner-udea.png" alt="Logo Universidad de Antioquia" class="logo" />
          <div class="title-section">
            <div class="title">INFORME DE CASO PATOLÓGICO</div>
            <div class="subtitle">Hospital Universitario Alma Mater de Antioquia</div>
          </div>
          <div class="date">${currentDate}</div>
        </div>
        
        <div class="info-section">
          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">Código del Caso</div>
              <div class="info-value">${c.caseCode || c.id}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Fecha de Recepción</div>
              <div class="info-value">${receivedDate}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Paciente</div>
              <div class="info-value">${c.patient?.fullName || 'N/A'}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Cédula</div>
              <div class="info-value">${c.patient?.dni || 'N/A'}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Entidad</div>
              <div class="info-value">${c.entity || 'N/A'}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Patólogo</div>
              <div class="info-value">${c.pathologist || 'No asignado'}</div>
            </div>
          </div>
        </div>
        
        <div class="tests-section">
          <div class="info-label" style="margin-bottom: 8px;">PRUEBAS SOLICITADAS</div>
          ${c.tests?.map(test => `<div class="test-item">${test}</div>`).join('') || '<div class="test-item">No hay pruebas registradas</div>'}
        </div>
        
        <div class="status-section">
          <div class="info-label" style="margin-bottom: 8px;">ESTADO ACTUAL</div>
          <div class="status-badge" style="background-color: ${getStatusColor(c.status)}; color: white;">
            ${c.status || 'N/A'}
          </div>
        </div>
        
        <div class="footer">
          <div>Informe generado automáticamente por el sistema</div>
          <div>Fecha de generación: ${new Date().toLocaleString('es-CO')}</div>
        </div>
      </body>
      </html>
    `
  }
  
  // Función para obtener color del estado
  function getStatusColor(status: string): string {
    switch (status) {
      case 'Completado': return '#10b981'
      case 'Por firmar': return '#f59e0b'
      case 'En proceso': return '#3b82f6'
      case 'Por entregar': return '#dc2626'
      default: return '#6b7280'
    }
  }
  
  // Función para descargar múltiples PDFs en un archivo ZIP
  async function downloadMultiplePDFs(
    cases: Case[], 
    onProgress?: (current: number, total: number) => void,
    onCancelled?: () => boolean
  ): Promise<void> {
    try {
      const zip = new JSZip()
      const pdfsFolder = zip.folder('informes_pdf')
      
      // Generar PDFs uno por uno para evitar sobrecarga
      for (let i = 0; i < cases.length; i++) {
        // Verificar si fue cancelado
        if (onCancelled && onCancelled()) {
          return
        }
        
        const c = cases[i]
        try {
          const pdfBlob = await generateCasePDF(c)
          const fileName = `caso_${c.caseCode || c.id}.pdf`
          pdfsFolder?.file(fileName, pdfBlob)
          
          // Actualizar progreso
          const current = i + 1
          const total = cases.length
          
          // Reportar progreso si se proporciona callback
          if (onProgress) {
            onProgress(current, total)
          }
          
        } catch (error) {
          // Continuar con el siguiente caso
        }
      }
      
      // Verificar cancelación antes de generar ZIP
      if (onCancelled && onCancelled()) {
        return
      }
      
      // Generar y descargar el ZIP
      const zipBlob = await zip.generateAsync({ type: 'blob' })
      const url = URL.createObjectURL(zipBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `informes_casos_${new Date().toISOString().split('T')[0]}.zip`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      throw error
    }
  }
  
  // Función para exportar casos a Excel (seleccionados o filtrados)
  async function exportCasesToExcel(cases: Case[], exportType: 'selected' | 'filtered' = 'selected'): Promise<void> {
    try {
      // Usar exactamente las mismas columnas que useExcelExport del FiltersBar
      const data = cases.map(c => ({
        'ID Caso': c.id,
        'Tipo de Muestra': c.sampleType,
        'Paciente': c.patient?.fullName || 'N/A',
        'Cédula': c.patient?.dni || 'N/A',
        'Entidad': c.entity || 'N/A',
        'Médico': c.requester || 'N/A',
        'Estado': c.status || 'N/A',
        'Fecha Recepción': c.receivedAt || 'N/A',
  'Fecha Firma': c.deliveredAt || '',
        'Pruebas': c.tests?.join(', ') || 'N/A'
      }))
      
      const XLSX = await import('xlsx')
      const ws = XLSX.utils.json_to_sheet(data)
      const wb = XLSX.utils.book_new()
      
      // Nombre de la hoja según el tipo de exportación
      const sheetName = exportType === 'selected' ? 'Casos Seleccionados' : 'Casos Filtrados'
      XLSX.utils.book_append_sheet(wb, ws, sheetName)
      
      // Generar nombre de archivo con fecha y tipo
      const typeLabel = exportType === 'selected' ? 'seleccionados' : 'filtrados'
      const fileName = `casos_${typeLabel}_${new Date().toISOString().split('T')[0]}.xlsx`
      XLSX.writeFile(wb, fileName)
    } catch (error) {
      throw error
    }
  }
  
  // Función para previsualizar múltiples casos usando el nuevo componente
  function previewMultipleCases(cases: Case[]): void {
    try {
      if (cases.length === 0) return
      
      // Usar el nuevo composable para vista previa múltiple
      multiplePDFPreview.previewMultipleCases(cases)
      
    } catch (error) {
      console.error('Error en previsualización múltiple:', error)
      throw error
    }
  }
  
  return {
    generateCasePDF,
    downloadMultiplePDFs,
    exportCasesToExcel,
    previewMultipleCases
  }
}
