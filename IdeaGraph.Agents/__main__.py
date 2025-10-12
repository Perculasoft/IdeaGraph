"""Entry point for running IdeaGraph.Agents as a module."""

import sys
import os
import asyncio

# Ensure we're in the right directory to find config.yaml
agent_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(agent_dir)

# Import the main function from the agent module
# The file is named "IdeaGraph.Agents.py" which Python can't import normally
# So we use importlib to load it
import importlib.util
spec = importlib.util.spec_from_file_location("agent", os.path.join(agent_dir, "IdeaGraph.Agents.py"))
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)

if __name__ == "__main__":
    asyncio.run(agent_module.main())
