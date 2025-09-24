export interface OpportunityTest {
  code: string
  name: string
  withinOpportunity: number
  outOfOpportunity: number
  opportunityTime: string // e.g., '7 días'
}

export interface OpportunityFilters {
  completionMin: number
  completionMax: number
  selectedTimes: string[]
  volumeMin: number | null
  volumeMax: number | null
  search: string
}

export interface PathologistPerformance {
  code: string
  name: string
  withinOpportunity: number
  outOfOpportunity: number
  avgTime: number
}

export interface PeriodSelection {
  monthIndex: number
  year: number
}


