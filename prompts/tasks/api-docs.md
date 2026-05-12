# Task: Generate API Documentation

Generates endpoint-level API documentation.
Requires scan result. Best results when all route files are in context.

## Input
- Scan result
- Route/handler files (all)
- Auth middleware files
- Request/response model/schema files

## Per-Endpoint Format

### `METHOD /path/to/endpoint`

**Description:** What this endpoint does.
**Auth:** Required / None / Optional

**Request**
| Field | Location | Type | Required | Description |
|---|---|---|---|---|

**Request Example**
```http
POST /api/users
Authorization: Bearer <token>
```

**Response**
| Status | Meaning |
|---|---|
| 200 | Success |
| 401 | Unauthorized |

**Response Example**
```json
{ "id": "uuid" }
```

## Rules
- Document every endpoint, do not skip any
- Group by resource/router
- Include a summary table at the top: method, path, auth, one-line description

## Output
<!-- output: docs/api.md -->
