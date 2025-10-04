// Servicio base para Special Cases
export const specialCasesService = {
  async list() {
    return [] as any[]
  },
  async detail(id: string) {
    return { id } as any
  },
}


