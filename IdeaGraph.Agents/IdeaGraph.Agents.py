"""
IdeaGraph.Agents - CoreAgent for Semantic Relation Creation

This agent periodically runs to:
1. Load all ideas from ChromaDB
2. Generate embeddings for ideas without them
3. Find similar ideas using similarity search
4. Determine relation types using GPT
5. Store relations in the database

Usage: python -m IdeaGraph.Agents
"""

import os
import sys
import time
import yaml
import logging
import httpx
import chromadb
import json
import math
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CoreAgent:
    """CoreAgent for semantic relation creation between ideas."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the CoreAgent with configuration."""
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing CoreAgent...")
        
        # Initialize ChromaDB client
        self.chroma_client = self._init_chromadb()
        self.ideas_collection = self.chroma_client.get_or_create_collection(name="ideas")
        self.relations_collection = self.chroma_client.get_or_create_collection(name="relations")
        
        # Store OpenAI configuration
        self.openai_api_key = self._get_config_value("openai", "api_key", "OPENAI_API_KEY", required=True)
        self.openai_org_id = self._get_config_value("openai", "org_id", "OPENAI_ORG_ID")
        self.embedding_model = self.config["openai"]["embedding_model"]
        self.chat_model = self.config["openai"]["chat_model"]
        
        # Store API configuration
        self.api_base_url = self.config["api"]["base_url"]
        self.api_key = self._get_config_value("api", "api_key", "X_API_KEY")
        self.use_direct_db = self.config["api"]["use_direct_db"]
        
        self.logger.info("CoreAgent initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def _get_config_value(self, section: str, key: str, env_var: str, required: bool = False) -> str:
        """Get config value from file or environment variable."""
        value = self.config[section][key]
        if not value:
            value = os.getenv(env_var, "")
        if required and not value:
            raise ValueError(f"Required configuration '{section}.{key}' or environment variable '{env_var}' not found")
        return value
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config["logging"]["level"]
        log_format = self.config["logging"]["format"]
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format=log_format,
            handlers=[logging.StreamHandler()]
        )
    
    def _init_chromadb(self) -> chromadb.CloudClient:
        """Initialize ChromaDB Cloud client."""
        tenant = self._get_config_value("chromadb", "tenant", "CHROMA_TENANT")
        database = self._get_config_value("chromadb", "database", "CHROMA_DATABASE")
        api_key = self._get_config_value("chromadb", "api_key", "CHROMA_API_KEY", required=True)
        
        self.logger.info(f"Connecting to ChromaDB Cloud (database: {database})...")
        try:
            client = chromadb.CloudClient(
                tenant=tenant,
                database=database,
                api_key=api_key
            )
            self.logger.info("Successfully connected to ChromaDB Cloud")
            return client
        except Exception as e:
            self.logger.error(f"Failed to connect to ChromaDB Cloud: {e}", exc_info=True)
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API."""
        headers = {"Authorization": f"Bearer {self.openai_api_key}"}
        if self.openai_org_id:
            headers["OpenAI-Organization"] = self.openai_org_id
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers=headers,
                    json={"model": self.embedding_model, "input": text}
                )
            r.raise_for_status()
            vec = r.json()["data"][0]["embedding"]
            
            # Normalize the vector
            norm = math.sqrt(sum(v*v for v in vec)) or 1.0
            normalized_vec = [v / norm for v in vec]
            return normalized_vec
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}", exc_info=True)
            raise
    
    async def determine_relation(self, idea1: Dict[str, Any], idea2: Dict[str, Any], distance: float) -> Optional[Dict[str, Any]]:
        """Use GPT to determine relation type and confidence between two ideas."""
        headers = {"Authorization": f"Bearer {self.openai_api_key}"}
        if self.openai_org_id:
            headers["OpenAI-Organization"] = self.openai_org_id
        
        # Parse idea details
        idea1_title = idea1["metadata"].get("title", "")
        idea1_doc = idea1.get("document", "")
        idea2_title = idea2["metadata"].get("title", "")
        idea2_doc = idea2.get("document", "")
        
        prompt = f"""Analyze the semantic relationship between these two ideas:

Idea 1:
Title: {idea1_title}
Content: {idea1_doc}

Idea 2:
Title: {idea2_title}
Content: {idea2_doc}

Similarity Distance: {distance:.4f}

Please determine:
1. The type of relationship (choose one): similar, extends, depends_on, contradicts, synergizes_with, or none
2. A confidence score from 0.0 to 1.0 indicating how strong this relationship is
3. A brief description of why this relationship exists

Respond ONLY with a JSON object (no markdown, no code blocks):
{{"relation_type": "similar", "confidence": 0.85, "description": "Both ideas focus on..."}}

If there is no meaningful relationship, use relation_type "none" and confidence < 0.75."""

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": self.chat_model,
                        "messages": [
                            {"role": "system", "content": "You are an AI assistant that analyzes semantic relationships between ideas. Always respond with valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                )
            r.raise_for_status()
            response_data = r.json()
            
            # Extract and parse the response
            content = response_data["choices"][0]["message"]["content"].strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            return result
        except Exception as e:
            self.logger.error(f"Error determining relation: {e}", exc_info=True)
            return None
    
    async def store_relation(self, source_id: str, target_id: str, relation_type: str, confidence: float, description: str = ""):
        """Store a relation via API or directly in ChromaDB."""
        if self.use_direct_db:
            # Store directly in ChromaDB
            rid = f"{source_id}->{target_id}:{relation_type}"
            meta = {
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": relation_type,
                "weight": confidence,
                "description": description,
                "created_at": datetime.utcnow().isoformat(),
                "created_by": "CoreAgent"
            }
            self.relations_collection.upsert(
                ids=[rid],
                documents=[f"{relation_type}: {description}"],
                metadatas=[meta]
            )
            self.logger.info(f"Stored relation directly: {rid}")
        else:
            # Store via API
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["X-Api-Key"] = self.api_key
            
            payload = {
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": relation_type,
                "weight": confidence
            }
            
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    r = await client.post(
                        f"{self.api_base_url}/relation",
                        headers=headers,
                        json=payload
                    )
                r.raise_for_status()
                self.logger.info(f"Stored relation via API: {source_id} -> {target_id} ({relation_type})")
            except Exception as e:
                self.logger.error(f"Error storing relation via API: {e}", exc_info=True)
                raise
    
    def get_all_ideas(self) -> List[Dict[str, Any]]:
        """Get all ideas from ChromaDB."""
        try:
            result = self.ideas_collection.get(include=["metadatas", "documents", "embeddings"])
            ideas = []
            for i, idea_id in enumerate(result["ids"]):
                ideas.append({
                    "id": idea_id,
                    "metadata": result["metadatas"][i] or {},
                    "document": result["documents"][i] if result["documents"] else "",
                    "embedding": result["embeddings"][i] if result["embeddings"] else None
                })
            self.logger.info(f"Retrieved {len(ideas)} ideas from ChromaDB")
            return ideas
        except Exception as e:
            self.logger.error(f"Error retrieving ideas: {e}", exc_info=True)
            return []
    
    async def update_idea_embedding(self, idea_id: str, document: str) -> List[float]:
        """Generate and update embedding for an idea."""
        self.logger.info(f"Generating embedding for idea {idea_id}")
        embedding = await self.embed_text(document)
        
        # Update the idea with new embedding
        self.ideas_collection.update(
            ids=[idea_id],
            embeddings=[embedding]
        )
        self.logger.info(f"Updated embedding for idea {idea_id}")
        return embedding
    
    def check_existing_relation(self, source_id: str, target_id: str) -> bool:
        """Check if a relation already exists between two ideas."""
        try:
            # Check in both directions
            result = self.relations_collection.get(
                where={
                    "$or": [
                        {
                            "$and": [
                                {"source_id": source_id},
                                {"target_id": target_id}
                            ]
                        },
                        {
                            "$and": [
                                {"source_id": target_id},
                                {"target_id": source_id}
                            ]
                        }
                    ]
                }
            )
            return len(result["ids"]) > 0
        except Exception as e:
            self.logger.debug(f"Error checking existing relation: {e}")
            # If we can't check, assume it doesn't exist
            return False
    
    async def process_idea(self, idea: Dict[str, Any]):
        """Process a single idea: update embedding if needed, find similar ideas, create relations."""
        idea_id = idea["id"]
        document = idea["document"]
        embedding = idea["embedding"]
        
        self.logger.info(f"Processing idea: {idea_id}")
        
        # Generate embedding if missing
        if not embedding or len(embedding) == 0:
            self.logger.info(f"Idea {idea_id} has no embedding, generating...")
            embedding = await self.update_idea_embedding(idea_id, document)
        
        # Find similar ideas
        try:
            n_results = self.config["similarity_search"]["n_results"]
            similar_results = self.ideas_collection.query(
                query_embeddings=[embedding],
                n_results=n_results + 1,  # +1 because the idea itself will be included
                include=["metadatas", "documents", "distances"]
            )
            
            # Process each similar idea
            confidence_threshold = self.config["similarity_search"]["confidence_threshold"]
            relations_created = 0
            
            for i, similar_id in enumerate(similar_results["ids"][0]):
                # Skip self
                if similar_id == idea_id:
                    continue
                
                # Check if relation already exists
                if self.check_existing_relation(idea_id, similar_id):
                    self.logger.debug(f"Relation already exists: {idea_id} <-> {similar_id}, skipping")
                    continue
                
                distance = similar_results["distances"][0][i]
                similar_idea = {
                    "id": similar_id,
                    "metadata": similar_results["metadatas"][0][i] or {},
                    "document": similar_results["documents"][0][i] if similar_results["documents"] else ""
                }
                
                # Determine relation type
                self.logger.debug(f"Analyzing relation between {idea_id} and {similar_id} (distance: {distance:.4f})")
                relation_info = await self.determine_relation(idea, similar_idea, distance)
                
                if relation_info and relation_info["relation_type"] != "none":
                    confidence = relation_info["confidence"]
                    
                    if confidence >= confidence_threshold:
                        # Create the relation
                        await self.store_relation(
                            source_id=idea_id,
                            target_id=similar_id,
                            relation_type=relation_info["relation_type"],
                            confidence=confidence,
                            description=relation_info.get("description", "")
                        )
                        relations_created += 1
                        self.logger.info(
                            f"Created relation: {idea_id} -> {similar_id} "
                            f"({relation_info['relation_type']}, confidence: {confidence:.2f})"
                        )
                    else:
                        self.logger.debug(
                            f"Skipping relation (low confidence): {idea_id} -> {similar_id} "
                            f"({relation_info['relation_type']}, confidence: {confidence:.2f})"
                        )
            
            self.logger.info(f"Created {relations_created} relations for idea {idea_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing idea {idea_id}: {e}", exc_info=True)
    
    async def run_once(self):
        """Run the agent once to process all ideas."""
        self.logger.info("=" * 80)
        self.logger.info("Starting CoreAgent execution")
        self.logger.info("=" * 80)
        
        start_time = time.time()
        
        # Get all ideas
        ideas = self.get_all_ideas()
        
        if not ideas:
            self.logger.warning("No ideas found in database")
            return
        
        # Process each idea
        total_ideas = len(ideas)
        for idx, idea in enumerate(ideas, 1):
            self.logger.info(f"Processing idea {idx}/{total_ideas}")
            try:
                await self.process_idea(idea)
            except Exception as e:
                self.logger.error(f"Error processing idea {idea['id']}: {e}", exc_info=True)
                # Continue with next idea
                continue
        
        elapsed_time = time.time() - start_time
        self.logger.info("=" * 80)
        self.logger.info(f"CoreAgent execution completed in {elapsed_time:.2f} seconds")
        self.logger.info("=" * 80)
    
    async def run_loop(self):
        """Run the agent in a continuous loop with configured interval."""
        execution_interval = self.config["execution_interval"]
        self.logger.info(f"Starting CoreAgent loop (interval: {execution_interval}s)")
        
        while True:
            try:
                await self.run_once()
            except Exception as e:
                self.logger.error(f"Error in agent execution: {e}", exc_info=True)
            
            self.logger.info(f"Sleeping for {execution_interval} seconds...")
            time.sleep(execution_interval)


async def main():
    """Main entry point for the CoreAgent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="IdeaGraph CoreAgent - Semantic Relation Creation")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (instead of continuous loop)"
    )
    
    args = parser.parse_args()
    
    # Create and run agent
    agent = CoreAgent(config_path=args.config)
    
    if args.once:
        await agent.run_once()
    else:
        await agent.run_loop()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
