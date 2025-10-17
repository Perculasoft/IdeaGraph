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
    "BaseUrl": "http://localhost:8000/",
    "X-Api-Key": "your-api-key"
  },
  "KiGateApi": {
    "KiGateApiUrl": "https://your-kigate-api-url",
    "KiGateBearerToken": "your-bearer-token"
  }
}
```

**Note:** The KiGate API configuration is optional. If not configured, KiGate endpoints will return 503 Service Unavailable.

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

### KiGate API Integration

The KiGate API provides AI-powered features through a centralized agent-driven API Gateway. All endpoints are proxied through `/api/kigate` and require configuration in appsettings.json.

| ASP.NET Core API | KiGate Endpoint | Method | Description |
|-----------------|------------------|--------|-------------|
| `/api/kigate/health` | `/health` | GET | Check KiGate API health |
| `/api/kigate/agents` | `/api/agents` | GET | Get all available agents |
| `/api/kigate/agent/execute` | `/agent/execute` | POST | Execute an agent with a message |
| `/api/kigate/openai` | `/api/openai` | POST | Call OpenAI API |
| `/api/kigate/gemini` | `/api/gemini` | POST | Call Google Gemini API |
| `/api/kigate/claude` | `/api/claude` | POST | Call Claude API |
| `/api/kigate/github/create-issue` | `/api/github/create-issue` | POST | Create a GitHub issue with AI improvement |

**Health Check Response:**
```json
{
  "status": "ok",
  "message": "KiGate API is running"
}
```

**Get Agents Response:**
```json
[
  {
    "name": "agent-name",
    "description": "Agent description",
    "provider": "openai",
    "model": "gpt-4"
  }
]
```

**Execute Agent Request:**
```json
{
  "agent_name": "agent-name",
  "message": "User message to the agent",
  "provider": "openai",
  "model": "gpt-4",
  "user_id": "optional-user-id",
  "parameters": {
    "key": "value"
  }
}
```

**Execute Agent Response:**
```json
{
  "job_id": "job-uuid",
  "result": {
    "content": "AI response content",
    "model": "gpt-4",
    "usage": {
      "prompt_tokens": 100,
      "completion_tokens": 50,
      "total_tokens": 150
    }
  },
  "error": null
}
```

**AI API Request (OpenAI/Gemini/Claude):**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Your prompt here"
    }
  ],
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**AI API Response:**
```json
{
  "content": "AI generated response",
  "model": "gpt-4",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

**Create GitHub Issue Request:**
```json
{
  "repository": "owner/repo",
  "text": "Issue description",
  "user_id": "optional-user-id"
}
```

**Create GitHub Issue Response:**
```json
{
  "issue_number": 123,
  "title": "AI-generated issue title",
  "url": "https://github.com/owner/repo/issues/123",
  "error": null
}
```

**Configuration Note:** If KiGate API is not configured (missing KiGateApiUrl in appsettings), all KiGate endpoints will return:
```json
{
  "error": "KiGate API is not configured. Please set KiGateApiUrl in appsettings."
}
```
with HTTP status code 503 (Service Unavailable).

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

### KiGateController
- **Route**: `/api/kigate`
- **Purpose**: Proxy requests to KiGate API (non-admin endpoints only)
- **Authentication**: Uses Bearer token configured in appsettings
- **Endpoints**:
  - `GET /api/kigate/health` - Health check
  - `GET /api/kigate/agents` - Get all available agents
  - `POST /api/kigate/agent/execute` - Execute an agent
  - `POST /api/kigate/openai` - Call OpenAI API
  - `POST /api/kigate/gemini` - Call Google Gemini API
  - `POST /api/kigate/claude` - Call Claude API
  - `POST /api/kigate/github/create-issue` - Create GitHub issue
- **Configuration Check**: Returns 503 if KiGate API is not configured
- **Logging**: Logs all KiGate API requests and errors

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
