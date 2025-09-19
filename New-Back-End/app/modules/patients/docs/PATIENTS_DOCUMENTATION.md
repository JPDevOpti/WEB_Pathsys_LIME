# Patients Module Documentation

## Module Architecture

### Module Structure
The patients module follows a layered architecture that separates responsibilities:

```
patients/
├── models/          # Pydantic models for MongoDB
├── schemas/         # API input/output schemas
├── repositories/    # Data access layer
├── services/        # Business logic
└── routes/          # API endpoints
```

### Module Dependencies
- **Cases Module**: For case management
- **Auth Module**: For authentication and authorization
- **Shared**: Common schemas and utilities
- **Core**: System exceptions and dependencies

### Design Pattern
- **Repository Pattern**: Abstracts data access
- **Service Layer**: Contains business logic
- **DTO Pattern**: Separation between data models and API schemas

## Server Configuration

### Server Information
- **Base URL**: `http://localhost:8000`
- **API Version**: `/api/v1`
- **Base Endpoint for Patients**: `http://localhost:8000/api/v1/patients`
- **Default Port**: 8000

### Start Server
```bash
cd New-Back-End
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Model Structure

### Patient Model Fields
```json
{
    "id": "string (MongoDB auto-generated ID)",
    "patient_code": "string (unique patient code, 6-12 digits)",
    "name": "string (2-200 characters)",
    "age": "integer (0-150)",
    "gender": "string (Male, Female)",
    "entity_info": {
        "id": "string (unique entity ID)",
        "name": "string (health entity name)"
    },
    "care_type": "string (Outpatient, Inpatient)",
    "observations": "string (optional, max 500 characters)",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Required Fields for Creation
- `patient_code`: Unique patient code (6-12 digits)
- `name`: Full patient name
- `age`: Patient age (0-150 years)
- `gender`: Patient gender
- `entity_info`: Health entity information
- `care_type`: Medical care type

### Optional Fields
- `observations`: Additional patient observations

## API Endpoints

### 1. POST http://localhost:8000/api/v1/patients/
**Create new patient**

**Authentication**: Required  
**Allowed Roles**: admin, auxiliary

#### Example: Create basic patient
```json
{
  "patient_code": "12345678",
  "name": "John Carlos Perez",
  "age": 35,
  "gender": "Masculino",
  "entity_info": {
    "id": "ent_001",
    "name": "EPS Sanitas"
  },
  "care_type": "Ambulatorio",
  "observations": "Patient with hypertension history"
}
```

#### Example: Create minimal patient
```json
{
  "patient_code": "87654321",
  "name": "Maria Gonzalez",
  "age": 28,
  "gender": "Femenino",
  "entity_info": {
    "id": "ent_002",
    "name": "Sura"
  },
  "care_type": "Hospitalizado"
}
```

Response (201):
```json
{
  "id": "64f8a1b2c3d4e5f6a7b8c9d0",
  "patient_code": "12345678",
  "name": "John Carlos Perez",
  "age": 35,
  "gender": "Masculino",
  "entity_info": {
    "id": "ent_001",
    "name": "EPS Sanitas"
  },
  "care_type": "Ambulatorio",
  "observations": "Patient with hypertension history",
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

### 2. GET http://localhost:8000/api/v1/patients/
**List patients with filters**

**Authentication**: Required  
**Allowed Roles**: admin, pathologist, auxiliary

URL with parameters:
- `http://localhost:8000/api/v1/patients/` (all patients)
- `http://localhost:8000/api/v1/patients/?skip=0&limit=10` (pagination)
- `http://localhost:8000/api/v1/patients/?gender=Masculino&limit=20` (only males)
- `http://localhost:8000/api/v1/patients/?entity=Sanitas` (by entity)

Query parameters:
- `skip`: Records to skip (default: 0)
- `limit`: Maximum records (default: 100, max: 1000)
- `search`: Search by name or code
- `entity`: Filter by entity name
- `gender`: Filter by gender (Masculino, Femenino)
- `care_type`: Filter by type (Ambulatorio, Hospitalizado)

Response (200):
```json
[
  {
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "patient_code": "12345678",
    "name": "John Carlos Perez",
    "age": 35,
    "gender": "Masculino",
    "entity_info": {
      "id": "ent_001",
      "name": "EPS Sanitas"
    },
    "care_type": "Ambulatorio",
    "observations": "Patient with hypertension history",
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
]
```

### 3. GET http://localhost:8000/api/v1/patients/search/advanced
**Advanced patient search**

**Authentication**: Required  
**Allowed Roles**: admin, pathologist, auxiliary

**Query Parameters**:
- `name`: Search by patient name
- `patient_code`: Search by patient code
- `age_min`: Minimum age (0-150)
- `age_max`: Maximum age (0-150)
- `entity`: Filter by health entity
- `gender`: Filter by gender (Masculino, Femenino)
- `care_type`: Filter by care type
- `date_from`: Creation date from (format: YYYY-MM-DD)
- `date_to`: Creation date to (format: YYYY-MM-DD)
- `skip`: Records to skip for pagination
- `limit`: Result limit (1-1000)

**Usage examples**:
```bash
# Search male patients between 30 and 50 years old
GET /api/v1/patients/search/advanced?gender=Masculino&age_min=30&age_max=50

# Search patients from a specific entity
GET /api/v1/patients/search/advanced?entity=Sanitas&limit=50

# Search patients created in a date range
GET /api/v1/patients/search/advanced?date_from=2024-01-01&date_to=2024-01-31
```

Response (200):
```json
{
  "patients": [
    {
      "id": "64f8a1b2c3d4e5f6a7b8c9d0",
      "patient_code": "12345678",
      "name": "John Carlos Perez",
      "age": 35,
      "gender": "Masculino",
      "entity_info": {
        "id": "ent_001",
        "name": "EPS Sanitas"
      },
      "care_type": "Ambulatorio",
      "observations": "Patient with hypertension history",
      "created_at": "2024-01-15T10:30:00.000Z",
      "updated_at": "2024-01-15T10:30:00.000Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 5
}
```

### 4. GET http://localhost:8000/api/v1/patients/{patient_code}
**Get patient by code**

**Authentication**: Required  
**Allowed Roles**: admin, pathologist, auxiliary

URL examples:
- `http://localhost:8000/api/v1/patients/12345678`
- `http://localhost:8000/api/v1/patients/87654321`

Response (200): (complete patient as in creation response)

### 5. PUT http://localhost:8000/api/v1/patients/{patient_code}
**Update patient**

**Authentication**: Required  
**Allowed Roles**: admin, auxiliary

URL examples:
- `http://localhost:8000/api/v1/patients/12345678`
- `http://localhost:8000/api/v1/patients/87654321`

#### Example: Partial update
```json
{
  "age": 36,
  "observations": "Patient with controlled hypertension"
}
```

#### Example: Complete update
```json
{
  "name": "John Carlos Perez Rodriguez",
  "age": 36,
  "gender": "Masculino",
  "entity_info": {
    "id": "ent_003",
    "name": "Nueva EPS"
  },
  "care_type": "Hospitalizado",
  "observations": "Patient with controlled hypertension and type 2 diabetes"
}
```

Response (200):
```json
{
  "id": "64f8a1b2c3d4e5f6a7b8c9d0",
  "patient_code": "12345678",
  "name": "John Carlos Perez Rodriguez",
  "age": 36,
  "gender": "Masculino",
  "entity_info": {
    "id": "ent_003",
    "name": "Nueva EPS"
  },
  "care_type": "Hospitalizado",
  "observations": "Patient with controlled hypertension and type 2 diabetes",
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T11:15:00.000Z"
}
```

### 6. PUT http://localhost:8000/api/v1/patients/{patient_code}/change-code
**Change patient code**

**Authentication**: Required  
**Allowed Roles**: admin, auxiliary

URL examples:
- `http://localhost:8000/api/v1/patients/12345678/change-code?new_code=87654321`
- `http://localhost:8000/api/v1/patients/87654321/change-code?new_code=11223344`

Response (200): (updated patient with new code)

### 7. DELETE http://localhost:8000/api/v1/patients/{patient_code}
**Delete patient**

**Authentication**: Required  
**Allowed Roles**: admin

URL examples:
- `http://localhost:8000/api/v1/patients/12345678`
- `http://localhost:8000/api/v1/patients/87654321`

Response (200):
```json
{
  "message": "Patient 12345678 deleted successfully"
}
```

⚠️ **IMPORTANT**: Cannot delete a patient that has associated cases. First delete or reassign the cases.

### 8. GET http://localhost:8000/api/v1/patients/count
**Get total patients count**

**Authentication**: Required  
**Allowed Roles**: admin, pathologist, auxiliary

Response (200):
```json
{
  "total": 150
}
```

 

## Enumeration Values

#### Patient Gender
- `Masculino` - Male patient
- `Femenino` - Female patient

⚠️ **IMPORTANT**: Values must be sent exactly as shown (with initial capital).

#### Care Type
- `Ambulatorio` - Outpatient care
- `Hospitalizado` - Inpatient care

⚠️ **IMPORTANT**: Values must be sent exactly as shown (with initial capital).

## Validation Rules

#### Required Fields
- **patient_code**: Required, 6-12 digits, unique in system
- **name**: Required, 2-200 characters
- **age**: Required, 0-150 years
- **gender**: Required, "Masculino" or "Femenino"
- **entity_info**: Required (complete object)
- **care_type**: Required, "Ambulatorio" or "Hospitalizado"

#### Specific Validations
1. **patient_code**: Automatically cleaned (numbers only), must be unique, 6-12 digits
2. **name**: Automatically capitalized, letters, spaces and accents only
3. **age**: Integer between 0 and 150
4. **gender**: Valid values: "Masculino", "Femenino"
5. **care_type**: Valid values: "Ambulatorio", "Hospitalizado"
6. **entity_info.id**: Required when entity_info is provided
7. **entity_info.name**: Required when entity_info is provided
8. **observations**: Optional, maximum 500 characters

## Common Error Cases

### 1. Duplicate Code (400 Bad Request)
```json
{
  "detail": "Patient with code 12345678 already exists"
}
```

### 2. Invalid Data (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error.number.not_ge",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

### 3. Missing Required Fields (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 4. Patient Not Found (404 Not Found)
```json
{
  "detail": "Patient with code 99999999 not found"
}
```

### 5. Patient with Cases Cannot Be Deleted (400 Bad Request)
```json
{
  "detail": "Cannot delete a patient that has associated cases. First delete or reassign the cases."
}
```

### 6. Invalid Date Format in Advanced Search (400 Bad Request)
```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

### 7. Invalid Date Range (400 Bad Request)
```json
{
  "detail": "Start date cannot be after end date"
}
```

## Interactive Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces provide interactive documentation and allow testing endpoints directly from the browser.

## Important Notes

1. **Code Validation**: The `patient_code` is used as the main patient identifier and must be unique in the system
2. **Automatic Capitalization**: Names are automatically capitalized
3. **Data Cleaning**: Patient code is automatically cleaned by removing non-numeric characters
4. **Optional Fields**: Only "observations" is optional in creation
5. **Consistent Responses**: All responses include timestamps
6. **Advanced Search**: Specialized endpoint with multiple filters and complete pagination
7. **Flexible Filters**: Listing endpoints support multiple combinable filters
8. **Date Validation**: Search dates must use ISO format (YYYY-MM-DD)
9. **Pagination**: All listing endpoints support pagination with skip/limit
10. **Entities**: Health entity management system separate from patient model
11. **Entity Filters**: Entity filters search in the `entity_info.name` field

## Troubleshooting

### If server doesn't start:
1. Verify MongoDB is running
2. Verify environment variables in `.env`
3. Verify port 8000 is not in use

### If there are connection errors:
1. Verify MongoDB URL in configuration
2. Verify "lime_pathsys" database exists
3. Verify MongoDB connection permissions
