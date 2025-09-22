# Diseases Module Documentation

## Model Structure

The diseases module manages disease information and medical classification codes (CIE10, etc.) with the following structure:

### Main Fields:
- **table**: Reference table (e.g., "CIE10")
- **code**: Unique disease code (e.g., "A000")
- **name**: Complete disease name
- **description**: General description or category of the disease
- **is_active**: Active state of the disease
- **created_at**: Creation date
- **updated_at**: Last update date

## Available Endpoints

### 1. Create Disease
**POST** `/diseases/`

**Example usage:**
```bash
curl -X POST "http://localhost:8000/diseases/" \
  -H "Content-Type: application/json" \
  -d '{
    "table": "CIE10",
    "code": "A000",
    "name": "COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
    "description": "COLERA",
    "is_active": true
  }'
```

### 2. Get Disease by Code
**GET** `/diseases/code/{code}`

**Example usage:**
```bash
curl -X GET "http://localhost:8000/diseases/code/A000"
```

### 3. Get All Diseases
**GET** `/diseases/`

**Query Parameters:**
- `skip`: Number of elements to skip (default: 0)
- `limit`: Maximum number of elements to return (default: 100, max: 15000)
- `is_active`: Filter by active state (optional)

**Example usage:**
```bash
curl -X GET "http://localhost:8000/diseases/?skip=0&limit=50&is_active=true"
```

### 4. Search Diseases by Name
**GET** `/diseases/search/name`

**Query Parameters:**
- `q`: Search term by name (required)
- `skip`: Number of elements to skip (default: 0)
- `limit`: Maximum number of elements to return (default: 100, max: 15000)

**Example usage:**
```bash
curl -X GET "http://localhost:8000/diseases/search/name?q=COLERA&skip=0&limit=20"
```

### 5. Search Diseases by Code
**GET** `/diseases/search/code`

**Query Parameters:**
- `q`: Search term by code (required)
- `skip`: Number of elements to skip (default: 0)
- `limit`: Maximum number of elements to return (default: 100, max: 15000)

**Example usage:**
```bash
curl -X GET "http://localhost:8000/diseases/search/code?q=A00&skip=0&limit=20"
```

### 6. Get Diseases by Table
**GET** `/diseases/table/{table}`

**Query Parameters:**
- `skip`: Number of elements to skip (default: 0)
- `limit`: Maximum number of elements to return (default: 100, max: 15000)

**Example usage:**
```bash
curl -X GET "http://localhost:8000/diseases/table/CIE10?skip=0&limit=50"
```

### 7. Delete Disease
**DELETE** `/diseases/{disease_id}`

**Example usage:**
```bash
curl -X DELETE "http://localhost:8000/diseases/507f1f77bcf86cd799439011"
```

## Use Cases

### 1. Mass Import of Diseases from Excel
The module includes an import script that allows loading diseases from Excel files with columns:
- Table
- Code
- Name
- Description

**Example usage of the script:**
```bash
# Dry-run mode (preview only)
python Back-End/scripts/import_diseases.py --dry-run

# Real import
python Back-End/scripts/import_diseases.py

# Specify file directly
python Back-End/scripts/import_diseases.py --file "path/to/file.xlsx"
```

### 2. Disease Search for Diagnoses
Search endpoints allow finding diseases quickly by name or code, facilitating diagnosis selection in the system.

### 3. CIE10 Code Management
The module is designed to handle international disease classification codes, allowing:
- Organization by reference table
- Search by specific code
- Unique code validation

### 4. Disease Catalog Maintenance
Allows complete management of the disease catalog with:
- Record creation and updates
- Permanent deletion when necessary
- Version control with timestamps

## Technical Features

- ✅ **Fields in English** but content in Spanish
- ✅ **Compatibility** with current module
- ✅ **Unique code validation**
- ✅ **Search** by name and code with regex
- ✅ **Pagination** in all lists
- ✅ **Hard delete** by default
- ✅ **Robust error handling**
- ✅ **Complete logging**

## Response Examples

### Create Disease Response
```json
{
  "id": "507f1f77bcf86cd799439011",
  "table": "CIE10",
  "code": "A000",
  "name": "COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
  "description": "COLERA",
  "is_active": true,
  "created_at": "2025-01-20T10:30:00Z",
  "updated_at": "2025-01-20T10:30:00Z"
}
```

### Disease List Response
```json
{
  "diseases": [
    {
      "id": "507f1f77bcf86cd799439011",
      "table": "CIE10",
      "code": "A000",
      "name": "COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
      "description": "COLERA",
      "is_active": true,
      "created_at": "2025-01-20T10:30:00Z",
      "updated_at": "2025-01-20T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### Search Response
```json
{
  "diseases": [
    {
      "id": "507f1f77bcf86cd799439011",
      "table": "CIE10",
      "code": "A000",
      "name": "COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
      "description": "COLERA",
      "is_active": true,
      "created_at": "2025-01-20T10:30:00Z",
      "updated_at": "2025-01-20T10:30:00Z"
    }
  ],
  "search_term": "COLERA",
  "skip": 0,
  "limit": 100
}
```
