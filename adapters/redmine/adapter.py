from __future__ import annotations

from typing import Any, Dict
import requests

from adapters.base import SUTAdapter, TestResult
from adapters.registry import register

import os
import subprocess
from pathlib import Path

@register("redmine")
class RedmineAdapter(SUTAdapter):
    @property
    def type_name(self) -> str:
        return "redmine"

    def healthcheck(self) -> bool:
        base_url = self.sut_config["base_url"].rstrip("/")
        # Redmine has /login; checking it is a simple "is server up?" test
        url = f"{base_url}/login"
        try:
            r = requests.get(url, timeout=5)
            return r.status_code in (200, 302)
        except requests.RequestException:
            return False

    def get_context_bundle(self) -> Dict[str, Any]:
        # Later you can parse OpenAPI + manual here; for now keep it minimal.
        return {
            "app": "Redmine",
            "base_url": self.sut_config["base_url"],
            "domain": "issue tracking",
            "core_entities": ["project", "issue", "user", "wiki", "news", "boards"],
            "auth_method": self.sut_config.get("auth", {}).get("method", "unknown"),
        }

    def execute_testcase(self, testcase: Dict[str, Any]) -> TestResult:
        # Stub execution for now (so pipeline works end-to-end).
        # Later: implement UI (Playwright) or API calls.
        tc_id = testcase.get("id", "UNKNOWN")
        return TestResult(
            testcase_id=tc_id,
            status="skipped",
            details="Execution not implemented yet (adapter stub)."
        )
    
    def collect_coverage(self) -> dict:
        root = Path(__file__).resolve().parents[2]
        cov_dir = root / "redmine" / "coverage"
        index_html = cov_dir / "index.html"
        resultset = cov_dir / ".resultset.json"

        if not cov_dir.exists():
            return {"available": False, "reason": "coverage folder not found"}

        out = {"available": True, "path": str(cov_dir)}
        out["index_html_exists"] = index_html.exists()
        out["resultset_exists"] = resultset.exists()

        # Optional: parse resultset JSON to extract exact % (if SimpleCov is used)
        if resultset.exists():
            try:
                import json
                data = json.loads(resultset.read_text(encoding="utf-8"))
                # SimpleCov structure varies; often "result" has "covered_percent"
                # We'll be defensive:
                # Find any dict containing 'covered_percent'
                covered = None
                def walk(x):
                    nonlocal covered
                    if isinstance(x, dict):
                        if "covered_percent" in x and isinstance(x["covered_percent"], (int, float)):
                            covered = x["covered_percent"]
                            return
                        for v in x.values():
                            if covered is None:
                                walk(v)
                    elif isinstance(x, list):
                        for v in x:
                            if covered is None:
                                walk(v)
                walk(data)
                if covered is not None:
                    out["covered_percent"] = round(float(covered), 2)
            except Exception as e:
                out["parse_error"] = str(e)

        return out


    def run_suite(self) -> dict:
        root = Path(__file__).resolve().parents[2]   # project root
        redmine_dir = root / "redmine"

        # 1) Generate Ruby tests
        gen = subprocess.run(
            ["python", "scripts/generate_tests.py"],
            cwd=str(redmine_dir),
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

        # 2) Run Ruby test suite (generated tests)
        run = subprocess.run(
            ["bundle", "exec", "rails", "test", "test/generated"],
            cwd=str(redmine_dir),
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
        }