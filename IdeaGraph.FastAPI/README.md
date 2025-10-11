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

- `GET /health` - Health check
- `POST /idea` - Create a new idea
- `GET /ideas` - List all ideas
- `GET /ideas/{idea_id}` - Get a specific idea
- `GET /similar/{idea_id}` - Find similar ideas
- `POST /relation` - Create a relation between ideas
- `GET /relations/{idea_id}` - Get relations for an idea

## Features

- **Semantic Search**: Uses OpenAI embeddings for semantic similarity
- **Vector Database**: ChromaDB Cloud for efficient vector storage and retrieval
- **Relation Tracking**: Track relationships between ideas (depends_on, extends, contradicts, synergizes_with)
- **CORS Support**: Configurable CORS for frontend integration
