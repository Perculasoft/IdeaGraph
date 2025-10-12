# IdeaGraph.Agents - CoreAgent

## Overview

The **CoreAgent** is an intelligent background service that automatically discovers and creates semantic relationships between ideas in the IdeaGraph system. It uses **ChromaDB** for vector similarity search and **OpenAI GPT** models to understand the nature and quality of relationships between ideas.

## Features

- **Automatic Embedding Generation**: Generates embeddings for ideas that don't have them using OpenAI's `text-embedding-3-large` model
- **Semantic Similarity Search**: Finds related ideas using vector similarity in ChromaDB
- **Intelligent Relation Detection**: Uses GPT-4o-mini to analyze and classify relationships between ideas
- **Configurable Execution**: Run continuously on a schedule or execute once
- **Robust Error Handling**: Errors in processing one idea don't stop the entire service
- **Flexible Storage**: Store relations via FastAPI or directly to ChromaDB
- **Comprehensive Logging**: Detailed logs for monitoring and debugging

## Relation Types

The CoreAgent can identify the following types of relationships:

- `similar` - Ideas that are similar or related in content
- `extends` - One idea extends or builds upon another
- `depends_on` - One idea depends on another to be realized
- `contradicts` - Ideas that contradict or conflict with each other
- `synergizes_with` - Ideas that work well together and amplify each other

## Quick Start

1. Navigate to the IdeaGraph.Agents directory:
```bash
cd IdeaGraph.Agents
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Edit `.env` and add your API keys:
```bash
OPENAI_API_KEY=your-openai-api-key
CHROMA_API_KEY=your-chroma-api-key
X_API_KEY=your-api-key-for-ideagraph-api
```

5. Test the configuration:
```bash
python test_agent.py
```

6. Run the agent once to test:
```bash
python __main__.py --once
```

7. Run the agent continuously:
```bash
python __main__.py
```

## Configuration

Edit `config.yaml` to customize the agent behavior:

### Key Configuration Options

- `execution_interval`: How often to run the agent (in seconds)
- `similarity_search.n_results`: Number of similar ideas to find per idea
- `similarity_search.confidence_threshold`: Minimum confidence score to create a relation (0.0 - 1.0)
- `openai.embedding_model`: OpenAI model for generating embeddings
- `openai.chat_model`: OpenAI model for analyzing relationships
- `api.use_direct_db`: Whether to write relations directly to ChromaDB or via API

## Usage

### Run Continuously (Background Service)

Run the agent in continuous mode, processing ideas at the configured interval:

```bash
python -m IdeaGraph.Agents
```

Or specify a custom config file:

```bash
python -m IdeaGraph.Agents --config path/to/config.yaml
```

### Run Once

Execute the agent once and exit:

```bash
python -m IdeaGraph.Agents --once
```

This is useful for:
- Testing the configuration
- Manual execution after adding many new ideas
- Scheduled cron jobs

## How It Works

1. **Load Ideas**: Retrieves all ideas from the ChromaDB `ideas` collection
2. **Check Embeddings**: For each idea without an embedding, generates one using OpenAI
3. **Find Similar Ideas**: Performs a similarity search to find related ideas
4. **Analyze Relations**: Uses GPT-4o-mini to determine the type and quality of each relationship
5. **Store Relations**: Creates relations that meet the confidence threshold
6. **Repeat**: Continues processing all ideas, then waits for the next interval

## Example Workflow

```
[CoreAgent] Starting execution
[CoreAgent] Retrieved 42 ideas from ChromaDB
[CoreAgent] Processing idea 1/42
[CoreAgent] Idea abc123 has no embedding, generating...
[CoreAgent] Updated embedding for idea abc123
[CoreAgent] Analyzing relation between abc123 and def456 (distance: 0.2341)
[CoreAgent] Created relation: abc123 -> def456 (similar, confidence: 0.87)
[CoreAgent] Created 3 relations for idea abc123
...
[CoreAgent] Execution completed in 45.32 seconds
[CoreAgent] Sleeping for 300 seconds...
```

## Logging

Logs are output to stdout and can be configured in `config.yaml`:

- `logging.level`: Set to DEBUG, INFO, WARNING, ERROR, or CRITICAL
- `logging.format`: Customize the log message format

Example of redirecting logs to a file:

```bash
python -m IdeaGraph.Agents > coreagent.log 2>&1
```

## Running as a Service

### Linux (systemd)

Create a systemd service file `/etc/systemd/system/ideagraph-coreagent.service`:

```ini
[Unit]
Description=IdeaGraph CoreAgent - Semantic Relation Creation
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/IdeaGraph/IdeaGraph.Agents
Environment="PATH=/path/to/python/bin"
ExecStart=/path/to/python/bin/python -m IdeaGraph.Agents
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ideagraph-coreagent
sudo systemctl start ideagraph-coreagent
sudo systemctl status ideagraph-coreagent
```

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "IdeaGraph.Agents"]
```

Build and run:
```bash
docker build -t ideagraph-coreagent .
docker run -d --name coreagent --env-file .env ideagraph-coreagent
```

## Troubleshooting

### Agent not creating relations

- Check the `confidence_threshold` in config.yaml - it might be too high
- Review logs to see if ideas are being found as similar
- Verify that ideas have meaningful content (not just short titles)

### Out of memory errors

- Reduce `similarity_search.n_results` in config
- Increase `execution_interval` to give the system more rest time
- Process ideas in smaller batches

### API connection errors

- Verify `api.base_url` is correct
- Check that the FastAPI service is running
- Ensure `X_API_KEY` matches between agent and API

### Rate limiting from OpenAI

- Increase `execution_interval` to reduce API calls
- Consider using `use_direct_db: true` to avoid API overhead
- Check your OpenAI API rate limits

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Structure

- `IdeaGraph.Agents.py` - Main CoreAgent implementation
- `config.yaml` - Configuration file
- `.env` - Environment variables (not committed)
- `requirements.txt` - Python dependencies

## License

See the main repository LICENSE.txt file.

## Support

For issues or questions, please open an issue in the GitHub repository.
