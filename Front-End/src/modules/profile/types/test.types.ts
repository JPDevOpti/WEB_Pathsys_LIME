
export interface TestFormModel {
  testCode: string
  testName: string
  testDescription: string
  timeDays: number 
  price: number
  isActive: boolean
}

export interface TestCreateRequest {
  test_code: string
  name: string
  description: string
  time: number 
  price: number 
  is_active: boolean
}
export interface TestCreateResponse {
  _id: string
  test_code: string
  name: string
  description: string
  time: number 
  price: number
  is_active: boolean
  created_at: string
  updated_at?: string
}
export interface TestCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

export interface TestFormValidation {
  isValid: boolean
  errors: {
    testCode?: string
    testName?: string
    testDescription?: string
    timeDays?: string
    price?: string
  }
}

export interface TestEditFormModel {
  id: string
  testCode: string
  testName: string
  testDescription: string
  timeDays: number 
  price: number 
  isActive: boolean
}

export interface TestUpdateRequest {
  test_code?: string
  name?: string
  description?: string
  time?: number 
  price?: number 
  is_active?: boolean
}

export interface TestUpdateResponse {
  _id: string
  test_code: string
  name: string
  description: string
  time: number 
  price: number 
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TestEditionState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

export interface TestEditFormValidation {
  isValid: boolean
  errors: {
    testCode?: string
    testName?: string
    testDescription?: string
    timeDays?: string
    price?: string
  }
}
