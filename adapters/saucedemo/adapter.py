from __future__ import annotations
from typing import Any, Dict, List, Optional
from adapters.base import SUTAdapter, TestResult
from adapters.registry import register

from playwright.sync_api import sync_playwright
import subprocess
import time
import os
from pathlib import Path

from core.saucedemo_coverage_analyzer import SauceDemoCoverageAnalyzer


@register("saucedemo")
class SauceDemoAdapter(SUTAdapter):
    def __init__(self, sut_config: Dict[str, Any]):
        super().__init__(sut_config)
        self._visited_pages = set()
        self._root = Path(__file__).resolve().parents[2]
        self._saucedemo_dir = self._root / "saucedemo"
        self._coverage_analyzer: Optional[SauceDemoCoverageAnalyzer] = None

    @property
    def type_name(self) -> str:
        return "saucedemo"

    @property
    def coverage_analyzer(self) -> SauceDemoCoverageAnalyzer:
        """Lazy-load coverage analyzer."""
        if self._coverage_analyzer is None:
            self._coverage_analyzer = SauceDemoCoverageAnalyzer(self._saucedemo_dir)
            self._coverage_analyzer.load_coverage()
        return self._coverage_analyzer

    def _mark_page(self, page_name: str) -> None:
        self._visited_pages.add(page_name)
        self.coverage_analyzer.mark_page_visited(page_name)

    def healthcheck(self) -> bool:
        base_url = self.sut_config["base_url"].rstrip("/")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(base_url, wait_until="domcontentloaded", timeout=15000)
                browser.close()
            return True
        except Exception:
            return False

    def get_context_bundle(self) -> Dict[str, Any]:
        """Provide app-specific context for test generation."""
        context = {
            "app": "SauceDemo",
            "base_url": self.sut_config["base_url"],
            "domain": "e-commerce demo",
            "core_entities": ["product", "cart", "checkout", "user"],
            "auth_method": self.sut_config.get("auth", {}).get("method", "form"),
            "test_framework": "playwright",
        }
        
        coverage_summary = self.coverage_analyzer.get_coverage_summary()
        if coverage_summary.get("available"):
            context["coverage_summary"] = coverage_summary
            context["priority_flows"] = [
                f.flow.name for f in self.coverage_analyzer.get_priority_flows(max_count=5)
            ]
        
        return context

    def execute_testcase(self, testcase: Dict[str, Any]) -> TestResult:
        return TestResult(
            testcase_id=testcase.get("id", "UNKNOWN"),
            status="skipped",
            details="SauceDemoAdapter currently runs in suite mode."
        )

    def collect_coverage(self) -> dict:
        """Collect coverage data with detailed page and flow breakdown."""
        self._coverage_analyzer = None
        analyzer = self.coverage_analyzer
        
        summary = analyzer.get_coverage_summary()
        
        priority_flows = analyzer.get_priority_flows(max_count=5)
        
        return {
            "available": True,
            "type": "ui_page_coverage",
            "total_pages": summary.get("total_pages", 0),
            "covered_pages": summary.get("covered_pages", 0),
            "page_coverage_percent": summary.get("page_coverage_percent", 0),
            "uncovered_pages": summary.get("uncovered_pages", []),
            "total_flows": summary.get("total_flows", 0),
            "fully_covered_flows": summary.get("fully_covered_flows", 0),
            "flow_coverage_percent": summary.get("flow_coverage_percent", 0),
            "priority_flows": [
                {
                    "name": f.flow.name,
                    "priority": f.flow.priority,
                    "coverage": f.coverage_percent,
                    "label": f.priority_label,
                }
                for f in priority_flows
            ],
        }

    def run_suite(
        self,
        use_coverage_driven: bool = True,
        focus_flows: Optional[List[str]] = None,
        test_count: int = 15,
    ) -> dict:
        """
        Run the test generation and execution suite.
        
        Args:
            use_coverage_driven: Use coverage-driven prompt (default: True)
            focus_flows: List of specific flows to focus on
            test_count: Number of test functions to generate
        
        Returns:
            Dict with test results and coverage info
        """
        cmd = ["python", "scripts/generate_tests.py", f"--test-count={test_count}"]
        
        if not use_coverage_driven:
            cmd.append("--full")
        elif focus_flows:
            cmd.append(f"--focus={','.join(focus_flows)}")
        
        gen = subprocess.run(
            cmd,
            cwd=str(self._saucedemo_dir),
            capture_output=True,
            text=True,
        )

        if gen.returncode != 0:
            return {
                "status": "error",
                "stage": "generate_tests",
                "stdout": gen.stdout[-2000:],
                "stderr": gen.stderr[-2000:],
            }

        run = subprocess.run(
            ["python", "-m", "pytest", "tests/generated/", "-v"],
            cwd=str(self._saucedemo_dir),
            capture_output=True,
            text=True,
        )

        self._save_coverage_from_run()

        return {
            "status": "passed" if run.returncode == 0 else "failed",
            "stage": "pytest",
            "exit_code": run.returncode,
            "stdout": run.stdout[-4000:],
            "stderr": run.stderr[-4000:],
            "generation_mode": "coverage_driven" if use_coverage_driven else "full",
        }

    def run_builtin_suite(self) -> dict:
        """Run the built-in hardcoded test suite (original behavior)."""
        start = time.time()
        base_url = self.sut_config["base_url"].rstrip("/")
        username = self.sut_config["auth"]["user"]["username"]
        password = self.sut_config["auth"]["user"]["password"]

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(base_url, wait_until="domcontentloaded", timeout=15000)
                self._mark_page("login")

                page.locator("#user-name").fill(username)
                page.locator("#password").fill(password)
                page.locator("#login-button").click()
                page.wait_for_url("**/inventory.html", timeout=15000)
                self._mark_page("inventory")

                page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
                page.locator(".shopping_cart_link").click()
                page.wait_for_url("**/cart.html", timeout=15000)
                self._mark_page("cart")

                page.locator('[data-test="checkout"]').click()
                page.wait_for_url("**/checkout-step-one.html", timeout=15000)
                self._mark_page("checkout_step_one")

                page.goto(base_url, wait_until="domcontentloaded", timeout=15000)
                self._mark_page("login")

                page.locator("#user-name").fill("invalid_user")
                page.locator("#password").fill("wrong_password")
                page.locator("#login-button").click()

                browser.close()

            self._save_coverage_from_run()

            return {"status": "passed", "details": "Suite passed.", "duration_s": round(time.time()-start, 3)}
        except Exception as e:
            return {"status": "error", "details": str(e)}

    def _save_coverage_from_run(self) -> None:
        """Save current coverage state to JSON file."""
        self.coverage_analyzer.set_visited_pages(self._visited_pages)
        self.coverage_analyzer.save_coverage()

    def run_iterative_improvement(self, max_iterations: int = 3) -> dict:
        """
        Run multiple iterations of test generation, each focusing on
        flows that still have low coverage.
        """
        iterations = []
        
        for i in range(max_iterations):
            self._coverage_analyzer = None
            analyzer = self.coverage_analyzer
            
            priority_flows = analyzer.get_priority_flows(max_count=5)
            uncovered = [f for f in priority_flows if f.coverage_percent < 50]
            
            if not uncovered and i > 0:
                break
            
            if i == 0:
                result = self.run_suite(use_coverage_driven=True)
            else:
                focus = [f.flow.name for f in uncovered[:3]]
                result = self.run_suite(
                    use_coverage_driven=True,
                    focus_flows=focus,
                    test_count=10,
                )
            
            self._coverage_analyzer = None
            coverage = self.collect_coverage()
            
            iterations.append({
                "iteration": i + 1,
                "test_result": result["status"],
                "page_coverage_percent": coverage.get("page_coverage_percent", 0),
                "flow_coverage_percent": coverage.get("flow_coverage_percent", 0),
            })
            
            if result["status"] == "error":
                break
        
        return {
            "iterations": iterations,
            "final_coverage": self.collect_coverage(),
        }

    def print_coverage_report(self) -> None:
        """Print human-readable coverage report."""
        self.coverage_analyzer.print_report()
