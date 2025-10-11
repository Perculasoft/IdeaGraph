from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os, uuid, httpx, math
import chromadb
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- ENV ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_ORG_ID  = os.getenv("OPENAI_ORG_ID", "")
EMBED_MODEL    = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
CHROMA_TENANT  = os.getenv("CHROMA_TENANT", "")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "IdeaGraph")
ALLOW_ORIGINS  = [o.strip() for o in os.getenv("ALLOW_ORIGINS", "").split(",") if o.strip()]

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY is required but not found in environment variables.")
    print("Please create a .env file based on .env.example and set your OPENAI_API_KEY.")
    raise RuntimeError("OPENAI_API_KEY is required")

# --- App + CORS ---
app = FastAPI(title="IdeaGraph API", version="0.1")
if ALLOW_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- Chroma Client/Collections ---
try:
    client = chromadb.CloudClient(
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
        api_key=CHROMA_API_KEY
    )
    ideas = client.get_or_create_collection(name="ideas")        # ids, documents, embeddings, metadatas
    relations = client.get_or_create_collection(name="relations")# store edges as docs w/ metadata
except Exception as e:
    print(f"ERROR: Failed to connect to ChromaDB Cloud: {e}")
    print("Please check your CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE settings in .env file.")
    raise

# --- Schemas ---
class IdeaIn(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = []

class RelationIn(BaseModel):
    source_id: str
    target_id: str
    relation_type: str  # depends_on / extends / contradicts / synergizes_with
    weight: float = 1.0

# --- OpenAI Embedding ---
async def embed_text(text: str):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    if OPENAI_ORG_ID:
        headers["OpenAI-Organization"] = OPENAI_ORG_ID
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
    return [v / norm for v in vec]

# --- API ---
@app.get("/health")
def health():
    collections = client.list_collections()
    collection_names = [col.name for col in collections]
    return {"status": "ok", "collections": collection_names}

@app.post("/idea")
async def create_idea(idea: IdeaIn):
    _id = str(uuid.uuid4())
    doc = f"{idea.title}\n\n{idea.description}\n\nTags: {', '.join(idea.tags)}"
    vec = await embed_text(doc)
    meta = {
        "title": idea.title,
        "description": idea.description,
        "tags": ",".join(idea.tags),  # Convert list to comma-separated string for ChromaDB
        "created_at": datetime.utcnow().isoformat()
    }
    ideas.add(ids=[_id], documents=[doc], embeddings=[vec], metadatas=[meta])
    return {"id": _id, "title": meta["title"], "description": meta["description"], "tags": idea.tags, "created_at": meta["created_at"], "relations": [], "impact_score": 0.0}

@app.get("/ideas")
def list_ideas():
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
            "created_at": meta.get("created_at", "")
        })
    # optional: sort by created_at desc (string ISO OK)
    out.sort(key=lambda x: x.get("created_at",""), reverse=True)
    return out

@app.get("/ideas/{idea_id}")
def get_idea(idea_id: str):
    res = ideas.get(ids=[idea_id])
    if not res["ids"]:
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
    return {
        "id": idea_id,
        "title": meta.get("title",""),
        "description": meta.get("description",""),
        "tags": tags_list,
        "created_at": meta.get("created_at",""),
        "relations": edges
    }

@app.get("/similar/{idea_id}")
def similar(idea_id: str, k: int = 5):
    base = ideas.get(ids=[idea_id])
    if not base["ids"]:
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
            "distance": float(res["distances"][0][i]) if "distances" in res else None
        })
    return out[:k]

@app.post("/relation")
def add_relation(rel: RelationIn):
    # store each relation as its own doc in "relations"
    rid = f"{rel.source_id}->{rel.target_id}:{rel.relation_type}"
    meta = rel.dict()
    relations.upsert(ids=[rid], documents=[f"{rel.relation_type}"], metadatas=[meta])
    return {"id": rid, **meta}

@app.get("/relations/{idea_id}")
def list_relations(idea_id: str):
    rels = relations.get(where={"source_id": idea_id})
    return [
        {
            "id": rels["ids"][i],
            "source_id": (rels["metadatas"][i] or {}).get("source_id"),
            "target_id": (rels["metadatas"][i] or {}).get("target_id"),
            "relation_type": (rels["metadatas"][i] or {}).get("relation_type"),
            "weight": (rels["metadatas"][i] or {}).get("weight", 1.0),
        }
        for i in range(len(rels["ids"]))
    ]

# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    print("Starting IdeaGraph FastAPI server...")
    print(f"Server will be available at: http://localhost:8000")
    print(f"API documentation at: http://localhost:8000/docs")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

