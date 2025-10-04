export interface CaseApprovalItem {
  id: string
  caseCode: string
  entity: string
  patient: string
  test: string
  status: 'pending' | 'approved' | 'rejected'
}






