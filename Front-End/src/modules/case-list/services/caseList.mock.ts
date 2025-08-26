import type { Case } from '../types/case.types'

const mockCases: Case[] = [
  {
    id: 'MX-2025-0001',
    sampleType: 'Biopsia',
    patient: {
      id: 'P-001',
      dni: '123456789',
      fullName: 'Juan Pérez',
      sex: 'masculino',
      age: 45,
      entity: 'Entidad A',
      attentionType: 'ambulatorio',
      notes: 'Sin antecedentes relevantes'
    },
    entity: 'Entidad A',
    requester: 'Dr. Ramírez',
    status: 'En proceso',
    receivedAt: new Date().toISOString().split('T')[0],
    deliveredAt: '',
    tests: ['000101 - Prueba A', '000102 - Prueba B', '000101 - Prueba A'],
    pathologist: 'Dra. Gómez',
    notes: ''
  },
  {
    id: 'MX-2025-0002',
    sampleType: 'Citología',
    patient: {
      id: 'P-002',
      dni: '987654321',
      fullName: 'María López',
      sex: 'femenino',
      age: 37,
      entity: 'Entidad B',
      attentionType: 'hospitalizado'
    },
    entity: 'Entidad B',
    requester: 'Dra. Silva',
    status: 'Por firmar',
    receivedAt: new Date(Date.now() - 3 * 86400000).toISOString().split('T')[0],
    deliveredAt: '',
    tests: ['000201 - Prueba C'],
    pathologist: 'Dr. Ruiz'
  },
  {
    id: 'MX-2025-0003',
    sampleType: 'Biopsia',
    patient: {
      id: 'P-003',
      dni: '555666777',
      fullName: 'Carlos Sánchez',
      sex: 'masculino',
      age: 52,
      entity: 'Entidad A',
      attentionType: 'ambulatorio'
    },
    entity: 'Entidad A',
    requester: 'Dr. Ramírez',
    status: 'Completado',
    receivedAt: new Date(Date.now() - 9 * 86400000).toISOString().split('T')[0],
    deliveredAt: new Date(Date.now() - 2 * 86400000).toISOString().split('T')[0],
    tests: ['000101 - Prueba A'],
    pathologist: 'Dra. Gómez'
  },
]

export async function fetchMockCases(): Promise<Case[]> {
  // Simular latencia
  await new Promise((res) => setTimeout(res, 300))
  return mockCases
}


