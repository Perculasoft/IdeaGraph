#!/usr/bin/env python3
"""
Validation script to check ChromaDB Cloud configuration.
This script verifies that the environment variables are correctly set
and that the ChromaDB CloudClient can be initialized (without actually connecting).
"""
import os
import sys

# Add the api directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def validate_chromadb_cloud_config():
    """Validate ChromaDB Cloud configuration"""
    print("Validating ChromaDB Cloud Configuration")
    print("=" * 60)
    print()
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        print(f"⚠ Warning: .env file not found at {env_file}")
        print("⚠ Create a .env file with required variables")
        print()
        print("Required variables:")
        print("  - OPENAI_API_KEY")
        print("  - CHROMA_API_KEY")
        print()
        return False
    
    print(f"✓ .env file found at {env_file}")
    print()
    
    # Import load_dotenv
    from dotenv import load_dotenv
    
    # Load .env file
    result = load_dotenv()
    if not result:
        print("✗ Failed to load .env file")
        return False
    
    print("✓ .env file loaded successfully")
    print()
    
    # Read ChromaDB Cloud environment variables
    CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
    CHROMA_TENANT = os.getenv("CHROMA_TENANT", "")
    CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "IdeaGraph")
    
    print("ChromaDB Cloud Configuration:")
    print(f"  CHROMA_API_KEY: {'***' + CHROMA_API_KEY[-4:] if len(CHROMA_API_KEY) > 4 else 'NOT SET'}")
    print(f"  CHROMA_TENANT: {CHROMA_TENANT if CHROMA_TENANT else 'NOT SET (will be auto-inferred)'}")
    print(f"  CHROMA_DATABASE: {CHROMA_DATABASE}")
    print()
    
    # Validate required variables
    errors = []
    
    if not CHROMA_API_KEY:
        errors.append("CHROMA_API_KEY is not set")
    
    if errors:
        print("✗ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        print()
        return False
    
    # Check OpenAI configuration (also required for the app)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    if not OPENAI_API_KEY:
        print("⚠ Warning: OPENAI_API_KEY is not set (required for embeddings)")
        print()
    
    print("✓ All required ChromaDB Cloud configuration is set!")
    print()
    
    # Try to import chromadb
    try:
        import chromadb
        print("✓ chromadb module is available")
        
        # Check if CloudClient is available
        if hasattr(chromadb, 'CloudClient'):
            print("✓ chromadb.CloudClient is available")
        else:
            print("✗ chromadb.CloudClient is not available")
            print("  Your chromadb version might be too old")
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import chromadb: {e}")
        print("  Run: pip install -r requirements.txt")
        return False
    
    print()
    print("=" * 60)
    print("✓ SUCCESS: ChromaDB Cloud configuration is valid!")
    print()
    print("Next steps:")
    print("  1. Verify your CHROMA_API_KEY is correct")
    print("  2. Start the application: uvicorn api.main:app --reload")
    print("  3. Test the /health endpoint: http://localhost:8000/health")
    print()
    
    return True

if __name__ == "__main__":
    success = validate_chromadb_cloud_config()
    sys.exit(0 if success else 1)
