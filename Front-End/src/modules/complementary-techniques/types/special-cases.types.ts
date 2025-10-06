// Types for Special Cases and Complementary Techniques (code keys in English, values may be in Spanish)

export interface SpecialCase {
  id: string
  title: string
  status: 'pending' | 'in_progress' | 'closed'
}

// Represents a complementary technique entry based on the provided Excel columns
export interface ComplementaryTechnique {
  id: string
  // FECHA
  date: string
  // ELABORÓ
  elaboratedBy: string
  // N° CASO
  caseNumber: string
  // DOCUMENTO PACIENTE
  patientDocument: string
  // NOMBRE DEL PACIENTE
  patientName: string
  // INSTITUCIÓN
  institution: string
  // NÚMERO DE PLACAS RECIBE
  receivedSlidesCount: number
  // RECIBE
  receivedBy: string
  // FECHA ENTREGA
  deliveryDate: string
  // ENTREGA
  deliveredBy: string
  // INMUNOHISTOQUIMICAS DE BAJA COMPLEJIDAD: ALK-1, TOXOPLASMA, CMV, TDT, SINAPTOFISINA, MAPS2, SOX10, etc.
  lowComplexityIHQ: string
  // # PLACAS (para baja complejidad)
  lowComplexitySlidesCount: number
  // INMUNOHISTOQUIMICAS DE ALTA COMPLEJIDAD EN DIFERENTE MUESTRA Y MÉDULA ÓSEA
  highComplexityIHQ: string
  // # PLACAS (para alta complejidad)
  highComplexitySlidesCount: number
  // INMUNOHISTOQUIMICAS ESPECIALES: ATRX, IDH1, MUC1, PD1, PD-L1, PERFORINA, PIT-1, TPIT, H3K
  specialIHQ: string
  // # PLACAS (para especiales)
  specialIHQSlidesCount: number
  // HISTOQUÍMICAS
  histochemical: string
  // # PLACAS (para histoquímicas)
  histochemicalSlidesCount: number
  // RECIBO (e.g., FACTURAR, PENDIENTE, ANULADO). Values in Spanish per workspace rule
  receiptStatus: 'FACTURAR' | 'PENDIENTE' | 'ANULADO' | string
  // OBSERVACIONES
  notes: string
}


