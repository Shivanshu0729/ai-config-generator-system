"""Debug script to test the generate endpoint directly."""

import sys
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

try:
    print("Testing imports...")
    from app.pipeline.orchestrator import Orchestrator
    print("✓ Orchestrator imported")
    
    from app.routes.generate import GenerateRequest, GenerateResponse
    print("✓ GenerateRequest and GenerateResponse imported")
    
    print("\nInitializing Orchestrator...")
    orchestrator = Orchestrator(max_repair_attempts=3)
    print("✓ Orchestrator initialized")
    
    print("\nRunning orchestrator with test prompt...")
    result = orchestrator.run("build a gym website")
    print(f"✓ Orchestrator ran successfully")
    print(f"Result: {result}")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All tests passed!")
