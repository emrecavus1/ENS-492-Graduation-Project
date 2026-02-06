from __future__ import annotations

from typing import Any, Dict, List
import yaml

from adapters.registry import get_adapter
import adapters.redmine.adapter  # noqa: F401
import adapters.saucedemo.adapter  # noqa: F401


from core.schema import TestCase


def load_sut_config(sut_path: str) -> Dict[str, Any]:
    with open(sut_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_smoke_tests(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Placeholder generator.
    Replace this with your LLM generation logic later.
    """
    tc = TestCase(
        id="TC_SMOKE_001",
        title=f"Smoke: open login page ({context.get('app','SUT')})",
        steps=[f"Open {context['base_url'].rstrip('/')}/login"],
        expected_results=["Login page loads successfully"],
        tags=["smoke"],
        priority="high",
    )
    return [tc.to_dict()]


def run_pipeline(sut_path: str) -> Dict[str, Any]:
    sut_config = load_sut_config(sut_path)

    adapter_type = sut_config["type"]
    AdapterCls = get_adapter(adapter_type)
    adapter = AdapterCls(sut_config)

    ok = adapter.healthcheck()
    if not ok:
        raise RuntimeError(f"SUT healthcheck failed for type={adapter_type}")

    # ✅ NEW: if the adapter supports suite mode, run it and return immediately
    run_suite = getattr(adapter, "run_suite", None)
    if callable(run_suite):
        suite_result = run_suite()

        collect_cov = getattr(adapter, "collect_coverage", None)
        coverage = collect_cov() if callable(collect_cov) else {"available": False}

        return {
            "sut_type": adapter_type,
            "sut_name": adapter.name,
            "suite": suite_result,
            "coverage": coverage,
        }


    # Fallback: placeholder per-testcase flow (works for adapters without suite runner)
    context = adapter.get_context_bundle()
    tests = generate_smoke_tests(context)

    results = []
    for tc in tests:
        results.append(adapter.execute_testcase(tc).__dict__)

    return {
        "sut_type": adapter_type,
        "sut_name": adapter.name,
        "tests": tests,
        "results": results,
    }

