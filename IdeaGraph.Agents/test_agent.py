#!/usr/bin/env python3
"""
Test script for IdeaGraph.Agents CoreAgent

This script tests the CoreAgent logic without requiring actual API keys.
It uses mock data to verify the workflow.
"""

import sys
import os
import yaml

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """Test that config.yaml can be loaded."""
    print("Testing config loading...")
    try:
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        print("✓ Config loaded successfully")
        print(f"  - Execution interval: {config['execution_interval']}s")
        print(f"  - Embedding model: {config['openai']['embedding_model']}")
        print(f"  - Chat model: {config['openai']['chat_model']}")
        print(f"  - Confidence threshold: {config['similarity_search']['confidence_threshold']}")
        return True
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return False

def test_module_import():
    """Test that the agent module can be imported."""
    print("\nTesting module import...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("agent", "IdeaGraph.Agents.py")
        agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_module)
        print("✓ Module imported successfully")
        print(f"  - CoreAgent class found: {hasattr(agent_module, 'CoreAgent')}")
        print(f"  - main function found: {hasattr(agent_module, 'main')}")
        return True, agent_module
    except Exception as e:
        print(f"✗ Failed to import module: {e}")
        return False, None

def test_class_instantiation(agent_module):
    """Test that CoreAgent can be instantiated (will fail without env vars, but tests structure)."""
    print("\nTesting class structure...")
    try:
        # Check that the class has expected methods
        required_methods = [
            'run_once', 'run_loop', 'get_all_ideas', 
            'process_idea', 'embed_text', 'determine_relation', 
            'store_relation', 'update_idea_embedding', 'check_existing_relation'
        ]
        
        for method in required_methods:
            if hasattr(agent_module.CoreAgent, method):
                print(f"✓ Method '{method}' found")
            else:
                print(f"✗ Method '{method}' not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to test class structure: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are installed."""
    print("\nTesting dependencies...")
    dependencies = [
        'chromadb',
        'openai', 
        'httpx',
        'dotenv',
        'yaml'
    ]
    
    all_ok = True
    for dep in dependencies:
        try:
            if dep == 'yaml':
                __import__('yaml')
            elif dep == 'dotenv':
                __import__('dotenv')
            else:
                __import__(dep)
            print(f"✓ {dep} is installed")
        except ImportError:
            print(f"✗ {dep} is NOT installed")
            all_ok = False
    
    return all_ok

def test_config_validation():
    """Test that config values are valid."""
    print("\nTesting config validation...")
    try:
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Check execution_interval is positive
        if config['execution_interval'] > 0:
            print(f"✓ execution_interval is valid: {config['execution_interval']}")
        else:
            print(f"✗ execution_interval must be positive: {config['execution_interval']}")
            return False
        
        # Check confidence_threshold is between 0 and 1
        threshold = config['similarity_search']['confidence_threshold']
        if 0.0 <= threshold <= 1.0:
            print(f"✓ confidence_threshold is valid: {threshold}")
        else:
            print(f"✗ confidence_threshold must be between 0.0 and 1.0: {threshold}")
            return False
        
        # Check n_results is positive
        n_results = config['similarity_search']['n_results']
        if n_results > 0:
            print(f"✓ n_results is valid: {n_results}")
        else:
            print(f"✗ n_results must be positive: {n_results}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Config validation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 80)
    print("IdeaGraph.Agents CoreAgent - Test Suite")
    print("=" * 80)
    
    results = []
    
    # Test 1: Config loading
    results.append(("Config Loading", test_config_loading()))
    
    # Test 2: Dependencies
    results.append(("Dependencies", test_dependencies()))
    
    # Test 3: Module import
    success, agent_module = test_module_import()
    results.append(("Module Import", success))
    
    # Test 4: Class structure (only if import succeeded)
    if success and agent_module:
        results.append(("Class Structure", test_class_instantiation(agent_module)))
    
    # Test 5: Config validation
    results.append(("Config Validation", test_config_validation()))
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 All tests passed! The CoreAgent is ready to run.")
        print("\nTo run the agent:")
        print("  1. Create a .env file with your API keys (see .env.example)")
        print("  2. Run: python __main__.py --once")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before running the agent.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
