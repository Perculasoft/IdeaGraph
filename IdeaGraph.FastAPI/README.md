# IdeaGraph FastAPI

FastAPI backend for IdeaGraph - a semantic knowledge graph for ideas.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
# Required: Your OpenAI API key
OPENAI_API_KEY=your-openai-api-key-here

# Optional: OpenAI Organization ID
OPENAI_ORG_ID=your-org-id-here-optional

# Optional: Embedding model to use (default: text-embedding-3-small)
EMBEDDING_MODEL=text-embedding-3-small

# Required: ChromaDB Cloud API key
CHROMA_API_KEY=your-chroma-api-key-here

# Optional: ChromaDB Cloud tenant (if not provided, will be inferred from API key)
CHROMA_TENANT=your-tenant-name

# Optional: ChromaDB Cloud database (default: IdeaGraph)
CHROMA_DATABASE=IdeaGraph

# Optional: CORS allowed origins (comma-separated)
ALLOW_ORIGINS=http://localhost:3000,http://localhost:5173

# Optional: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) - default: INFO
LOG_LEVEL=INFO

# Optional: Microsoft Graph API credentials for mail endpoints
CLIENT_ID=your-azure-app-client-id
CLIENT_SECRET=your-azure-app-client-secret
TENANT_ID=your-azure-tenant-id
```

### 3. Run the Application

#### Option 1: Using uvicorn directly (recommended for development)

```bash
uvicorn api.main:app --reload
```

#### Option 2: Running the main.py file directly (works with Visual Studio)

```bash
python api/main.py
```

The API will be available at `http://localhost:8000`

#### Visual Studio Users

To start the server in Visual Studio:
1. Make sure you have created a `.env` file based on `.env.example` with your API keys
2. Press F5 or click the "Start" button in Visual Studio
3. The console window will show startup messages and any errors
4. If you see errors about missing API keys, check your `.env` file

## Testing Environment Configuration

To verify that your `.env` file is being loaded correctly:

```bash
python test_dotenv_loading.py
```

To validate your ChromaDB Cloud configuration:

```bash
python validate_chromadb_config.py
```

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /idea` - Create a new idea
- `GET /ideas` - List all ideas
- `GET /ideas/{idea_id}` - Get a specific idea
- `GET /similar/{idea_id}` - Find similar ideas
- `POST /relation` - Create a relation between ideas
- `GET /relations/{idea_id}` - Get relations for an idea

### Mail Endpoints (requires Graph API configuration)
- `POST /mail/send` - Send an email via Microsoft Graph API
- `GET /mail/receive` - Fetch emails from shared mailbox and create ideas

To enable mail endpoints, add the following to your `.env` file:
```env
CLIENT_ID=your-azure-app-client-id
CLIENT_SECRET=your-azure-app-client-secret
TENANT_ID=your-azure-tenant-id
```

**Note**: Mail endpoints require an Azure App Registration with the following Microsoft Graph API permissions:
- `Mail.Send` (for sending emails)
- `Mail.ReadWrite` (for reading and moving emails)
- `Mail.ReadWrite.Shared` (for accessing shared mailboxes)

## Features

- **Semantic Search**: Uses OpenAI embeddings for semantic similarity
- **Vector Database**: ChromaDB Cloud for efficient vector storage and retrieval (configured without local persistence to avoid permission issues in production)
- **Relation Tracking**: Track relationships between ideas (depends_on, extends, contradicts, synergizes_with)
- **CORS Support**: Configurable CORS for frontend integration
- **Comprehensive Logging**: Structured logging with configurable log levels for error tracking and debugging
- **Mail Integration**: Send emails and automatically create ideas from incoming emails via Microsoft Graph API

## Mail Endpoints Usage

### Send Email
Send an email using Microsoft Graph API:

```bash
POST /mail/send
Content-Type: application/json
X-Api-Key: your-api-key

{
  "sender": "user@example.com",
  "subject": "Meeting Request",
  "body": "<h1>Hello</h1><p>This is an HTML email.</p>",
  "to": "recipient1@example.com,recipient2@example.com",
  "cc": "cc@example.com"
}
```

- **sender**: Email address to send from (must have appropriate permissions)
- **subject**: Email subject line
- **body**: HTML body content
- **to**: Comma-separated email addresses for To recipients
- **cc**: Optional comma-separated email addresses for Cc recipients

### Receive Emails and Create Ideas
Fetch emails from the shared mailbox `idea@angermeier.net` and automatically create ideas:

```bash
GET /mail/receive
X-Api-Key: your-api-key
```

This endpoint will:
1. Fetch all unread emails from the shared mailbox inbox
2. Extract the subject (used as idea title) and body (used as description)
3. Use AI to generate 5 relevant tags for each email
4. Create a new idea in ChromaDB with the email content
5. Move the processed email to the Archive folder

**Example Response:**
```json
{
  "message": "Processed 3 emails",
  "ideas_created": [
    {
      "id": "abc-123",
      "title": "Feature Request: Dark Mode",
      "tags": ["feature", "ui", "accessibility", "design", "enhancement"],
      "email_id": "AAMkADQ..."
    }
  ]
}
```

## Logging

The application includes comprehensive logging functionality to help with debugging and monitoring:

### Log Levels

You can configure the log level using the `LOG_LEVEL` environment variable in your `.env` file:

- `DEBUG`: Detailed information for debugging (includes all operations)
- `INFO`: General information about application operation (default)
- `WARNING`: Warning messages for potentially problematic situations
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors that may cause application failure

### Log Format

All log messages include:
- Timestamp
- Logger name (module)
- Log level
- Message content

Example log output:
```
2025-01-15 10:30:45,123 - api.main - INFO - Connecting to ChromaDB Cloud...
2025-01-15 10:30:46,234 - api.main - INFO - Successfully connected to ChromaDB Cloud
2025-01-15 10:30:47,345 - api.main - INFO - Creating new idea: 'My Great Idea'
```

### What is Logged

- **Startup**: Application initialization and configuration
- **API Requests**: All endpoint access (INFO level)
- **Operations**: Successful operations like idea creation, retrieval (INFO level)
- **Errors**: All errors with full stack traces (ERROR level)
- **Debug Info**: Detailed operation information when LOG_LEVEL=DEBUG

## Troubleshooting

### Permission Denied Errors

If you encounter errors like `[Errno 13] Permission denied: '/home/ideagraph'` when using ChromaDB Cloud:

The application is configured to use ChromaDB Cloud without local persistence. This means:
- No local directories are created
- All data is stored in ChromaDB Cloud
- The `persist_directory` setting is explicitly disabled

This configuration prevents permission issues in restricted deployment environments while maintaining full functionality with ChromaDB Cloud.

### ChromaDB Connection Issues

If you have trouble connecting to ChromaDB Cloud:
1. Verify your `CHROMA_API_KEY` is correct in the `.env` file
2. Check that `CHROMA_TENANT` and `CHROMA_DATABASE` match your ChromaDB Cloud settings
3. Enable DEBUG logging (`LOG_LEVEL=DEBUG`) to see detailed connection information
4. Run the validation script: `python validate_chromadb_config.py`
