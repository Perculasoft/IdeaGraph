"""
Example usage script for IdeaGraph CoreAgent

This example demonstrates how to use the CoreAgent programmatically
(without running it as a command-line tool).
"""

import asyncio
import logging
import importlib.util
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def example_run_once():
    """Example: Run the agent once to process all ideas."""
    print("=" * 80)
    print("Example 1: Running CoreAgent once")
    print("=" * 80)
    
    # Load the agent module
    spec = importlib.util.spec_from_file_location(
        "agent", 
        os.path.join(os.path.dirname(__file__), "IdeaGraph.Agents.py")
    )
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    
    # Create agent instance with custom config
    agent = agent_module.CoreAgent(config_path="config.yaml")
    
    # Run once
    await agent.run_once()
    
    print("\n✓ Agent execution completed\n")


async def example_with_custom_config():
    """Example: Using custom configuration values."""
    print("=" * 80)
    print("Example 2: Using custom configuration")
    print("=" * 80)
    
    # You can modify config values after loading
    spec = importlib.util.spec_from_file_location(
        "agent", 
        os.path.join(os.path.dirname(__file__), "IdeaGraph.Agents.py")
    )
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    
    agent = agent_module.CoreAgent(config_path="config.yaml")
    
    # Override config values
    agent.config["similarity_search"]["confidence_threshold"] = 0.80
    agent.config["similarity_search"]["n_results"] = 3
    
    print(f"Using confidence threshold: {agent.config['similarity_search']['confidence_threshold']}")
    print(f"Using n_results: {agent.config['similarity_search']['n_results']}")
    
    # Run once with custom config
    await agent.run_once()
    
    print("\n✓ Agent execution completed with custom config\n")


async def example_processing_specific_idea():
    """Example: Process a specific idea instead of all ideas."""
    print("=" * 80)
    print("Example 3: Processing a specific idea")
    print("=" * 80)
    
    spec = importlib.util.spec_from_file_location(
        "agent", 
        os.path.join(os.path.dirname(__file__), "IdeaGraph.Agents.py")
    )
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    
    agent = agent_module.CoreAgent(config_path="config.yaml")
    
    # Get all ideas
    ideas = agent.get_all_ideas()
    
    if not ideas:
        print("No ideas found in database")
        return
    
    # Process only the first idea (as an example)
    print(f"Processing only idea: {ideas[0]['id']}")
    await agent.process_idea(ideas[0])
    
    print("\n✓ Processed single idea\n")


def main():
    """Main function to run examples."""
    print("\nIdeaGraph CoreAgent - Usage Examples\n")
    print("Note: These examples require valid API keys in your .env file\n")
    
    examples = [
        ("Run once", example_run_once),
        ("Custom configuration", example_with_custom_config),
        ("Process specific idea", example_processing_specific_idea)
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nUncomment the example you want to run in this file.\n")
    
    # Uncomment one of these to run the example:
    
    # asyncio.run(example_run_once())
    # asyncio.run(example_with_custom_config())
    # asyncio.run(example_processing_specific_idea())


if __name__ == "__main__":
    main()
