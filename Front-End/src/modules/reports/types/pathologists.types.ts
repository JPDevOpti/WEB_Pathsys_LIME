export interface PathologistMetrics {
  code: string
  name: string
  withinOpportunity: number
  outOfOpportunity: number
  averageDays: number
}

export interface PathologistsReportData {
  pathologists: PathologistMetrics[]
  summary?: {
    total: number
    within: number
    out: number
  }
}

export interface PeriodSelection {
  month: number
  year: number
}
