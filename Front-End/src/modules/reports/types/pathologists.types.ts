export interface PathologistMetrics {
  name: string
  withinOpportunity: number
  outOfOpportunity: number
  avgTime: number
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
