"""Demo script to test validation with a realistic website prompt."""

import json
import os

from app.pipeline.orchestrator import run_pipeline

# Example prompt for building a website
EXAMPLE_PROMPTS = [
    "Build an e-commerce website with product catalog, shopping cart, and user authentication",
    "Create a project management tool with tasks, teams, and real-time collaboration features",
    "Build a social media platform with user profiles, posts, comments, and messaging",
]

def test_validation_with_prompt(prompt: str):
    """Run the pipeline with a prompt and show validation results."""
    print(f"\n{'='*80}")
    print(f"Testing with prompt: {prompt}")
    print(f"{'='*80}\n")

    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY environment variable not set")
        print("   Set it to run the full pipeline demo, or use the unit tests in test/test_validator.py for validation-only checks.")
        return
    
    try:
        result = run_pipeline(prompt, max_repair_attempts=3)
        
        if result.get("success"):
            print("✅ VALIDATION PASSED!\n")
            config = result.get("config", {})
            print(f"App Name: {config.get('app_name')}")
            print(f"Description: {config.get('app_description')}")
            print(f"Entities: {list(config.get('entities', {}).keys())}")
            print(f"\nMetrics:")
            metrics = result.get("metrics", {})
            print(f"  Success: {metrics.get('success')}")
            print(f"  Repair Attempts: {metrics.get('repair_attempts')}")
            print(f"  Total Time: {metrics.get('total_time', 0):.2f}s")
            
            print(f"\nFull Config (JSON):")
            print(json.dumps(config, indent=2))
        else:
            print("❌ VALIDATION FAILED\n")
            print(f"Error: {result.get('error')}")
            metrics = result.get("metrics", {})
            print(f"\nMetrics:")
            print(f"  Success: {metrics.get('success')}")
            print(f"  Repair Attempts: {metrics.get('repair_attempts')}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test with one of the example prompts
    prompt = EXAMPLE_PROMPTS[0]  # Change index to test different prompts (0, 1, or 2)
    test_validation_with_prompt(prompt)
    
    print(f"\n\n{'='*80}")
    print("OTHER EXAMPLE PROMPTS TO TRY:")
    print(f"{'='*80}")
    for i, p in enumerate(EXAMPLE_PROMPTS, 1):
        print(f"\n{i}. {p}")
