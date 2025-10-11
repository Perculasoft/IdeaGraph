# Migration Guide: ChromaDB Local to ChromaDB Cloud

This document explains how to migrate from local ChromaDB to ChromaDB Cloud.

## What Changed?

The IdeaGraph FastAPI backend now uses **ChromaDB Cloud** instead of a local ChromaDB instance. This provides:

- ✅ Centralized cloud storage
- ✅ Better scalability
- ✅ Shared access across multiple instances
- ✅ No local data directory management

## Required Configuration

### 1. Get ChromaDB Cloud Credentials

1. Visit [https://www.trychroma.com/](https://www.trychroma.com/)
2. Sign up or log in to your account
3. Create a new tenant or use an existing one
4. Generate an API key from your dashboard

### 2. Update Your Environment Variables

Replace the old configuration in your `.env` file:

#### Old Configuration (Local)
```env
# ChromaDB Data Directory
CHROMA_DIR=./data
```

#### New Configuration (Cloud)
```env
# ChromaDB Cloud Configuration
CHROMA_API_KEY=your-chroma-api-key-here
CHROMA_TENANT=your-tenant-name
CHROMA_DATABASE=IdeaGraph
```

### Environment Variables Explained

- **`CHROMA_API_KEY`** (Required): Your ChromaDB Cloud API key
  - Get this from your ChromaDB Cloud dashboard
  - Keep this secret and never commit it to version control

- **`CHROMA_TENANT`** (Optional): Your tenant name
  - If not provided, it will be automatically inferred from your API key
  - Only specify if your API key has access to multiple tenants

- **`CHROMA_DATABASE`** (Optional): The database name
  - Default: `IdeaGraph`
  - This is the name of your database in ChromaDB Cloud
  - You can change this if you want to use a different database name

## Migration Steps

1. **Backup your local data** (if you have important data):
   ```bash
   # Your local ChromaDB data is stored in the directory specified by CHROMA_DIR
   # By default: ./data
   cp -r ./data ./data_backup
   ```

2. **Update your `.env` file** with the new ChromaDB Cloud configuration:
   ```bash
   cp .env.example .env
   # Edit .env and add your CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE
   ```

3. **Verify your configuration**:
   ```bash
   python test_dotenv_loading.py
   ```

4. **Start the application**:
   ```bash
   uvicorn api.main:app --reload
   ```

## Data Migration

**Important**: Your existing local data will NOT be automatically migrated to ChromaDB Cloud.

If you need to migrate existing data:

1. Export your local collections
2. Re-create them in ChromaDB Cloud using the API endpoints
3. Or contact ChromaDB support for migration assistance

## Troubleshooting

### Error: "CHROMA_API_KEY is required"

Make sure you've set the `CHROMA_API_KEY` environment variable in your `.env` file.

### Error: "Tenant XYZ does not match ABC from the server"

Your API key might be scoped to a specific tenant. Either:
- Don't specify `CHROMA_TENANT` (let it be inferred from the API key)
- Or specify the correct tenant that matches your API key's scope

### Connection Issues

- Verify your API key is correct
- Check your internet connection
- Ensure you're not behind a firewall blocking `api.trychroma.com`

## Code Changes Summary

The main change is in `api/main.py`:

### Before
```python
import chromadb

CHROMA_DIR = os.getenv("CHROMA_DIR", "./data")
client = chromadb.PersistentClient(path=CHROMA_DIR)
```

### After
```python
import chromadb

CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
CHROMA_TENANT  = os.getenv("CHROMA_TENANT", "")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "IdeaGraph")

if not CHROMA_API_KEY:
    raise RuntimeError("CHROMA_API_KEY is required")

client = chromadb.CloudClient(
    api_key=CHROMA_API_KEY,
    tenant=CHROMA_TENANT if CHROMA_TENANT else None,
    database=CHROMA_DATABASE
)
```

## Additional Resources

- [ChromaDB Cloud Documentation](https://docs.trychroma.com/deployment/chroma-cloud)
- [ChromaDB Cloud Console](https://www.trychroma.com/)
- [IdeaGraph Repository](https://github.com/Perculasoft/IdeaGraph)

## Support

If you encounter any issues during migration, please:
1. Check the troubleshooting section above
2. Review the [ChromaDB Cloud documentation](https://docs.trychroma.com/)
3. Open an issue on the [IdeaGraph GitHub repository](https://github.com/Perculasoft/IdeaGraph/issues)
