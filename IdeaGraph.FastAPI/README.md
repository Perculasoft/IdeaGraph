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

# Optional: ChromaDB data directory (default: ./data)
CHROMA_DIR=./data

# Optional: CORS allowed origins (comma-separated)
ALLOW_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Run the Application

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

## Testing Environment Configuration

To verify that your `.env` file is being loaded correctly:

```bash
python test_dotenv_loading.py
```

## API Endpoints

- `GET /health` - Health check
- `POST /idea` - Create a new idea
- `GET /ideas` - List all ideas
- `GET /ideas/{idea_id}` - Get a specific idea
- `GET /similar/{idea_id}` - Find similar ideas
- `POST /relation` - Create a relation between ideas
- `GET /relations/{idea_id}` - Get relations for an idea

## Features

- **Semantic Search**: Uses OpenAI embeddings for semantic similarity
- **Vector Database**: ChromaDB for efficient vector storage and retrieval
- **Relation Tracking**: Track relationships between ideas (depends_on, extends, contradicts, synergizes_with)
- **CORS Support**: Configurable CORS for frontend integration
