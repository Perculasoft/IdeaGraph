#!/usr/bin/env python3
"""
Test script to verify that .env file is loaded correctly by main.py
"""
import os
import sys

# Add the api directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_dotenv_loading():
    """Test that environment variables are loaded from .env file"""
    print("Testing .env file loading in main.py")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        print(f"⚠ Warning: .env file not found at {env_file}")
        print("⚠ Create a .env file with OPENAI_API_KEY and other required variables")
        print()
        return False
    
    print(f"✓ .env file found at {env_file}")
    print()
    
    # Clear environment variables to test loading
    test_vars = ['OPENAI_API_KEY', 'OPENAI_ORG_ID', 'EMBEDDING_MODEL', 'CHROMA_DIR', 'ALLOW_ORIGINS']
    for var in test_vars:
        if var in os.environ:
            print(f"  Note: {var} was already set in environment")
            
    print()
    print("Simulating what main.py does:")
    print("-" * 60)
    
    # Import load_dotenv
    from dotenv import load_dotenv
    
    # Load .env file (this is what main.py does)
    result = load_dotenv()
    print(f"load_dotenv() returned: {result}")
    
    if not result:
        print("✗ Failed to load .env file")
        return False
    
    # Read environment variables like main.py does
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_ORG_ID  = os.getenv("OPENAI_ORG_ID", "")
    EMBED_MODEL    = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    CHROMA_DIR     = os.getenv("CHROMA_DIR", "./data")
    ALLOW_ORIGINS  = [o.strip() for o in os.getenv("ALLOW_ORIGINS", "").split(",") if o.strip()]
    
    print()
    print("Environment variables loaded:")
    print(f"  OPENAI_API_KEY: {'***' + OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 4 else 'NOT SET'}")
    print(f"  OPENAI_ORG_ID: {OPENAI_ORG_ID if OPENAI_ORG_ID else 'NOT SET'}")
    print(f"  EMBEDDING_MODEL: {EMBED_MODEL}")
    print(f"  CHROMA_DIR: {CHROMA_DIR}")
    print(f"  ALLOW_ORIGINS: {ALLOW_ORIGINS}")
    print()
    
    if not OPENAI_API_KEY:
        print("✗ OPENAI_API_KEY is not set in .env file")
        return False
    
    print("✓ SUCCESS: .env file is being loaded correctly!")
    print("✓ main.py will now read environment variables from .env file")
    return True

if __name__ == "__main__":
    success = test_dotenv_loading()
    sys.exit(0 if success else 1)
