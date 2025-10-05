// API Constants
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500
} as const

export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  DELETE: 'DELETE',
  PATCH: 'PATCH'
} as const

// API Endpoints Base Paths
export const API_ENDPOINTS = {
  AUTH: '/auth',
  USERS: '/users',
  PATIENTS: '/patients',
  CASES: '/cases',
  ENTITIES: '/entities',
  PATHOLOGISTS: '/pathologists',
  TESTS: '/tests',
  REPORTS: '/reports',
  UPLOADS: '/uploads'
} as const

// Request Headers
export const HEADERS = {
  CONTENT_TYPE: 'Content-Type',
  AUTHORIZATION: 'Authorization',
  ACCEPT: 'Accept'
} as const

export const CONTENT_TYPES = {
  JSON: 'application/json',
  FORM_DATA: 'multipart/form-data',
  URL_ENCODED: 'application/x-www-form-urlencoded'
} as const

// Request Timeouts (in milliseconds)
export const TIMEOUTS = {
  DEFAULT: 10000, // 10 seconds
  UPLOAD: 30000,  // 30 seconds
  DOWNLOAD: 60000 // 60 seconds
} as const