export const AVAILABLE_METHODS = [
  { value: 'hematoxilina-eosina', label: 'Hematoxilina-Eosina' },
  { value: 'inmunohistoquimica-polimero-peroxidasa', label: 'Inmunohistoquimica: Polímero-Peroxidasa' },
  { value: 'coloraciones-especiales', label: 'Coloraciones especiales' },
  { value: 'inmunofluorescencia-metodo-directo', label: 'Inmunoflurescencia: método directo' }
]

export function normalizeMethod(input: string | undefined | null): string {
  if (!input || typeof input !== 'string') return ''
  const norm = (s: string) => s.trim().toLowerCase()
  const i = norm(input)
  const foundByValue = AVAILABLE_METHODS.find(m => norm(m.value) === i)
  if (foundByValue) return foundByValue.value
  const foundByLabel = AVAILABLE_METHODS.find(m => norm(m.label) === i)
  if (foundByLabel) return foundByLabel.value
  return input
}
