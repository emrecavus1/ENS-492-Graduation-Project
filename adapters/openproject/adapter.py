from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import os
import subprocess

import requests

from adapters.base import SUTAdapter, TestResult
from adapters.registry import register
from core.openproject_coverage_analyzer import OpenProjectCoverageAnalyzer


@register("openproject")
class OpenProjectAdapter(SUTAdapter):
    def __init__(self, sut_config: Dict[str, Any]):
        super().__init__(sut_config)
        self._root = Path(__file__).resolve().parents[2]
        project_dir = self.sut_config.get("project_dir")
        if project_dir:
            self._openproject_dir = (self._root / project_dir).resolve()
        elif (self._root / "openproject_clean").exists():
            self._openproject_dir = self._root / "openproject_clean"
        else:
            self._openproject_dir = self._root / "openproject"
        self._coverage_analyzer: Optional[OpenProjectCoverageAnalyzer] = None

    @property
    def type_name(self) -> str:
        return "openproject"

    @property
    def coverage_analyzer(self) -> OpenProjectCoverageAnalyzer:
        if self._coverage_analyzer is None:
            self._coverage_analyzer = OpenProjectCoverageAnalyzer(self._openproject_dir)
            self._coverage_analyzer.load_coverage()
        return self._coverage_analyzer

    def healthcheck(self) -> bool:
        base_url = self.sut_config.get("base_url", "http://localhost:3000").rstrip("/")
        try:
            response = requests.get(f"{base_url}/signin", timeout=5)
            return response.status_code in (200, 301, 302, 401, 403)
        except requests.RequestException:
            return False

    def get_context_bundle(self) -> Dict[str, Any]:
        context = {
            "app": "OpenProject",
            "base_url": self.sut_config.get("base_url", "http://localhost:3000"),
            "domain": "project management",
            "core_entities": ["project", "work_package", "user", "status"],
            "auth_method": self.sut_config.get("auth", {}).get("method", "session"),
            "test_framework": "rspec",
        }

        summary = self.coverage_analyzer.get_summary()
        if summary.get("available"):
            context["coverage_summary"] = summary
            context["priority_files"] = [
                item.file_path for item in self.coverage_analyzer.get_prioritized_files(max_count=8)
            ]
        return context

    def execute_testcase(self, testcase: Dict[str, Any]) -> TestResult:
        return TestResult(
            testcase_id=testcase.get("id", "UNKNOWN"),
            status="skipped",
            details="OpenProjectAdapter currently runs in suite mode.",
        )

    def collect_coverage(self) -> Dict[str, Any]:
        self._coverage_analyzer = None
        analyzer = self.coverage_analyzer
        summary = analyzer.get_summary()
        if not summary.get("available"):
            return {"available": False, "reason": "coverage/.resultset.json not found or empty"}

        priority = analyzer.get_prioritized_files(max_count=10)
        return {
            "available": True,
            "type": "simplecov",
            "path": str(self._openproject_dir / "coverage" / ".resultset.json"),
            **summary,
            "priority_files": [
                {
                    "file_path": item.file_path,
                    "category": item.category,
                    "coverage": item.covered_percent,
                    "lines": item.total_lines,
                    "priority": item.priority_label,
                }
                for item in priority
            ],
        }

    def run_suite(
        self,
        include_auth_tests: bool = True,
        focus_resources: Optional[List[str]] = None,
        test_count: int = 24,
    ) -> Dict[str, Any]:
        cmd = ["python", "scripts/generate_tests.py", f"--test-count={test_count}"]

        if not include_auth_tests:
            cmd.append("--no-auth")
        if focus_resources:
            cmd.append(f"--focus={','.join(focus_resources)}")

        generation = subprocess.run(
            cmd,
            cwd=str(self._openproject_dir),
            capture_output=True,
            text=True,
        )
        if generation.returncode != 0:
            return {
                "status": "error",
                "stage": "generate_tests",
                "stdout": generation.stdout[-3000:],
                "stderr": generation.stderr[-3000:],
            }

        run = subprocess.run(
            ["bundle", "exec", "rspec", "spec/generated/openproject_generated_request_spec.rb"],
            cwd=str(self._openproject_dir),
            capture_output=True,
            text=True,
            env={**os.environ, "RAILS_ENV": "test", "COVERAGE": "1"},
        )

        return {
            "status": "passed" if run.returncode == 0 else "failed",
            "stage": "rspec",
            "exit_code": run.returncode,
            "stdout": run.stdout[-5000:],
            "stderr": run.stderr[-5000:],
        }

    def run_iterative_improvement(
        self,
        iterations: int = 3,
        test_count: int = 20,
        focus_coverage_threshold: float = 80.0,
    ) -> Dict[str, Any]:
        """
        Run iterative generation/test loop for OpenProject.
        """
        cmd = [
            "python",
            "scripts/generate_tests.py",
            "--iterative",
            "--run-tests",
            f"--iterations={iterations}",
            f"--test-count={test_count}",
            f"--focus-coverage-threshold={focus_coverage_threshold}",
        ]
        result = subprocess.run(
            cmd,
            cwd=str(self._openproject_dir),
            capture_output=True,
            text=True,
            env={**os.environ, "RAILS_ENV": "test", "COVERAGE": "1"},
        )

        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "stage": "iterative_generate_and_test",
            "exit_code": result.returncode,
            "stdout": result.stdout[-6000:],
            "stderr": result.stderr[-6000:],
            "final_coverage": self.collect_coverage(),
        }
