from __future__ import annotations

from typing import Any, Dict, List, Optional
import requests
import subprocess
import os
from pathlib import Path

from adapters.base import SUTAdapter, TestResult
from adapters.registry import register

from core.taiga_coverage_analyzer import TaigaCoverageAnalyzer


@register("taiga")
class TaigaAdapter(SUTAdapter):
    """
    Adapter for Taiga project management application.
    Taiga uses Django/Python with Django REST Framework.
    """
    
    def __init__(self, sut_config: Dict[str, Any]):
        super().__init__(sut_config)
        self._root = Path(__file__).resolve().parents[2]
        self._taiga_dir = self._root / "taiga"
        self._coverage_analyzer: Optional[TaigaCoverageAnalyzer] = None
        self._auth_token: Optional[str] = None

    @property
    def type_name(self) -> str:
        return "taiga"
    
    @property
    def coverage_analyzer(self) -> TaigaCoverageAnalyzer:
        """Lazy-load coverage analyzer."""
        if self._coverage_analyzer is None:
            self._coverage_analyzer = TaigaCoverageAnalyzer(self._taiga_dir)
            self._coverage_analyzer.load_coverage()
        return self._coverage_analyzer

    def _get_auth_token(self) -> Optional[str]:
        """Get JWT auth token from Taiga."""
        if self._auth_token:
            return self._auth_token
        
        try:
            auth_config = self.sut_config.get("auth", {})
            credentials = auth_config.get("credentials", {})
            
            response = requests.post(
                f"{self.sut_config['api_base']}/auth",
                json={
                    "username": credentials.get("username", "admin"),
                    "password": credentials.get("password", "123123"),
                    "type": "normal",
                },
                timeout=10,
            )
            
            if response.status_code == 200:
                self._auth_token = response.json().get("auth_token")
                return self._auth_token
        except requests.RequestException:
            pass
        
        return None

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        token = self._get_auth_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def healthcheck(self) -> bool:
        """Check if Taiga API is reachable."""
        api_base = self.sut_config.get("api_base", "http://localhost:9000/api/v1")
        try:
            response = requests.get(f"{api_base}/", timeout=5)
            return response.status_code in (200, 301, 302, 404)
        except requests.RequestException:
            return False

    def get_context_bundle(self) -> Dict[str, Any]:
        """Provide app-specific context for test generation."""
        context = {
            "app": "Taiga",
            "base_url": self.sut_config.get("base_url", "http://localhost:9000"),
            "api_base": self.sut_config.get("api_base", "http://localhost:9000/api/v1"),
            "domain": "project management",
            "core_entities": ["project", "userstory", "task", "issue", "milestone", "wiki"],
            "auth_method": "jwt",
            "test_framework": "pytest",
        }
        
        coverage_summary = self.coverage_analyzer.get_coverage_summary()
        if coverage_summary.get("available"):
            context["coverage_summary"] = coverage_summary
            context["priority_viewsets"] = [
                v.name for v in self.coverage_analyzer.get_prioritized_viewsets(max_count=5)
            ]
        
        return context

    def execute_testcase(self, testcase: Dict[str, Any]) -> TestResult:
        """Execute a single test case."""
        return TestResult(
            testcase_id=testcase.get("id", "UNKNOWN"),
            status="skipped",
            details="TaigaAdapter currently runs in suite mode."
        )

    def collect_coverage(self) -> dict:
        """Collect coverage data with detailed ViewSet breakdown."""
        self._coverage_analyzer = None
        analyzer = self.coverage_analyzer
        
        cov_file = self._taiga_dir / "coverage" / "coverage.json"
        
        if not cov_file.exists():
            return {"available": False, "reason": "coverage.json not found"}
        
        summary = analyzer.get_coverage_summary()
        priority = analyzer.get_prioritized_viewsets(max_count=5)
        
        return {
            "available": True,
            "type": "python_coverage",
            "path": str(cov_file),
            "total_viewsets": summary.get("total_viewsets", 0),
            "zero_coverage_count": summary.get("zero_coverage_count", 0),
            "well_covered_count": summary.get("well_covered_count", 0),
            "overall_coverage_percent": summary.get("overall_coverage_percent", 0),
            "priority_viewsets": [
                {
                    "name": v.name,
                    "coverage": v.covered_percent,
                    "lines": v.total_lines,
                    "priority": v.priority_label,
                }
                for v in priority
            ],
        }

    def run_suite(
        self,
        use_coverage_driven: bool = True,
        focus_viewsets: Optional[List[str]] = None,
        test_count: int = 20,
    ) -> dict:
        """
        Run the test generation and execution suite.
        """
        cmd = ["python", "scripts/generate_tests.py", f"--test-count={test_count}"]
        
        if not use_coverage_driven:
            cmd.append("--full")
        elif focus_viewsets:
            cmd.append(f"--focus={','.join(focus_viewsets)}")
        
        gen = subprocess.run(
            cmd,
            cwd=str(self._taiga_dir),
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
            cwd=str(self._taiga_dir),
            capture_output=True,
            text=True,
        )

        return {
            "status": "passed" if run.returncode == 0 else "failed",
            "stage": "pytest",
            "exit_code": run.returncode,
            "stdout": run.stdout[-4000:],
            "stderr": run.stderr[-4000:],
            "generation_mode": "coverage_driven" if use_coverage_driven else "full",
        }

    def run_coverage_in_docker(self) -> dict:
        """
        Run coverage collection inside the Taiga Docker container.
        This requires the taiga-docker setup to be running.
        """
        docker_config = self.sut_config.get("docker", {})
        container = docker_config.get("backend_container", "taiga-docker-taiga-back-1")
        
        commands = [
            "coverage run --source='taiga' manage.py test --noinput",
            "coverage json -o /taiga-back/coverage.json",
        ]
        
        results = []
        for cmd in commands:
            result = subprocess.run(
                ["docker", "exec", container, "bash", "-c", cmd],
                capture_output=True,
                text=True,
            )
            results.append({
                "command": cmd,
                "exit_code": result.returncode,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-1000:],
            })
            
            if result.returncode != 0:
                return {
                    "status": "error",
                    "stage": cmd,
                    "results": results,
                }
        
        copy_result = subprocess.run(
            ["docker", "cp", f"{container}:/taiga-back/coverage.json", 
             str(self._taiga_dir / "coverage" / "coverage.json")],
            capture_output=True,
            text=True,
        )
        
        return {
            "status": "passed" if copy_result.returncode == 0 else "failed",
            "results": results,
            "coverage_path": str(self._taiga_dir / "coverage" / "coverage.json"),
        }

    def run_iterative_improvement(self, max_iterations: int = 3) -> dict:
        """
        Run multiple iterations of test generation, each focusing on
        ViewSets that still have low coverage.
        """
        iterations = []
        
        for i in range(max_iterations):
            self._coverage_analyzer = None
            analyzer = self.coverage_analyzer
            
            zero_cov = analyzer.get_zero_coverage_viewsets(min_lines=20)
            
            if not zero_cov and i > 0:
                break
            
            if i == 0:
                result = self.run_suite(use_coverage_driven=True)
            else:
                focus = [self._map_viewset_name(v.name) for v in zero_cov[:5]]
                focus = [f for f in focus if f]
                result = self.run_suite(
                    use_coverage_driven=True,
                    focus_viewsets=focus,
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

    def _map_viewset_name(self, module_name: str) -> Optional[str]:
        """Map module name to ViewSet key."""
        name_lower = module_name.lower()
        
        mapping = {
            "projects": ["project"],
            "userstories": ["userstory", "user_story"],
            "tasks": ["task"],
            "issues": ["issue"],
            "milestones": ["milestone"],
            "users": ["user"],
        }
        
        for key, patterns in mapping.items():
            if any(p in name_lower for p in patterns):
                return key
        return None

    def print_coverage_report(self) -> None:
        """Print human-readable coverage report."""
        self.coverage_analyzer.print_report()
