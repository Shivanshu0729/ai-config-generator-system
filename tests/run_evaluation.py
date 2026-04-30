"""Evaluation runner - execute tests and report results."""

import json
import sys
from tests.evaluation import EvaluationRunner
from app.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Run full evaluation and print results."""
    try:
        runner = EvaluationRunner()
        summary = runner.run_all()
        
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80)
        
        print(f"\nTotal Tests: {summary['total_tests']}")
        print(f"Successes: {summary['successes']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Failures: {summary['failures']}")
        
        print(f"\nProduction Success Rate: {summary['production_success_rate']}")
        print(f"Edge Case Success Rate: {summary['edge_case_success_rate']}")
        
        print(f"\nAvg Time per Test: {summary['avg_time_per_test']}")
        print(f"Avg Repair Attempts: {summary['avg_repair_attempts']}")
        
        print("\n" + "-"*80)
        print("DETAILED RESULTS")
        print("-"*80)
        
        for result in summary['results']:
            status = "✓ PASS" if result['success'] else "✗ FAIL"
            print(f"{result['test_id']}: {status} ({result['time']}, repairs: {result['repairs']})")
            if result['error']:
                print(f"  Error: {result['error'][:80]}")
        
        print("\n" + "="*80)
        
        with open("evaluation_results.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        logger.info("Evaluation results saved to evaluation_results.json")
        
        return 0 if summary['successes'] >= summary['total_tests'] * 0.7 else 1
    
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
