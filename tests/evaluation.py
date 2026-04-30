"""Evaluation framework with test dataset and metrics."""

from dataclasses import dataclass, field
from typing import list
import json
import time
from app.pipeline.orchestrator import Orchestrator
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TestCase:
    """Single test case."""
    id: str
    category: str 
    prompt: str
    description: str
    expected_features: list[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Result from running a test case."""
    test_id: str
    success: bool
    error: str = None
    repair_attempts: int = 0
    total_time: float = 0.0
    config: dict = None


class EvaluationDataset:
    """Test dataset for evaluation."""
    
    @staticmethod
    def get_production_prompts() -> list[TestCase]:
        """10 real-world product prompts."""
        return [
            TestCase(
                id="prod-001",
                category="production",
                prompt="Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
                description="CRM with multi-tenant support",
                expected_features=["login", "contacts", "dashboard", "roles", "premium", "payments", "analytics"]
            ),
            TestCase(
                id="prod-002",
                category="production",
                prompt="Create an e-commerce platform with product catalog, shopping cart, checkout, order tracking, and email notifications.",
                description="E-commerce platform",
                expected_features=["catalog", "cart", "checkout", "orders", "notifications"]
            ),
            TestCase(
                id="prod-003",
                category="production",
                prompt="Build a project management tool with teams, tasks, timelines, Gantt charts, and real-time collaboration.",
                description="Project management app",
                expected_features=["teams", "tasks", "timelines", "collaboration"]
            ),
            TestCase(
                id="prod-004",
                category="production",
                prompt="Create a booking platform for salons with appointment scheduling, staff management, availability, and customer reviews.",
                description="Salon booking system",
                expected_features=["scheduling", "staff", "availability", "reviews"]
            ),
            TestCase(
                id="prod-005",
                category="production",
                prompt="Build a learning management system with courses, videos, quizzes, progress tracking, and certificates.",
                description="Learning platform",
                expected_features=["courses", "videos", "quizzes", "progress", "certificates"]
            ),
            TestCase(
                id="prod-006",
                category="production",
                prompt="Create a social network with profiles, posts, comments, likes, followers, and messaging.",
                description="Social network",
                expected_features=["profiles", "posts", "comments", "followers", "messaging"]
            ),
            TestCase(
                id="prod-007",
                category="production",
                prompt="Build a restaurant management app with menu management, orders, delivery tracking, and customer loyalty program.",
                description="Restaurant platform",
                expected_features=["menu", "orders", "delivery", "loyalty"]
            ),
            TestCase(
                id="prod-008",
                category="production",
                prompt="Create a fitness app with workouts, progress tracking, nutrition logs, community challenges, and social sharing.",
                description="Fitness tracking app",
                expected_features=["workouts", "tracking", "nutrition", "challenges"]
            ),
            TestCase(
                id="prod-009",
                category="production",
                prompt="Build a real estate platform with property listings, virtual tours, agent profiles, mortgage calculator, and saved favorites.",
                description="Real estate marketplace",
                expected_features=["listings", "tours", "agents", "calculator", "favorites"]
            ),
            TestCase(
                id="prod-010",
                category="production",
                prompt="Create an HR management system with employee profiles, attendance, payroll, leave management, and performance reviews.",
                description="HR management system",
                expected_features=["employees", "attendance", "payroll", "leave", "reviews"]
            ),
        ]
    
    @staticmethod
    def get_edge_cases() -> list[TestCase]:
        """10 edge cases: vague, conflicting, incomplete."""
        return [
            TestCase(
                id="edge-001",
                category="edge_case",
                prompt="Make a website",
                description="Vague: minimal information"
            ),
            TestCase(
                id="edge-002",
                category="edge_case",
                prompt="Build an app that is secure but also fast and cheap and works offline and has AI",
                description="Conflicting: many contradictions"
            ),
            TestCase(
                id="edge-003",
                category="edge_case",
                prompt="Admin dashboard with reports. Premium users get more reports. Free users get basic reports. Only admins can see admin reports.",
                description="Complex role logic"
            ),
            TestCase(
                id="edge-004",
                category="edge_case",
                prompt="API for users and posts and comments. User can create post. User can comment on post. Comment can have replies.",
                description="Incomplete: missing DB design clarity"
            ),
            TestCase(
                id="edge-005",
                category="edge_case",
                prompt="App where users and admins do different things with same data",
                description="Vague: unclear role separation"
            ),
            TestCase(
                id="edge-006",
                category="edge_case",
                prompt="Backend API that serves mobile and web and desktop apps with different auth mechanisms",
                description="Incomplete: multi-platform"
            ),
            TestCase(
                id="edge-007",
                category="edge_case",
                prompt="System must be real-time collaborative and also work offline",
                description="Conflicting requirements"
            ),
            TestCase(
                id="edge-008",
                category="edge_case",
                prompt="Data app with dashboard but no mention of what data",
                description="Vague: missing context"
            ),
            TestCase(
                id="edge-009",
                category="edge_case",
                prompt="Build something for payments and also refunds and chargebacks and fraud detection",
                description="Complex: financial domain"
            ),
            TestCase(
                id="edge-010",
                category="edge_case",
                prompt="Multi-language app that works in 50 countries with local compliance",
                description="Incomplete: massive scope"
            ),
        ]
    
    @staticmethod
    def get_all() -> list[TestCase]:
        """Get all test cases."""
        return EvaluationDataset.get_production_prompts() + EvaluationDataset.get_edge_cases()


class EvaluationRunner:
    """Run evaluation tests and collect metrics."""
    
    def __init__(self):
        self.dataset = EvaluationDataset()
        self.results: list[TestResult] = []
    
    def run_all(self) -> dict:
        """Run all tests."""
        logger.info("=== STARTING EVALUATION ===")
        
        all_tests = self.dataset.get_all()
        
        for test in all_tests:
            logger.info(f"\nRunning test: {test.id} - {test.description}")
            result = self._run_test(test)
            self.results.append(result)
        
        return self.get_summary()
    
    def _run_test(self, test: TestCase) -> TestResult:
        """Run single test case."""
        start_time = time.time()
        
        try:
            orchestrator = Orchestrator(max_repair_attempts=3)
            result = orchestrator.run(test.prompt)
            
            elapsed = time.time() - start_time
            
            if result["success"]:
                return TestResult(
                    test_id=test.id,
                    success=True,
                    repair_attempts=result["metrics"]["repair_attempts"],
                    total_time=elapsed,
                    config=result["config"]
                )
            else:
                return TestResult(
                    test_id=test.id,
                    success=False,
                    error=result["error"],
                    repair_attempts=result["metrics"]["repair_attempts"],
                    total_time=elapsed,
                )
        
        except Exception as e:
            elapsed = time.time() - start_time
            return TestResult(
                test_id=test.id,
                success=False,
                error=str(e),
                total_time=elapsed
            )
    
    def get_summary(self) -> dict:
        """Get evaluation summary."""
        total = len(self.results)
        successes = sum(1 for r in self.results if r.success)
        failures = total - successes
        
        prod_results = [r for r in self.results if r.test_id.startswith("prod-")]
        edge_results = [r for r in self.results if r.test_id.startswith("edge-")]
        
        prod_success = sum(1 for r in prod_results if r.success)
        edge_success = sum(1 for r in edge_results if r.success)
        
        avg_time = sum(r.total_time for r in self.results) / total if total > 0 else 0
        avg_repairs = sum(r.repair_attempts for r in self.results) / total if total > 0 else 0
        
        return {
            "total_tests": total,
            "successes": successes,
            "success_rate": f"{(successes / total * 100):.1f}%" if total > 0 else "0%",
            "failures": failures,
            "production_success_rate": f"{(prod_success / len(prod_results) * 100):.1f}%" if prod_results else "0%",
            "edge_case_success_rate": f"{(edge_success / len(edge_results) * 100):.1f}%" if edge_results else "0%",
            "avg_time_per_test": f"{avg_time:.2f}s",
            "avg_repair_attempts": f"{avg_repairs:.1f}",
            "results": [
                {
                    "test_id": r.test_id,
                    "success": r.success,
                    "error": r.error,
                    "time": f"{r.total_time:.2f}s",
                    "repairs": r.repair_attempts
                }
                for r in self.results
            ]
        }