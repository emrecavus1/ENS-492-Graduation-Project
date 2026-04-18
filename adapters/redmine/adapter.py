from __future__ import annotations

from typing import Any, Dict, List, Optional
import requests

from adapters.base import SUTAdapter, TestResult
from adapters.registry import register

import os
import subprocess
from pathlib import Path

from core.coverage_analyzer import CoverageAnalyzer


@register("redmine")
class RedmineAdapter(SUTAdapter):
    def __init__(self, sut_config: Dict[str, Any]):
        super().__init__(sut_config)
        self._root = Path(__file__).resolve().parents[2]
        self._redmine_dir = self._root / "redmine"
        self._coverage_analyzer: Optional[CoverageAnalyzer] = None
    
    @property
    def type_name(self) -> str:
        return "redmine"
    
    @property
    def coverage_analyzer(self) -> CoverageAnalyzer:
        """Lazy-load coverage analyzer."""
        if self._coverage_analyzer is None:
            self._coverage_analyzer = CoverageAnalyzer(self._redmine_dir)
            self._coverage_analyzer.load_coverage()
        return self._coverage_analyzer

    def healthcheck(self) -> bool:
        base_url = self.sut_config["base_url"].rstrip("/")
        url = f"{base_url}/login"
        try:
            r = requests.get(url, timeout=5)
            return r.status_code in (200, 302)
        except requests.RequestException:
            return False

    def get_context_bundle(self) -> Dict[str, Any]:
        context = {
            "app": "Redmine",
            "base_url": self.sut_config["base_url"],
            "domain": "issue tracking",
            "core_entities": ["project", "issue", "user", "wiki", "news", "boards"],
            "auth_method": self.sut_config.get("auth", {}).get("method", "unknown"),
        }
        
        coverage_summary = self.coverage_analyzer.get_coverage_summary()
        if coverage_summary.get("available"):
            context["coverage_summary"] = coverage_summary
            context["priority_controllers"] = [
                c.name for c in self.coverage_analyzer.get_prioritized_controllers(max_count=10)
            ]
        
        return context

    def execute_testcase(self, testcase: Dict[str, Any]) -> TestResult:
        tc_id = testcase.get("id", "UNKNOWN")
        return TestResult(
            testcase_id=tc_id,
            status="skipped",
            details="Execution not implemented yet (adapter stub)."
        )
    
    def collect_coverage(self) -> dict:
        """Collect coverage data with detailed controller breakdown."""
        cov_dir = self._redmine_dir / "coverage"
        index_html = cov_dir / "index.html"
        resultset = cov_dir / ".resultset.json"

        if not cov_dir.exists():
            return {"available": False, "reason": "coverage folder not found"}

        out = {
            "available": True,
            "path": str(cov_dir),
            "index_html_exists": index_html.exists(),
            "resultset_exists": resultset.exists(),
        }

        if resultset.exists():
            self._coverage_analyzer = None
            analyzer = self.coverage_analyzer
            
            summary = analyzer.get_coverage_summary()
            out.update({
                "total_controllers": summary.get("total_controllers", 0),
                "zero_coverage_count": summary.get("zero_coverage_count", 0),
                "well_covered_count": summary.get("well_covered_count", 0),
                "overall_coverage_percent": summary.get("overall_coverage_percent", 0),
            })
            
            priority = analyzer.get_prioritized_controllers(max_count=5)
            out["priority_controllers"] = [
                {
                    "name": c.name,
                    "coverage": c.covered_percent,
                    "lines": c.total_lines,
                    "priority": c.priority_label,
                }
                for c in priority
            ]
            
            zero_cov = analyzer.get_zero_coverage_controllers(min_lines=30)
            out["zero_coverage_controllers"] = [c.name for c in zero_cov[:10]]

        return out

    def run_suite(
        self,
        use_coverage_driven: bool = True,
        focus_controllers: Optional[List[str]] = None,
        test_count: int = 20,
    ) -> dict:
        """
        Run the test generation and execution suite.
        
        Args:
            use_coverage_driven: Use coverage-driven prompt (default: True)
            focus_controllers: List of specific controllers to focus on
            test_count: Number of test blocks to generate
        
        Returns:
            Dict with test results and coverage info
        """
        cmd = ["python", "scripts/generate_tests.py", f"--test-count={test_count}"]
        
        if not use_coverage_driven:
            cmd.append("--full")
        elif focus_controllers:
            cmd.append(f"--focus={','.join(focus_controllers)}")
        
        gen = subprocess.run(
            cmd,
            cwd=str(self._redmine_dir),
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
            ["bundle", "exec", "rails", "test", "test/generated"],
            cwd=str(self._redmine_dir),
            capture_output=True,
            text=True,
            env={**os.environ, "RAILS_ENV": "test", "COVERAGE": "1"},
        )

        return {
            "status": "passed" if run.returncode == 0 else "failed",
            "stage": "rails_test",
            "exit_code": run.returncode,
            "stdout": run.stdout[-4000:],
            "stderr": run.stderr[-4000:],
            "generation_mode": "coverage_driven" if use_coverage_driven else "full",
        }

    def run_iterative_improvement(self, max_iterations: int = 3) -> dict:
        """
        Run multiple iterations of test generation, each focusing on
        controllers that still have low coverage.
        
        Args:
            max_iterations: Maximum number of improvement iterations
        
        Returns:
            Dict with iteration results and final coverage
        """
        iterations = []
        
        for i in range(max_iterations):
            self._coverage_analyzer = None
            analyzer = self.coverage_analyzer
            
            zero_cov = analyzer.get_zero_coverage_controllers(min_lines=30)
            
            if not zero_cov and i > 0:
                break
            
            if i == 0:
                result = self.run_suite(use_coverage_driven=True)
            else:
                focus = [c.name for c in zero_cov[:5]]
                result = self.run_suite(
                    use_coverage_driven=True,
                    focus_controllers=focus,
                    test_count=15,
                )
            
            self._coverage_analyzer = None
            coverage = self.collect_coverage()
            
            iterations.append({
                "iteration": i + 1,
                "test_result": result["status"],
                "coverage_percent": coverage.get("overall_coverage_percent", 0),
                "zero_coverage_remaining": coverage.get("zero_coverage_count", 0),
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
