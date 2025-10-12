from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from datetime import datetime
import os, uuid, httpx, math
import chromadb
from dotenv import load_dotenv
import logging
from fastapi.openapi.utils import get_openapi

# Load environment variables from .env file
load_dotenv()

# --- Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configure root logger
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler()
    ]
)

# Create logger for this module
logger = logging.getLogger(__name__)

# --- ENV ---
logger.debug("Loading environment variables...")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_ORG_ID  = os.getenv("OPENAI_ORG_ID", "")
EMBED_MODEL    = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
CHROMA_TENANT  = os.getenv("CHROMA_TENANT", "")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "IdeaGraph")
X_API_KEY = os.getenv("X_API_KEY", "")
ALLOW_ORIGINS  = [o.strip() for o in os.getenv("ALLOW_ORIGINS", "").split(",") if o.strip()]

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is required but not found in environment variables.")
    logger.error("Please create a .env file based on .env.example and set your OPENAI_API_KEY.")
    raise RuntimeError("OPENAI_API_KEY is required")

logger.info(f"Embedding model: {EMBED_MODEL}")
logger.info(f"ChromaDB database: {CHROMA_DATABASE}")
if ALLOW_ORIGINS:
    logger.info(f"CORS enabled for origins: {ALLOW_ORIGINS}")

# --- API Key Authentication ---
api_key_header = APIKeyHeader(name="X-Api-Key", auto_error=False)

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="IdeaGraph API",
        version="1.0.0",
        description="Die zentrale API für IdeaGraph",
        routes=app.routes,
    )

    openapi_schema["servers"] = [
        {
            "url": "https://api.angermeier.net",
            "description": "Produktivserver"
        }
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not X_API_KEY:
        # If no API key is configured, allow all requests
        logger.warning("No X_API_KEY configured in environment - authentication is disabled!")
        return api_key
    
    if api_key != X_API_KEY:
        logger.warning(f"Invalid API key attempt from request")
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key"
        )
    return api_key

logger.info("API key authentication configured" if X_API_KEY else "API key authentication is DISABLED")

# --- App + CORS ---
logger.info("Initializing FastAPI application...")

if ALLOW_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug(f"CORS middleware configured with origins: {ALLOW_ORIGINS}")

# --- Chroma Client/Collections ---
logger.info("Connecting to ChromaDB Cloud...")
try:
    client = chromadb.CloudClient(
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
        api_key=CHROMA_API_KEY
    )
    logger.info("Successfully connected to ChromaDB Cloud")
    logger.debug(f"ChromaDB tenant: {CHROMA_TENANT}, database: {CHROMA_DATABASE}")
    
    ideas = client.get_or_create_collection(name="ideas")        # ids, documents, embeddings, metadatas
    relations = client.get_or_create_collection(name="relations")# store edges as docs w/ metadata
    logger.info("Successfully initialized ChromaDB collections: 'ideas' and 'relations'")
except Exception as e:
    logger.error(f"Failed to connect to ChromaDB Cloud: {e}", exc_info=True)
    logger.error("Please check your CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE settings in .env file.")
    raise

# --- Schemas ---
class IdeaIn(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = []
    status: str = "New"

class IdeaUpdateIn(BaseModel):
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    status: str | None = None

class RelationIn(BaseModel):
    source_id: str
    target_id: str
    relation_type: str  # depends_on / extends / contradicts / synergizes_with
    weight: float = 1.0

# --- OpenAI Embedding ---
async def embed_text(text: str):
    logger.debug(f"Generating embedding for text (length: {len(text)} chars)")
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    if OPENAI_ORG_ID:
        headers["OpenAI-Organization"] = OPENAI_ORG_ID
    try:
        async with httpx.AsyncClient(timeout=30) as client_http:
            r = await client_http.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json={"model": EMBED_MODEL, "input": text}
            )
        r.raise_for_status()
        vec = r.json()["data"][0]["embedding"]
        # normalize (gut für Cosine-Ähnlichkeit innerhalb Chroma)
        norm = math.sqrt(sum(v*v for v in vec)) or 1.0
        normalized_vec = [v / norm for v in vec]
        logger.debug(f"Successfully generated embedding (dimension: {len(normalized_vec)})")
        return normalized_vec
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from OpenAI API: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error generating embedding: {e}", exc_info=True)
        raise

# --- API ---
@app.get("/health")
def health(api_key: str = Depends(verify_api_key)):
    logger.debug("Health check requested")
    try:
        collections = client.list_collections()
        collection_names = [col.name for col in collections]
        logger.info(f"Health check successful. Collections: {collection_names}")
        return {"status": "ok", "collections": collection_names}
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/idea")
async def create_idea(idea: IdeaIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Creating new idea: '{idea.title}'")
    logger.debug(f"Idea details - title: '{idea.title}', description length: {len(idea.description)}, tags: {idea.tags}")
    
    try:
        _id = str(uuid.uuid4())
        doc = f"{idea.title}\n\n{idea.description}\n\nTags: {', '.join(idea.tags)}"
        vec = await embed_text(doc)
        meta = {
            "title": idea.title,
            "description": idea.description,
            "tags": ",".join(idea.tags),  # Convert list to comma-separated string for ChromaDB
            "created_at": datetime.utcnow().isoformat(),
            "status": idea.status
        }
        ideas.add(ids=[_id], documents=[doc], embeddings=[vec], metadatas=[meta])
        logger.info(f"Successfully created idea with ID: {_id}")
        return {"id": _id, "title": meta["title"], "description": meta["description"], "tags": idea.tags, "created_at": meta["created_at"], "status": meta["status"], "relations": [], "impact_score": 0.0}
    except Exception as e:
        logger.error(f"Failed to create idea '{idea.title}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create idea: {str(e)}")

@app.get("/ideas")
def list_ideas(api_key: str = Depends(verify_api_key)):
    logger.debug("Listing all ideas")
    try:
        res = ideas.get()
        out = []
        for i, _id in enumerate(res["ids"]):
            meta = res["metadatas"][i] or {}
            tags_str = meta.get("tags", "")
            tags_list = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
            out.append({
                "id": _id,
                "title": meta.get("title",""),
                "description": meta.get("description",""),
                "tags": tags_list,
                "created_at": meta.get("created_at", ""),
                "status": meta.get("status", "New")
            })
        # optional: sort by created_at desc (string ISO OK)
        out.sort(key=lambda x: x.get("created_at",""), reverse=True)
        logger.info(f"Successfully listed {len(out)} ideas")
        return out
    except Exception as e:
        logger.error(f"Failed to list ideas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list ideas: {str(e)}")

@app.get("/ideas/{idea_id}")
def get_idea(idea_id: str, api_key: str = Depends(verify_api_key)):
    logger.debug(f"Fetching idea with ID: {idea_id}")
    try:
        res = ideas.get(ids=[idea_id])
        if not res["ids"]:
            logger.warning(f"Idea not found: {idea_id}")
            raise HTTPException(404, "Idea not found")
        meta = res["metadatas"][0] or {}
        # fetch relations where source_id = idea_id
        rels = relations.get(where={"source_id": idea_id})
        edges = []
        for i, rid in enumerate(rels["ids"]):
            m = rels["metadatas"][i] or {}
            edges.append({
                "id": rid,
                "source_id": m.get("source_id"),
                "target_id": m.get("target_id"),
                "relation_type": m.get("relation_type"),
                "weight": m.get("weight", 1.0)
            })
        tags_str = meta.get("tags", "")
        tags_list = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
        logger.info(f"Successfully fetched idea: {idea_id} with {len(edges)} relations")
        return {
            "id": idea_id,
            "title": meta.get("title",""),
            "description": meta.get("description",""),
            "tags": tags_list,
            "created_at": meta.get("created_at",""),
            "status": meta.get("status", "New"),
            "relations": edges
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get idea {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get idea: {str(e)}")

@app.put("/ideas/{idea_id}")
async def update_idea(idea_id: str, idea_update: IdeaUpdateIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Updating idea with ID: {idea_id}")
    logger.debug(f"Update details - title: {idea_update.title}, description length: {len(idea_update.description or '')}, tags: {idea_update.tags}")
    
    try:
        # First check if idea exists
        res = ideas.get(ids=[idea_id])
        if not res["ids"]:
            logger.warning(f"Idea not found for update: {idea_id}")
            raise HTTPException(404, "Idea not found")
        
        # Get current metadata
        current_meta = res["metadatas"][0] or {}
        
        # Update only provided fields
        updated_title = idea_update.title if idea_update.title is not None else current_meta.get("title", "")
        updated_description = idea_update.description if idea_update.description is not None else current_meta.get("description", "")
        updated_tags = idea_update.tags if idea_update.tags is not None else [t.strip() for t in current_meta.get("tags", "").split(",") if t.strip()]
        updated_status = idea_update.status if idea_update.status is not None else current_meta.get("status", "New")
        
        # Create new document for embedding
        doc = f"{updated_title}\n\n{updated_description}\n\nTags: {', '.join(updated_tags)}"
        vec = await embed_text(doc)
        
        # Update metadata
        new_meta = {
            "title": updated_title,
            "description": updated_description,
            "tags": ",".join(updated_tags),
            "created_at": current_meta.get("created_at", datetime.utcnow().isoformat()),
            "status": updated_status
        }
        
        # Update in ChromaDB
        ideas.update(ids=[idea_id], documents=[doc], embeddings=[vec], metadatas=[new_meta])
        logger.info(f"Successfully updated idea with ID: {idea_id}")
        
        return {
            "id": idea_id,
            "title": new_meta["title"],
            "description": new_meta["description"],
            "tags": updated_tags,
            "created_at": new_meta["created_at"],
            "status": new_meta["status"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update idea {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update idea: {str(e)}")

@app.delete("/ideas/{idea_id}")
def delete_idea(idea_id: str, api_key: str = Depends(verify_api_key)):
    logger.info(f"Deleting idea with ID: {idea_id}")
    
    try:
        # Check if idea exists
        res = ideas.get(ids=[idea_id])
        if not res["ids"]:
            logger.warning(f"Idea not found for deletion: {idea_id}")
            raise HTTPException(404, "Idea not found")
        
        # Delete the idea
        ideas.delete(ids=[idea_id])
        
        # Also delete any relations where this idea is the source
        rels = relations.get(where={"source_id": idea_id})
        if rels["ids"]:
            relations.delete(ids=rels["ids"])
            logger.info(f"Deleted {len(rels['ids'])} relations for idea {idea_id}")
        
        logger.info(f"Successfully deleted idea with ID: {idea_id}")
        return {"message": "Idea deleted successfully", "id": idea_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete idea {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete idea: {str(e)}")


@app.get("/similar/{idea_id}")
def similar(idea_id: str, k: int = 5, api_key: str = Depends(verify_api_key)):
    logger.debug(f"Finding similar ideas for: {idea_id} (k={k})")
    try:
        base = ideas.get(ids=[idea_id])
        if not base["ids"]:
            logger.warning(f"Idea not found for similarity search: {idea_id}")
            raise HTTPException(404, "Idea not found")
        # Query per document text (nutzt den im Store gespeicherten Embedding/Doc)
        qdoc = base["documents"][0]
        res = ideas.query(query_texts=[qdoc], n_results=k+1)
        out = []
        for i, _id in enumerate(res["ids"][0]):
            if _id == idea_id:  # skip self
                continue
            meta = res["metadatas"][0][i] or {}
            tags_str = meta.get("tags", "")
            tags_list = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
            out.append({
                "id": _id,
                "title": meta.get("title",""),
                "description": meta.get("description",""),
                "tags": tags_list,
                "created_at": meta.get("created_at",""),
                "status": meta.get("status", "New"),
                "distance": float(res["distances"][0][i]) if "distances" in res else None
            })
        logger.info(f"Found {len(out)} similar ideas for {idea_id}")
        return out[:k]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to find similar ideas for {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to find similar ideas: {str(e)}")

@app.post("/relation")
def add_relation(rel: RelationIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Adding relation: {rel.source_id} -> {rel.target_id} ({rel.relation_type})")
    logger.debug(f"Relation details - weight: {rel.weight}")
    
    try:
        # store each relation as its own doc in "relations"
        rid = f"{rel.source_id}->{rel.target_id}:{rel.relation_type}"
        meta = rel.dict()
        relations.upsert(ids=[rid], documents=[f"{rel.relation_type}"], metadatas=[meta])
        logger.info(f"Successfully added relation with ID: {rid}")
        return {"id": rid, **meta}
    except Exception as e:
        logger.error(f"Failed to add relation {rel.source_id} -> {rel.target_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add relation: {str(e)}")

@app.get("/relations/{idea_id}")
def list_relations(idea_id: str, api_key: str = Depends(verify_api_key)):
    logger.debug(f"Listing relations for idea: {idea_id}")
    try:
        rels = relations.get(where={"source_id": idea_id})
        result = [
            {
                "id": rels["ids"][i],
                "source_id": (rels["metadatas"][i] or {}).get("source_id"),
                "target_id": (rels["metadatas"][i] or {}).get("target_id"),
                "relation_type": (rels["metadatas"][i] or {}).get("relation_type"),
                "weight": (rels["metadatas"][i] or {}).get("weight", 1.0),
            }
            for i in range(len(rels["ids"]))
        ]
        logger.info(f"Found {len(result)} relations for idea {idea_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to list relations for {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list relations: {str(e)}")

# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting IdeaGraph FastAPI server...")
    logger.info(f"Server will be available at: http://localhost:8000")
    logger.info(f"API documentation at: http://localhost:8000/docs")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

