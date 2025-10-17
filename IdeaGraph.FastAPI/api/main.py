from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from datetime import datetime
import os, uuid, httpx, math, tempfile
import chromadb
from dotenv import load_dotenv
import logging
from config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, OPENAI_API_KEY, OPENAI_ORG_ID, EMBED_MODEL, CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE, X_API_KEY, ALLOW_ORIGINS, LOG_FORMAT, LOG_LEVEL, KIGATE_API_URL, KIGATE_BEARER_TOKEN
from model import mailrequest, filecontentresponse
from fastapi.openapi.utils import get_openapi


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

# Graph API (optional for mail endpoints)
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
TENANT_ID = os.getenv("TENANT_ID", "")

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

class SectionIn(BaseModel):
    name: str

class SectionUpdateIn(BaseModel):
    name: str | None = None

class IdeaIn(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = []
    status: str = "New"
    section_id: str | None = None

class IdeaUpdateIn(BaseModel):
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    status: str | None = None
    section_id: str | None = None

class TaskIn(BaseModel):
    title: str
    description: str = ""
    repository: str = ""
    ki_suggestions: str = ""
    tags: list[str] = []
    status: str = "New"
    idea_id: str

class TaskUpdateIn(BaseModel):
    title: str | None = None
    description: str | None = None
    repository: str | None = None
    ki_suggestions: str | None = None
    tags: list[str] | None = None
    status: str | None = None
    idea_id: str | None = None

class RelationIn(BaseModel):
    source_id: str
    target_id: str
    relation_type: str  # depends_on / extends / contradicts / synergizes_with
    weight: float = 1.0

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
    # Configure settings to explicitly disable local persistence
    # This prevents ChromaDB from trying to create local directories
    settings = chromadb.Settings()
    settings.is_persistent = False
    # CloudClient shouldn't need local persistence, but some versions of the
    # Chroma SDK still try to prepare the directory specified in
    # ``persist_directory`` when creating new collections.  Using an empty
    # string makes the SDK fall back to the user's home directory which isn't
    # writable in our deployment environment (resulting in ``Permission
    # denied: '/home/ideagraph'`` when adding the first relation).  Point the
    # directory to a writable temporary location instead to avoid the
    # permission error while keeping persistence disabled.
    settings.persist_directory = os.path.join(tempfile.gettempdir(), "chromadb")
    os.makedirs(settings.persist_directory, exist_ok=True)
    
    client = chromadb.CloudClient(
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
        api_key=CHROMA_API_KEY,
        settings=settings
    )
    logger.info("Successfully connected to ChromaDB Cloud")
    logger.debug(f"ChromaDB tenant: {CHROMA_TENANT}, database: {CHROMA_DATABASE}")
    
    ideas = client.get_or_create_collection(name="ideas")        # ids, documents, embeddings, metadatas
    relations = client.get_or_create_collection(name="relations")# store edges as docs w/ metadata
    sections = client.get_or_create_collection(name="sections")  # ids, documents, metadatas
    tasks = client.get_or_create_collection(name="tasks")        # ids, documents, embeddings, metadatas
    logger.info("Successfully initialized ChromaDB collections: 'ideas', 'relations', 'sections', and 'tasks'")
except Exception as e:
    logger.error(f"Failed to connect to ChromaDB Cloud: {e}", exc_info=True)
    logger.error("Please check your CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE settings in .env file.")
    raise

# --- Include Routers ---
# Import and include Graph API mail router
if CLIENT_ID and CLIENT_SECRET and TENANT_ID:
    try:
        from graph import router as graph_router
        app.include_router(graph_router)
        logger.info("Graph API mail endpoints registered")
    except Exception as e:
        logger.warning(f"Failed to register Graph API mail router: {e}")
else:
    logger.warning("Graph API credentials not configured - mail endpoints disabled")

# --- Helper Functions ---
def parse_description_from_document(document: str) -> str:
    """
    Parse description from document format: {title}\n\n{description}\n\nTags: {tags}
    Returns empty string if parsing fails.
    """
    try:
        # Split by double newline to separate title, description, and tags
        parts = document.split("\n\n")
        if len(parts) >= 2:
            # The description is everything between title and tags section
            # Join all parts except first (title) and last (tags) if tags section exists
            if len(parts) >= 3 and parts[-1].startswith("Tags: "):
                description = "\n\n".join(parts[1:-1])
            else:
                # No tags section or malformed, take everything after title
                description = "\n\n".join(parts[1:])
            return description
        return ""
    except Exception as e:
        logger.warning(f"Failed to parse description from document: {e}")
        return ""

def parse_task_description_from_document(document: str) -> str:
    """
    Parse description from task document format: {title}\n\n{description}\n\nRepository: {repo}\n\nTags: {tags}
    Returns empty string if parsing fails.
    """
    try:
        # Split by double newline to separate title, description, repository and tags
        parts = document.split("\n\n")
        if len(parts) >= 2:
            # The description is everything between title and repository/tags sections
            description_parts = []
            for i, part in enumerate(parts[1:], 1):
                if part.startswith("Repository: ") or part.startswith("Tags: "):
                    break
                description_parts.append(part)
            return "\n\n".join(description_parts)
        return ""
    except Exception as e:
        logger.warning(f"Failed to parse task description from document: {e}")
        return ""

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

# --- Section CRUD Endpoints ---

@app.post("/section")
def create_section(section: SectionIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Creating new section: '{section.name}'")
    
    try:
        _id = str(uuid.uuid4())
        doc = section.name
        meta = {
            "name": section.name,
            "created_at": datetime.utcnow().isoformat()
        }
        # Sections don't need embeddings, just simple storage
        sections.add(ids=[_id], documents=[doc], metadatas=[meta])
        logger.info(f"Successfully created section with ID: {_id}")
        return {"id": _id, "name": meta["name"], "created_at": meta["created_at"]}
    except Exception as e:
        logger.error(f"Failed to create section '{section.name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create section: {str(e)}")

@app.get("/sections")
def list_sections(api_key: str = Depends(verify_api_key)):
    logger.debug("Listing all sections")
    try:
        res = sections.get(include=["metadatas"])
        out = []
        for i, _id in enumerate(res["ids"]):
            meta = res["metadatas"][i] or {}
            out.append({
                "id": _id,
                "name": meta.get("name", ""),
                "created_at": meta.get("created_at", "")
            })
        # Sort by name
        out.sort(key=lambda x: x.get("name", "").lower())
        logger.info(f"Successfully listed {len(out)} sections")
        return out
    except Exception as e:
        logger.error(f"Failed to list sections: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list sections: {str(e)}")

@app.get("/sections/{section_id}")
def get_section(section_id: str, api_key: str = Depends(verify_api_key)):
    logger.debug(f"Fetching section with ID: {section_id}")
    try:
        res = sections.get(ids=[section_id], include=["metadatas"])
        if not res["ids"]:
            logger.warning(f"Section not found: {section_id}")
            raise HTTPException(404, "Section not found")
        meta = res["metadatas"][0] or {}
        logger.info(f"Successfully fetched section: {section_id}")
        return {
            "id": section_id,
            "name": meta.get("name", ""),
            "created_at": meta.get("created_at", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get section {section_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get section: {str(e)}")

@app.put("/sections/{section_id}")
def update_section(section_id: str, section_update: SectionUpdateIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Updating section with ID: {section_id}")
    logger.debug(f"Update details - name: {section_update.name}")
    
    try:
        # Check if section exists
        res = sections.get(ids=[section_id], include=["metadatas"])
        if not res["ids"]:
            logger.warning(f"Section not found for update: {section_id}")
            raise HTTPException(404, "Section not found")
        
        # Get current metadata
        current_meta = res["metadatas"][0] or {}
        
        # Update only provided fields
        updated_name = section_update.name if section_update.name is not None else current_meta.get("name", "")
        
        # Update metadata
        new_meta = {
            "name": updated_name,
            "created_at": current_meta.get("created_at", datetime.utcnow().isoformat())
        }
        
        # Update in ChromaDB
        sections.update(ids=[section_id], documents=[updated_name], metadatas=[new_meta])
        logger.info(f"Successfully updated section with ID: {section_id}")
        
        return {
            "id": section_id,
            "name": new_meta["name"],
            "created_at": new_meta["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update section {section_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update section: {str(e)}")

@app.delete("/sections/{section_id}")
def delete_section(section_id: str, api_key: str = Depends(verify_api_key)):
    logger.info(f"Deleting section with ID: {section_id}")
    
    try:
        # Check if section exists
        res = sections.get(ids=[section_id])
        if not res["ids"]:
            logger.warning(f"Section not found for deletion: {section_id}")
            raise HTTPException(404, "Section not found")
        
        # Delete the section
        sections.delete(ids=[section_id])
        
        logger.info(f"Successfully deleted section with ID: {section_id}")
        return {"message": "Section deleted successfully", "id": section_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete section {section_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete section: {str(e)}")

# --- Idea CRUD Endpoints ---

@app.post("/idea")
async def create_idea(idea: IdeaIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Creating new idea: '{idea.title}'")
    logger.debug(f"Idea details - title: '{idea.title}', description length: {len(idea.description)}, tags: {idea.tags}, section_id: {idea.section_id}")
    
    try:
        _id = str(uuid.uuid4())
        doc = f"{idea.title}\n\n{idea.description}\n\nTags: {', '.join(idea.tags)}"
        vec = await embed_text(doc)
        meta = {
            "title": idea.title,
            "tags": ",".join(idea.tags),  # Convert list to comma-separated string for ChromaDB
            "created_at": datetime.utcnow().isoformat(),
            "status": idea.status
        }
        if idea.section_id:
            meta["section_id"] = idea.section_id
        ideas.add(ids=[_id], documents=[doc], embeddings=[vec], metadatas=[meta])
        logger.info(f"Successfully created idea with ID: {_id}")
        return {
            "id": _id, 
            "title": meta["title"], 
            "description": idea.description, 
            "tags": idea.tags, 
            "created_at": meta["created_at"], 
            "status": meta["status"],
            "section_id": idea.section_id,
            "relations": [], 
            "impact_score": 0.0
        }
    except Exception as e:
        logger.error(f"Failed to create idea '{idea.title}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create idea: {str(e)}")

@app.get("/ideas")
def list_ideas(api_key: str = Depends(verify_api_key)):
    logger.debug("Listing all ideas")
    try:
        res = ideas.get(include=["metadatas", "documents"])
        out = []
        for i, _id in enumerate(res["ids"]):
            meta = res["metadatas"][i] or {}
            doc = res["documents"][i] if res["documents"] else ""
            tags_str = meta.get("tags", "")
            tags_list = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
            description = parse_description_from_document(doc)
            idea_dict = {
                "id": _id,
                "title": meta.get("title",""),
                "description": description,
                "tags": tags_list,
                "created_at": meta.get("created_at", ""),
                "status": meta.get("status", "New")
            }
            if "section_id" in meta:
                idea_dict["section_id"] = meta["section_id"]
            out.append(idea_dict)
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
        res = ideas.get(ids=[idea_id], include=["metadatas", "documents"])
        if not res["ids"]:
            logger.warning(f"Idea not found: {idea_id}")
            raise HTTPException(404, "Idea not found")
        meta = res["metadatas"][0] or {}
        doc = res["documents"][0] if res["documents"] else ""
        description = parse_description_from_document(doc)
        # fetch relations where this idea is the source or target
        outgoing_rels = relations.get(where={"source_id": idea_id})
        incoming_rels = relations.get(where={"target_id": idea_id})
        
        # Combine and deduplicate relations
        all_rel_ids = set()
        edges = []
        
        for i, rid in enumerate(outgoing_rels["ids"]):
            if rid not in all_rel_ids:
                all_rel_ids.add(rid)
                m = outgoing_rels["metadatas"][i] or {}
                edges.append({
                    "id": rid,
                    "source_id": m.get("source_id"),
                    "target_id": m.get("target_id"),
                    "relation_type": m.get("relation_type"),
                    "weight": m.get("weight", 1.0)
                })
        
        for i, rid in enumerate(incoming_rels["ids"]):
            if rid not in all_rel_ids:
                all_rel_ids.add(rid)
                m = incoming_rels["metadatas"][i] or {}
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
        
        idea_dict = {
            "id": idea_id,
            "title": meta.get("title",""),
            "description": description,
            "tags": tags_list,
            "created_at": meta.get("created_at",""),
            "status": meta.get("status", "New"),
            "relations": edges
        }
        if "section_id" in meta:
            idea_dict["section_id"] = meta["section_id"]
        
        return idea_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get idea {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get idea: {str(e)}")

@app.put("/ideas/{idea_id}")
async def update_idea(idea_id: str, idea_update: IdeaUpdateIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Updating idea with ID: {idea_id}")
    logger.debug(f"Update details - title: {idea_update.title}, description length: {len(idea_update.description or '')}, tags: {idea_update.tags}, section_id: {idea_update.section_id}")
    
    try:
        # First check if idea exists and get current document
        res = ideas.get(ids=[idea_id], include=["metadatas", "documents"])
        if not res["ids"]:
            logger.warning(f"Idea not found for update: {idea_id}")
            raise HTTPException(404, "Idea not found")
        
        # Get current metadata and document
        current_meta = res["metadatas"][0] or {}
        current_doc = res["documents"][0] if res["documents"] else ""
        current_description = parse_description_from_document(current_doc)
        
        # Update only provided fields
        updated_title = idea_update.title if idea_update.title is not None else current_meta.get("title", "")
        updated_description = idea_update.description if idea_update.description is not None else current_description
        updated_tags = idea_update.tags if idea_update.tags is not None else [t.strip() for t in current_meta.get("tags", "").split(",") if t.strip()]
        updated_status = idea_update.status if idea_update.status is not None else current_meta.get("status", "New")
        
        # Create new document for embedding
        doc = f"{updated_title}\n\n{updated_description}\n\nTags: {', '.join(updated_tags)}"
        vec = await embed_text(doc)
        
        # Update metadata (without description to avoid size limit)
        new_meta = {
            "title": updated_title,
            "tags": ",".join(updated_tags),
            "created_at": current_meta.get("created_at", datetime.utcnow().isoformat()),
            "status": updated_status
        }
        
        # Handle section_id: if explicitly provided (even if None), update it; otherwise keep existing
        if idea_update.section_id is not None:
            new_meta["section_id"] = idea_update.section_id
        elif "section_id" in current_meta:
            new_meta["section_id"] = current_meta["section_id"]
        
        # Update in ChromaDB
        ideas.update(ids=[idea_id], documents=[doc], embeddings=[vec], metadatas=[new_meta])
        logger.info(f"Successfully updated idea with ID: {idea_id}")
        
        result = {
            "id": idea_id,
            "title": new_meta["title"],
            "description": updated_description,
            "tags": updated_tags,
            "created_at": new_meta["created_at"],
            "status": new_meta["status"]
        }
        if "section_id" in new_meta:
            result["section_id"] = new_meta["section_id"]
        
        return result
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
        
        # Delete any relations where this idea is the source or target
        outgoing_rels = relations.get(where={"source_id": idea_id})
        incoming_rels = relations.get(where={"target_id": idea_id})
        
        # Combine relation IDs to delete (deduplicate in case of self-relations)
        all_rel_ids = set(outgoing_rels["ids"]) | set(incoming_rels["ids"])
        
        if all_rel_ids:
            relations.delete(ids=list(all_rel_ids))
            logger.info(f"Deleted {len(all_rel_ids)} relations for idea {idea_id}")
        
        logger.info(f"Successfully deleted idea with ID: {idea_id}")
        return {"message": "Idea deleted successfully", "id": idea_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete idea {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete idea: {str(e)}")


@app.post("/ideas/{idea_id}/enhance")
async def enhance_idea(idea_id: str, api_key: str = Depends(verify_api_key)):
    """
    Du bist ein präziser deutscher Lektor.
    Verbessere Rechtschreibung, Grammatik, Stil und Struktur.
    Behalte Sinn & Fakten bei; erweitere nur behutsam um offensichtlich sinnvolle Klarstellungen (keine Spekulation, keine neuen externen Fakten). Schreibe auf Deutsch, sachlich, klar, ohne Marketing-Floskeln.
    """
    logger.info(f"Enhancing idea with ID: {idea_id}")
    
    try:
        # Get current idea
        res = ideas.get(ids=[idea_id], include=["metadatas", "documents"])
        if not res["ids"]:
            logger.warning(f"Idea not found for enhancement: {idea_id}")
            raise HTTPException(404, "Idea not found")
        
        current_meta = res["metadatas"][0] or {}
        current_doc = res["documents"][0] if res["documents"] else ""
        current_description = parse_description_from_document(current_doc)
        current_title = current_meta.get("title", "")
        
        if not current_description.strip():
            logger.warning(f"Idea {idea_id} has no description to enhance")
            raise HTTPException(400, "Idea has no description to enhance")
        
        # Call OpenAI to improve description and generate tags
        logger.debug(f"Calling OpenAI API to enhance description (length: {len(current_description)})")
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        if OPENAI_ORG_ID:
            headers["OpenAI-Organization"] = OPENAI_ORG_ID
        
        # Create prompt for OpenAI
        prompt = f""" Du bist ein präziser deutscher Lektor.

Given the following idea title and description, please:
1. Verbessere Rechtschreibung, Grammatik, Stil und Struktur.
2. Gestalten Sie die Beschreibung klarer und professioneller, ohne die ursprüngliche Bedeutung zu verlieren.
3. Behalte Sinn & Fakten bei; erweitere nur behutsam um offensichtlich sinnvolle Klarstellungen (keine Spekulation, keine neuen externen Fakten). Schreibe auf Deutsch, sachlich, klar, ohne Marketing-Floskeln.
4. Generiere genau 5 relevante Tags, die die Kernthemen dieser Idee beschreiben

Title: {current_title}

Description:
{current_description}

Please respond ONLY with a JSON object in this exact format (no markdown, no code blocks):
{{"improved_description": "your improved description here", "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]}}"""

        try:
            async with httpx.AsyncClient(timeout=60) as client_http:
                r = await client_http.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant that improves text and generates tags. Always respond with valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )
            r.raise_for_status()
            response_data = r.json()
            
            # Extract the improved description and tags from OpenAI response
            content = response_data["choices"][0]["message"]["content"].strip()
            logger.debug(f"OpenAI response: {content[:200]}...")
            
            # Parse JSON response (remove markdown code blocks if present)
            import json
            if content.startswith("```"):
                # Remove markdown code blocks
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            improved_description = result["improved_description"]
            new_tags = result["tags"][:5]  # Ensure max 5 tags
            
            logger.info(f"Successfully enhanced description and generated {len(new_tags)} tags")
            
            # Update the idea with improved description and new tags
            updated_title = current_title
            updated_status = current_meta.get("status", "New")
            
            # Create new document for embedding
            doc = f"{updated_title}\n\n{improved_description}\n\nTags: {', '.join(new_tags)}"
            vec = await embed_text(doc)
            
            # Update metadata
            new_meta = {
                "title": updated_title,
                "tags": ",".join(new_tags),
                "created_at": current_meta.get("created_at", datetime.utcnow().isoformat()),
                "status": updated_status
            }
            
            # Preserve section_id if it exists
            if "section_id" in current_meta:
                new_meta["section_id"] = current_meta["section_id"]
            
            # Update in ChromaDB
            ideas.update(ids=[idea_id], documents=[doc], embeddings=[vec], metadatas=[new_meta])
            logger.info(f"Successfully updated idea {idea_id} with enhanced content")
            
            result = {
                "id": idea_id,
                "title": updated_title,
                "description": improved_description,
                "tags": new_tags,
                "created_at": new_meta["created_at"],
                "status": updated_status
            }
            if "section_id" in new_meta:
                result["section_id"] = new_meta["section_id"]
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from OpenAI API: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {e.response.text}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to parse AI response")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enhance idea {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to enhance idea: {str(e)}")


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
async def add_relation(rel: RelationIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Adding relation: {rel.source_id} -> {rel.target_id} ({rel.relation_type})")
    logger.debug(f"Relation details - weight: {rel.weight}")

    try:
        # store each relation as its own doc in "relations"
        rid = f"{rel.source_id}->{rel.target_id}:{rel.relation_type}"
        meta = rel.dict()
        doc = f"{rel.source_id} {rel.relation_type} {rel.target_id}"
        vec = await embed_text(doc)
        relations.add(ids=[rid], documents=[doc], embeddings=[vec], metadatas=[meta])
        logger.info(f"Successfully added relation with ID: {rid}")
        return {"id": rid, **meta}
    except Exception as e:
        logger.error(f"Failed to add relation {rel.source_id} -> {rel.target_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add relation: {str(e)}")

@app.get("/relations/{idea_id}")
def list_relations(idea_id: str, api_key: str = Depends(verify_api_key)):
    logger.debug(f"Listing relations for idea: {idea_id}")
    try:
        # Get outgoing relations (where this idea is the source)
        outgoing_rels = relations.get(where={"source_id": idea_id})
        # Get incoming relations (where this idea is the target)
        incoming_rels = relations.get(where={"target_id": idea_id})
        
        # Combine and deduplicate relations by ID
        all_rel_ids = set()
        result = []
        
        # Add outgoing relations
        for i in range(len(outgoing_rels["ids"])):
            rel_id = outgoing_rels["ids"][i]
            if rel_id not in all_rel_ids:
                all_rel_ids.add(rel_id)
                result.append({
                    "id": rel_id,
                    "source_id": (outgoing_rels["metadatas"][i] or {}).get("source_id"),
                    "target_id": (outgoing_rels["metadatas"][i] or {}).get("target_id"),
                    "relation_type": (outgoing_rels["metadatas"][i] or {}).get("relation_type"),
                    "weight": (outgoing_rels["metadatas"][i] or {}).get("weight", 1.0),
                })
        
        # Add incoming relations
        for i in range(len(incoming_rels["ids"])):
            rel_id = incoming_rels["ids"][i]
            if rel_id not in all_rel_ids:
                all_rel_ids.add(rel_id)
                result.append({
                    "id": rel_id,
                    "source_id": (incoming_rels["metadatas"][i] or {}).get("source_id"),
                    "target_id": (incoming_rels["metadatas"][i] or {}).get("target_id"),
                    "relation_type": (incoming_rels["metadatas"][i] or {}).get("relation_type"),
                    "weight": (incoming_rels["metadatas"][i] or {}).get("weight", 1.0),
                })
        
        logger.info(f"Found {len(result)} relations for idea {idea_id} ({len(outgoing_rels['ids'])} outgoing, {len(incoming_rels['ids'])} incoming)")
        return result
    except Exception as e:
        logger.error(f"Failed to list relations for {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list relations: {str(e)}")

# --- Task CRUD Endpoints ---

@app.post("/task")
async def create_task(task: TaskIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Creating new task: '{task.title}' for idea {task.idea_id}")
    logger.debug(f"Task details - title: '{task.title}', description length: {len(task.description)}, tags: {task.tags}, repository: {task.repository}")
    
    try:
        # Verify the idea exists
        idea_res = ideas.get(ids=[task.idea_id])
        if not idea_res["ids"]:
            logger.warning(f"Idea {task.idea_id} not found for task creation")
            raise HTTPException(404, "Idea not found")
        
        _id = str(uuid.uuid4())
        doc = f"{task.title}\n\n{task.description}\n\nRepository: {task.repository}\n\nTags: {', '.join(task.tags)}"
        vec = await embed_text(doc)
        meta = {
            "title": task.title,
            "repository": task.repository,
            "ki_suggestions": task.ki_suggestions,
            "tags": ",".join(task.tags),
            "created_at": datetime.utcnow().isoformat(),
            "status": task.status,
            "idea_id": task.idea_id
        }
        tasks.add(ids=[_id], documents=[doc], embeddings=[vec], metadatas=[meta])
        logger.info(f"Successfully created task with ID: {_id}")
        return {
            "id": _id,
            "title": meta["title"],
            "description": task.description,
            "repository": meta["repository"],
            "ki_suggestions": meta["ki_suggestions"],
            "tags": task.tags,
            "created_at": meta["created_at"],
            "status": meta["status"],
            "idea_id": meta["idea_id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create task '{task.title}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@app.get("/tasks")
def list_tasks(api_key: str = Depends(verify_api_key)):
    logger.debug("Listing all tasks")
    try:
        res = tasks.get(include=["metadatas", "documents"])
        out = []
        for i, _id in enumerate(res["ids"]):
            meta = res["metadatas"][i] or {}
            doc = res["documents"][i] if res["documents"] else ""
            tags_str = meta.get("tags", "")
            tags_list = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
            
            # Parse description from document
            description = parse_task_description_from_document(doc)
            
            task_dict = {
                "id": _id,
                "title": meta.get("title", ""),
                "description": description,
                "repository": meta.get("repository", ""),
                "ki_suggestions": meta.get("ki_suggestions", ""),
                "tags": tags_list,
                "created_at": meta.get("created_at", ""),
                "status": meta.get("status", "New"),
                "idea_id": meta.get("idea_id", "")
            }
            out.append(task_dict)
        # Sort by created_at desc
        out.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        logger.info(f"Successfully listed {len(out)} tasks")
        return out
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")

@app.get("/tasks/idea/{idea_id}")
def list_tasks_by_idea(idea_id: str, api_key: str = Depends(verify_api_key)):
    logger.debug(f"Listing tasks for idea: {idea_id}")
    try:
        res = tasks.get(where={"idea_id": idea_id}, include=["metadatas", "documents"])
        out = []
        for i, _id in enumerate(res["ids"]):
            meta = res["metadatas"][i] or {}
            doc = res["documents"][i] if res["documents"] else ""
            tags_str = meta.get("tags", "")
            tags_list = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
            
            # Parse description from document
            description = parse_task_description_from_document(doc)
            
            task_dict = {
                "id": _id,
                "title": meta.get("title", ""),
                "description": description,
                "repository": meta.get("repository", ""),
                "ki_suggestions": meta.get("ki_suggestions", ""),
                "tags": tags_list,
                "created_at": meta.get("created_at", ""),
                "status": meta.get("status", "New"),
                "idea_id": meta.get("idea_id", "")
            }
            out.append(task_dict)
        # Sort by created_at desc
        out.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        logger.info(f"Successfully listed {len(out)} tasks for idea {idea_id}")
        return out
    except Exception as e:
        logger.error(f"Failed to list tasks for idea {idea_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")

@app.get("/tasks/{task_id}")
def get_task(task_id: str, api_key: str = Depends(verify_api_key)):
    logger.debug(f"Fetching task with ID: {task_id}")
    try:
        res = tasks.get(ids=[task_id], include=["metadatas", "documents"])
        if not res["ids"]:
            logger.warning(f"Task not found: {task_id}")
            raise HTTPException(404, "Task not found")
        meta = res["metadatas"][0] or {}
        doc = res["documents"][0] if res["documents"] else ""
        
        # Parse description from document
        description = parse_task_description_from_document(doc)
        
        tags_str = meta.get("tags", "")
        tags_list = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
        logger.info(f"Successfully fetched task: {task_id}")
        
        return {
            "id": task_id,
            "title": meta.get("title", ""),
            "description": description,
            "repository": meta.get("repository", ""),
            "ki_suggestions": meta.get("ki_suggestions", ""),
            "tags": tags_list,
            "created_at": meta.get("created_at", ""),
            "status": meta.get("status", "New"),
            "idea_id": meta.get("idea_id", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")

@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task_update: TaskUpdateIn, api_key: str = Depends(verify_api_key)):
    logger.info(f"Updating task with ID: {task_id}")
    logger.debug(f"Update details - title: {task_update.title}, description length: {len(task_update.description or '')}, tags: {task_update.tags}")
    
    try:
        # Check if task exists and get current data
        res = tasks.get(ids=[task_id], include=["metadatas", "documents"])
        if not res["ids"]:
            logger.warning(f"Task not found for update: {task_id}")
            raise HTTPException(404, "Task not found")
        
        # Get current metadata and document
        current_meta = res["metadatas"][0] or {}
        current_doc = res["documents"][0] if res["documents"] else ""
        current_description = parse_task_description_from_document(current_doc)
        
        # Update only provided fields
        updated_title = task_update.title if task_update.title is not None else current_meta.get("title", "")
        updated_description = task_update.description if task_update.description is not None else current_description
        updated_repository = task_update.repository if task_update.repository is not None else current_meta.get("repository", "")
        updated_ki_suggestions = task_update.ki_suggestions if task_update.ki_suggestions is not None else current_meta.get("ki_suggestions", "")
        updated_tags = task_update.tags if task_update.tags is not None else [t.strip() for t in current_meta.get("tags", "").split(",") if t.strip()]
        updated_status = task_update.status if task_update.status is not None else current_meta.get("status", "New")
        updated_idea_id = task_update.idea_id if task_update.idea_id is not None else current_meta.get("idea_id", "")
        
        # Create new document for embedding
        doc = f"{updated_title}\n\n{updated_description}\n\nRepository: {updated_repository}\n\nTags: {', '.join(updated_tags)}"
        vec = await embed_text(doc)
        
        # Update metadata
        new_meta = {
            "title": updated_title,
            "repository": updated_repository,
            "ki_suggestions": updated_ki_suggestions,
            "tags": ",".join(updated_tags),
            "created_at": current_meta.get("created_at", datetime.utcnow().isoformat()),
            "status": updated_status,
            "idea_id": updated_idea_id
        }
        
        # Update in ChromaDB
        tasks.update(ids=[task_id], documents=[doc], embeddings=[vec], metadatas=[new_meta])
        logger.info(f"Successfully updated task with ID: {task_id}")
        
        return {
            "id": task_id,
            "title": new_meta["title"],
            "description": updated_description,
            "repository": new_meta["repository"],
            "ki_suggestions": new_meta["ki_suggestions"],
            "tags": updated_tags,
            "created_at": new_meta["created_at"],
            "status": new_meta["status"],
            "idea_id": new_meta["idea_id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, api_key: str = Depends(verify_api_key)):
    logger.info(f"Deleting task with ID: {task_id}")
    
    try:
        # Check if task exists
        res = tasks.get(ids=[task_id])
        if not res["ids"]:
            logger.warning(f"Task not found for deletion: {task_id}")
            raise HTTPException(404, "Task not found")
        
        # Delete the task
        tasks.delete(ids=[task_id])
        
        logger.info(f"Successfully deleted task with ID: {task_id}")
        return {"message": "Task deleted successfully", "id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")

@app.post("/tasks/{task_id}/improve")
async def improve_task(task_id: str, api_key: str = Depends(verify_api_key)):
    """
    Improve task with AI:
    1. Normalize the description for a developer/Codex/Copilot
    2. Auto-generate title from text
    3. Extract 5 tags using KiGate API text-keyword-extractor-de agent
    4. Review with AI - set status to Ready if good, Review if issues (save feedback in KiSuggestions)
    """
    logger.info(f"Improving task with ID: {task_id}")
    
    try:
        # Get current task
        res = tasks.get(ids=[task_id], include=["metadatas", "documents"])
        if not res["ids"]:
            logger.warning(f"Task not found for improvement: {task_id}")
            raise HTTPException(404, "Task not found")
        
        current_meta = res["metadatas"][0] or {}
        current_doc = res["documents"][0] if res["documents"] else ""
        current_description = parse_task_description_from_document(current_doc)
        
        if not current_description.strip():
            logger.warning(f"Task {task_id} has no description to improve")
            raise HTTPException(400, "Task has no description to improve")
        
        # Step 1 & 2: Improve description and generate title with OpenAI
        logger.debug(f"Calling OpenAI API to improve task description and generate title")
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        if OPENAI_ORG_ID:
            headers["OpenAI-Organization"] = OPENAI_ORG_ID
        
        prompt = f"""You are a technical task optimizer for developers.

Given the following task description, please:
1. Normalize and improve the description to create a clear, well-structured task for a developer or AI assistant (Codex/Copilot)
2. Format the description as Markdown with clear sections
3. Correct spelling and grammar errors
4. Optimize text flow and clarity
5. Generate a concise, descriptive title (max 80 characters) that summarizes the task

Original Description:
{current_description}

Please respond ONLY with a JSON object in this exact format (no markdown, no code blocks):
{{"improved_description": "your improved description in Markdown format", "title": "Generated Task Title"}}"""

        try:
            async with httpx.AsyncClient(timeout=60) as client_http:
                r = await client_http.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant that optimizes technical task descriptions. Always respond with valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )
            r.raise_for_status()
            response_data = r.json()
            
            content = response_data["choices"][0]["message"]["content"].strip()
            logger.debug(f"OpenAI response: {content[:200]}...")
            
            # Parse JSON response
            import json
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            improved_description = result["improved_description"]
            generated_title = result["title"]
            
            logger.info(f"Successfully improved description and generated title")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from OpenAI API: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {e.response.text}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to parse AI response")
        
        # Step 3: Extract tags using KiGate API with text-keyword-extractor-de agent
        new_tags = []
        if KIGATE_API_URL and KIGATE_BEARER_TOKEN:
            try:
                logger.debug(f"Calling KiGate API text-keyword-extractor-de agent")
                kigate_headers = {"Authorization": f"Bearer {KIGATE_BEARER_TOKEN}"}
                async with httpx.AsyncClient(timeout=60) as client_http:
                    kigate_response = await client_http.post(
                        f"{KIGATE_API_URL}/agent/execute",
                        headers=kigate_headers,
                        json={
                            "agent_name": "text-keyword-extractor-de",
                            "message": improved_description
                        }
                    )
                kigate_response.raise_for_status()
                kigate_data = kigate_response.json()
                
                # Extract tags from the agent response
                if kigate_data.get("result") and kigate_data["result"].get("content"):
                    tags_content = kigate_data["result"]["content"]
                    # Try to parse tags from the response (assuming comma-separated or JSON format)
                    try:
                        # Try JSON array first
                        new_tags = json.loads(tags_content)
                        if not isinstance(new_tags, list):
                            new_tags = [str(new_tags)]
                    except:
                        # Fall back to comma-separated
                        new_tags = [t.strip() for t in tags_content.split(",") if t.strip()]
                    new_tags = new_tags[:5]  # Ensure max 5 tags
                    logger.info(f"Successfully extracted {len(new_tags)} tags from KiGate")
            except Exception as e:
                logger.warning(f"Failed to extract tags with KiGate API: {e}")
                # Fall back to generating tags with OpenAI
                new_tags = []
        
        # If KiGate tag extraction failed, use OpenAI as fallback
        if not new_tags:
            try:
                logger.debug("Falling back to OpenAI for tag extraction")
                tag_prompt = f"Extract exactly 5 relevant German keywords/tags from this task description. Return only a JSON array of strings: {improved_description}"
                async with httpx.AsyncClient(timeout=30) as client_http:
                    r = await client_http.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json={
                            "model": "gpt-4o-mini",
                            "messages": [
                                {"role": "system", "content": "You are a helpful assistant. Always respond with valid JSON array only."},
                                {"role": "user", "content": tag_prompt}
                            ],
                            "temperature": 0.5,
                            "max_tokens": 100
                        }
                    )
                r.raise_for_status()
                tag_response = r.json()
                tag_content = tag_response["choices"][0]["message"]["content"].strip()
                if tag_content.startswith("```"):
                    tag_content = tag_content.split("```")[1]
                    if tag_content.startswith("json"):
                        tag_content = tag_content[4:]
                    tag_content = tag_content.strip()
                new_tags = json.loads(tag_content)[:5]
                logger.info(f"Successfully generated {len(new_tags)} tags with OpenAI fallback")
            except Exception as e:
                logger.warning(f"Failed to generate tags with OpenAI fallback: {e}")
                new_tags = ["task", "development"]  # Default tags
        
        # Step 4: Review with AI - evaluate if task is meaningful, coherent, and feasible
        review_prompt = f"""You are a senior technical reviewer.

Review this task and determine if it is:
1. Meaningful - does it have a clear purpose?
2. Coherent - is it well-structured and understandable?
3. Feasible - can it realistically be implemented?

Task Title: {generated_title}

Task Description:
{improved_description}

Please respond ONLY with a JSON object:
{{"is_ready": true/false, "feedback": "brief feedback on issues or confirmation if ready (max 200 chars)"}}"""

        try:
            async with httpx.AsyncClient(timeout=30) as client_http:
                r = await client_http.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a helpful technical reviewer. Always respond with valid JSON only."},
                            {"role": "user", "content": review_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 300
                    }
                )
            r.raise_for_status()
            review_response = r.json()
            review_content = review_response["choices"][0]["message"]["content"].strip()
            
            if review_content.startswith("```"):
                review_content = review_content.split("```")[1]
                if review_content.startswith("json"):
                    review_content = review_content[4:]
                review_content = review_content.strip()
            
            review_result = json.loads(review_content)
            is_ready = review_result.get("is_ready", False)
            feedback = review_result.get("feedback", "")
            
            new_status = "Ready" if is_ready else "Review"
            ki_suggestions = "" if is_ready else feedback
            
            logger.info(f"Task review complete: status={new_status}, feedback={feedback[:50]}...")
            
        except Exception as e:
            logger.warning(f"Failed to review task with AI: {e}")
            # Default to Review status with generic feedback
            new_status = "Review"
            ki_suggestions = "AI review failed - please review manually"
        
        # Update the task with all improvements
        updated_repository = current_meta.get("repository", "")
        updated_idea_id = current_meta.get("idea_id", "")
        
        doc = f"{generated_title}\n\n{improved_description}\n\nRepository: {updated_repository}\n\nTags: {', '.join(new_tags)}"
        vec = await embed_text(doc)
        
        new_meta = {
            "title": generated_title,
            "repository": updated_repository,
            "ki_suggestions": ki_suggestions,
            "tags": ",".join(new_tags),
            "created_at": current_meta.get("created_at", datetime.utcnow().isoformat()),
            "status": new_status,
            "idea_id": updated_idea_id
        }
        
        # Update in ChromaDB
        tasks.update(ids=[task_id], documents=[doc], embeddings=[vec], metadatas=[new_meta])
        logger.info(f"Successfully improved and updated task {task_id}")
        
        return {
            "id": task_id,
            "title": new_meta["title"],
            "description": improved_description,
            "repository": new_meta["repository"],
            "ki_suggestions": new_meta["ki_suggestions"],
            "tags": new_tags,
            "created_at": new_meta["created_at"],
            "status": new_meta["status"],
            "idea_id": new_meta["idea_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to improve task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to improve task: {str(e)}")

@app.post("/tasks/{task_id}/github-issue")
async def create_github_issue_from_task(task_id: str, api_key: str = Depends(verify_api_key)):
    """
    Create a GitHub issue from a task that has status 'Ready'
    """
    logger.info(f"Creating GitHub issue for task: {task_id}")
    
    try:
        # Get current task
        res = tasks.get(ids=[task_id], include=["metadatas", "documents"])
        if not res["ids"]:
            logger.warning(f"Task not found: {task_id}")
            raise HTTPException(404, "Task not found")
        
        current_meta = res["metadatas"][0] or {}
        current_doc = res["documents"][0] if res["documents"] else ""
        
        # Check if task is ready
        if current_meta.get("status") != "Ready":
            logger.warning(f"Task {task_id} is not in Ready status")
            raise HTTPException(400, "Task must be in 'Ready' status to create GitHub issue")
        
        repository = current_meta.get("repository", "")
        if not repository:
            logger.warning(f"Task {task_id} has no repository specified")
            raise HTTPException(400, "Task must have a repository specified")
        
        title = current_meta.get("title", "")
        description = parse_task_description_from_document(current_doc)
        
        # Use KiGate API to create GitHub issue
        if not KIGATE_API_URL or not KIGATE_BEARER_TOKEN:
            logger.error("KiGate API is not configured")
            raise HTTPException(503, "KiGate API is not configured")
        
        try:
            logger.debug(f"Calling KiGate API to create GitHub issue for repository: {repository}")
            kigate_headers = {"Authorization": f"Bearer {KIGATE_BEARER_TOKEN}"}
            
            # Format the text for GitHub issue
            issue_text = f"# {title}\n\n{description}"
            
            async with httpx.AsyncClient(timeout=60) as client_http:
                kigate_response = await client_http.post(
                    f"{KIGATE_API_URL}/api/github/create-issue",
                    headers=kigate_headers,
                    json={
                        "repository": repository,
                        "text": issue_text
                    }
                )
            kigate_response.raise_for_status()
            issue_data = kigate_response.json()
            
            if issue_data.get("error"):
                logger.error(f"KiGate API returned error: {issue_data['error']}")
                raise HTTPException(500, f"Failed to create GitHub issue: {issue_data['error']}")
            
            logger.info(f"Successfully created GitHub issue #{issue_data.get('issue_number')} for task {task_id}")
            
            return {
                "issue_number": issue_data.get("issue_number"),
                "title": issue_data.get("title", title),
                "url": issue_data.get("url", ""),
                "error": None
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from KiGate API: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"KiGate API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Failed to create GitHub issue via KiGate: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create GitHub issue: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create GitHub issue for task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create GitHub issue: {str(e)}")

# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting IdeaGraph FastAPI server...")
    logger.info(f"Server will be available at: http://localhost:8000")
    logger.info(f"API documentation at: http://localhost:8000/docs")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

