# IdeaGraph API Controller Documentation

This document describes the ASP.NET Core API controllers that proxy requests to the FastAPI backend, providing better security by not exposing the FastAPI service directly.

## Architecture

The ASP.NET Core application now hosts API controllers that forward requests to the FastAPI backend service running on localhost:8000. This provides:

1. **Security**: FastAPI is not exposed to external access
2. **Centralized Access**: All requests go through the ASP.NET Core application
3. **1:1 Endpoint Mapping**: Each FastAPI endpoint has a corresponding ASP.NET Core controller endpoint

## Configuration

Configure the FastAPI backend URL in `appsettings.json`:

```json
{
  "FastAPI": {
    "BaseUrl": "http://localhost:8000/"
  }
}
```

## Endpoint Mapping

### Health Check

| ASP.NET Core API | FastAPI Endpoint | Method | Description |
|-----------------|------------------|--------|-------------|
| `/api/health` | `/health` | GET | Check service health and database collections |

**Response:**
```json
{
  "status": "ok",
  "collections": ["ideas", "relations"]
}
```

### Ideas Management

| ASP.NET Core API | FastAPI Endpoint | Method | Description |
|-----------------|------------------|--------|-------------|
| `/api/ideas` | `/ideas` | GET | List all ideas |
| `/api/ideas/{id}` | `/ideas/{id}` | GET | Get a specific idea with relations |
| `/api/idea` | `/idea` | POST | Create a new idea |
| `/api/ideas/{id}` | `/ideas/{id}` | PUT | Update an existing idea |
| `/api/ideas/{id}` | `/ideas/{id}` | DELETE | Delete an idea |

**List Ideas Response:**
```json
[
  {
    "id": "uuid",
    "title": "Idea Title",
    "description": "Description",
    "tags": ["tag1", "tag2"],
    "createdAt": "2025-01-01T00:00:00"
  }
]
```

**Get Idea Response:**
```json
{
  "id": "uuid",
  "title": "Idea Title",
  "description": "Description",
  "tags": ["tag1", "tag2"],
  "createdAt": "2025-01-01T00:00:00",
  "relations": [
    {
      "id": "relation-id",
      "sourceId": "source-uuid",
      "targetId": "target-uuid",
      "relationType": "depends_on",
      "weight": 1.0
    }
  ]
}
```

**Create Idea Request:**
```json
{
  "title": "New Idea",
  "description": "Detailed description",
  "tags": ["innovation", "tech"]
}
```

**Update Idea Request:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "tags": ["updated", "tags"]
}
```
Note: All fields are optional in update requests. Only provided fields will be updated.

**Delete Idea Response:**
```json
{
  "message": "Idea deleted successfully",
  "id": "uuid"
}
```

### Similarity Search

| ASP.NET Core API | FastAPI Endpoint | Method | Description |
|-----------------|------------------|--------|-------------|
| `/api/similar/{ideaId}?k=5` | `/similar/{ideaId}?k=5` | GET | Find similar ideas using embeddings |

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Similar Idea",
    "description": "Description",
    "tags": ["tag1"],
    "createdAt": "2025-01-01T00:00:00",
    "distance": 0.15
  }
]
```

### Relations Management

| ASP.NET Core API | FastAPI Endpoint | Method | Description |
|-----------------|------------------|--------|-------------|
| `/api/relations/{ideaId}` | `/relations/{ideaId}` | GET | Get all relations for an idea |
| `/api/relation` | `/relation` | POST | Create a new relation between ideas |

**Get Relations Response:**
```json
[
  {
    "id": "relation-id",
    "sourceId": "source-uuid",
    "targetId": "target-uuid",
    "relationType": "depends_on",
    "weight": 1.0
  }
]
```

**Create Relation Request:**
```json
{
  "sourceId": "source-uuid",
  "targetId": "target-uuid",
  "relationType": "depends_on",
  "weight": 1.0
}
```

**Relation Types:**
- `depends_on`: Source idea depends on target idea
- `extends`: Source idea extends target idea
- `contradicts`: Source idea contradicts target idea
- `synergizes_with`: Source idea synergizes with target idea

## Controllers

### HealthController
- **Route**: `/api/health`
- **Purpose**: Proxy health check requests to FastAPI
- **Logging**: Logs health check requests and responses

### IdeasController
- **Route**: `/api/ideas`
- **Purpose**: Manage ideas (list, get, create, update, delete)
- **Logging**: Logs all idea operations
- **Error Handling**: Returns 404 for not found, 500 for server errors

### SimilarController
- **Route**: `/api/similar`
- **Purpose**: Find similar ideas using vector embeddings
- **Logging**: Logs similarity search requests
- **Parameters**: `k` - number of similar ideas to return (default: 5)

### RelationsController
- **Route**: `/api/relations`
- **Purpose**: Manage relations between ideas
- **Logging**: Logs all relation operations
- **Error Handling**: Returns appropriate status codes with error details

## Security Considerations

1. **Internal FastAPI**: The FastAPI service should only be accessible from localhost
2. **ASP.NET Core Gateway**: All external requests go through ASP.NET Core
3. **HTTPS**: Production deployments should use HTTPS
4. **Authentication**: Can be added to controllers using ASP.NET Core authentication middleware
5. **Rate Limiting**: Can be added using ASP.NET Core rate limiting middleware
6. **API Keys**: Can be added using custom middleware or API key schemes

## Error Handling

All controllers implement consistent error handling:

- **404 Not Found**: When an idea or resource doesn't exist
- **500 Internal Server Error**: When FastAPI communication fails
- All errors include:
  - `error`: Error message
  - `detail`: Detailed error information (in development mode)

## Logging

All controllers use ILogger for:
- Request forwarding information
- Success/failure of operations
- Error details with exception information

## Future Enhancements

1. Add authentication and authorization
2. Implement caching for frequently accessed data
3. Add request validation middleware
4. Implement circuit breaker pattern for FastAPI calls
5. Add API versioning
6. Implement rate limiting
7. Add OpenAPI/Swagger documentation
