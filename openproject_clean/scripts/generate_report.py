#!/usr/bin/env python3
"""
Comprehensive Test Generation Report for OpenProject

Reports:
1. Coverage statistics from SimpleCov
2. Endpoint/resource documentation
3. Generated test analysis
4. Coverage gaps by resource
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OPENPROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))

from core.openproject_route_mapper import OPENPROJECT_RESOURCES, get_statistics, get_coverage_target_patterns
from core.openproject_coverage_analyzer import OpenProjectCoverageAnalyzer


@dataclass
class TestCaseInfo:
    name: str
    endpoint: str
    method: str
    resource: str
    requires_auth: bool


@dataclass
class ResourceCoverage:
    name: str
    total_endpoints: int
    tested_endpoints: int
    covered_percent: float
    auth_required: int
    safe_endpoints: int


@dataclass
class UncoveredReason:
    resource: str
    reason: str
    priority: str


def parse_coverage_file(coverage_path: Path) -> Dict[str, Any]:
    if not coverage_path.exists():
        return {}

    try:
        return json.loads(coverage_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def calculate_coverage_stats(coverage_data: Dict[str, Any]) -> Dict[str, Any]:
    if not coverage_data:
        return {
            "available": False,
            "total_lines": 0,
            "covered_lines": 0,
            "coverage_percent": 0.0,
        }

    total_lines = 0
    covered_lines = 0

    for suite_data in coverage_data.values():
        if not isinstance(suite_data, dict) or "coverage" not in suite_data:
            continue

        for _, file_data in suite_data["coverage"].items():
            lines = file_data.get("lines", []) if isinstance(file_data, dict) else file_data
            for line in lines:
                if line is not None:
                    total_lines += 1
                    if line > 0:
                        covered_lines += 1

    return {
        "available": total_lines > 0,
        "total_lines": total_lines,
        "covered_lines": covered_lines,
        "coverage_percent": (covered_lines / total_lines * 100) if total_lines > 0 else 0.0,
    }


def _guess_resource_from_endpoint(endpoint: str) -> str:
    # Prefer the longest matching base path first (e.g. /api/v3/projects
    # should map to api_v3_projects, not api_v3_root).
    candidates = sorted(
        OPENPROJECT_RESOURCES.items(),
        key=lambda item: len(item[1].base_path.rstrip("/")),
        reverse=True,
    )
    for name, resource in candidates:
        base = resource.base_path.rstrip("/")
        if base and endpoint.startswith(base):
            return name
    return "unknown"


def parse_generated_tests(test_file: Path) -> List[TestCaseInfo]:
    tests: List[TestCaseInfo] = []
    if not test_file.exists():
        return tests

    content = test_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    current_resource = "unknown"
    current_describe_method = ""
    current_describe_endpoint = "unknown"
    for idx, line in enumerate(lines):
        desc = re.search(r'describe\s+["\']([^"\']+)["\']', line)
        if desc:
            desc_text = desc.group(1).strip()
            slug = desc_text.lower().replace(" ", "_")
            if slug in OPENPROJECT_RESOURCES:
                current_resource = slug
            describe_method, describe_endpoint = _extract_method_and_endpoint_from_describe(desc_text)
            if describe_method and describe_endpoint:
                current_describe_method = describe_method
                current_describe_endpoint = describe_endpoint

        it_match = re.search(r'it\s+["\']([^"\']+)["\']', line)
        if not it_match:
            continue

        test_name = it_match.group(1)
        method = current_describe_method or "GET"
        endpoint = current_describe_endpoint
        requires_auth = False

        name_method, name_endpoint = _extract_method_and_endpoint_from_test_name(test_name)
        if name_method and name_endpoint:
            method = name_method
            endpoint = name_endpoint

        for j in range(idx, min(idx + 12, len(lines))):
            call_line = lines[j].strip()
            for verb in ("get", "post", "patch", "delete", "put"):
                if endpoint != "unknown":
                    # We already have canonical endpoint from test name.
                    break
                if re.search(rf"\b{verb}\s+['\"]", call_line):
                    method = verb.upper()
                    endpoint_match = re.search(rf"{verb}\s+['\"]([^'\"]+)['\"]", call_line)
                    endpoint = _normalize_runtime_endpoint(endpoint_match.group(1)) if endpoint_match else endpoint
            if "current_user" in call_line or "Authorization" in call_line:
                requires_auth = True

        guessed_resource = _guess_resource_from_endpoint(endpoint)
        resource = guessed_resource if guessed_resource != "unknown" else current_resource

        tests.append(
            TestCaseInfo(
                name=test_name,
                endpoint=endpoint,
                method=method,
                resource=resource,
                requires_auth=requires_auth,
            )
        )

    return tests


def discover_generated_spec_files() -> List[Path]:
    """
    Discover generated spec files to include in report analysis.
    Prefer the canonical generated file; fall back to iterative rounds.
    """
    generated_dir = OPENPROJECT_ROOT / "spec" / "generated"
    canonical = generated_dir / "openproject_generated_request_spec.rb"
    if canonical.exists():
        return [canonical]
    return sorted(generated_dir.glob("openproject_generated_round_*.rb"))


def _extract_method_and_endpoint_from_test_name(test_name: str) -> Tuple[str, str]:
    """
    Parse generated names like 'GET /api/v3/projects/:id' into canonical method/path.
    """
    match = re.match(
        r"^(GET|POST|PATCH|PUT|DELETE)\s+(/[A-Za-z0-9_:\-./]+)",
        test_name.strip(),
        flags=re.IGNORECASE,
    )
    if not match:
        return "", ""
    endpoint = match.group(2).strip()
    # Remove descriptive markers that the LLM may include in names.
    endpoint = re.sub(r"\s+\((public|authenticated)\)\s*$", "", endpoint, flags=re.IGNORECASE)
    return match.group(1).upper(), endpoint


def _extract_method_and_endpoint_from_describe(describe_text: str) -> Tuple[str, str]:
    """
    Parse describe labels like 'GET /projects/:id (public)' into canonical method/path.
    """
    match = re.match(
        r"^(GET|POST|PATCH|PUT|DELETE)\s+(/[A-Za-z0-9_:\-./]+)",
        describe_text.strip(),
        flags=re.IGNORECASE,
    )
    if not match:
        return "", ""
    endpoint = match.group(2).strip()
    endpoint = re.sub(r"\s+\((public|authenticated)\)\s*$", "", endpoint, flags=re.IGNORECASE)
    return match.group(1).upper(), endpoint


def _normalize_runtime_endpoint(endpoint: str) -> str:
    """
    Normalize interpolated runtime path strings to route-template style for matching.
    Example: /projects/#{project.id}/settings -> /projects/:id/settings
    """
    normalized = endpoint
    normalized = re.sub(r"#\{[^}]+\}", ":id", normalized)
    normalized = re.sub(r"/\d+(\b|/)", r"/:id\1", normalized)
    return normalized


def get_resource_coverage(tests: List[TestCaseInfo]) -> List[ResourceCoverage]:
    coverage_rows: List[ResourceCoverage] = []
    tested_pairs: Set[Tuple[str, str]] = {(t.method.upper(), t.endpoint) for t in tests if t.endpoint != "unknown"}

    for name, resource in OPENPROJECT_RESOURCES.items():
        safe_resource_endpoints = [e for e in resource.endpoints if e.safe_for_coverage]
        resource_pairs = {(e.method.upper(), e.path) for e in safe_resource_endpoints}
        total_endpoints = len(resource_pairs)
        if total_endpoints == 0:
            resource_pairs = {(e.method.upper(), e.path) for e in resource.endpoints}
            total_endpoints = len(resource_pairs)
        tested_endpoints = len(resource_pairs.intersection(tested_pairs))
        covered_percent = (tested_endpoints / total_endpoints * 100.0) if total_endpoints else 0.0
        auth_required = sum(1 for e in resource.endpoints if e.requires_auth)
        safe_endpoints = sum(1 for e in resource.endpoints if e.safe_for_coverage)

        coverage_rows.append(
            ResourceCoverage(
                name=name,
                total_endpoints=total_endpoints,
                tested_endpoints=tested_endpoints,
                covered_percent=covered_percent,
                auth_required=auth_required,
                safe_endpoints=safe_endpoints,
            )
        )
    return coverage_rows


def analyze_coverage_gaps(resource_coverage: List[ResourceCoverage]) -> List[UncoveredReason]:
    gaps: List[UncoveredReason] = []
    for row in resource_coverage:
        if row.covered_percent >= 80:
            continue

        if row.name.startswith("api_v3_"):
            reason = f"API v3 resource often needs explicit auth / fixtures (current: {row.covered_percent:.1f}%)"
            priority = "MEDIUM"
        elif row.name == "admin_statuses":
            reason = f"Administrative routes need current_user with elevated permissions (current: {row.covered_percent:.1f}%)"
            priority = "HIGH"
        else:
            reason = f"More generated examples needed for broad route coverage (current: {row.covered_percent:.1f}%)"
            priority = "LOW"

        gaps.append(UncoveredReason(resource=row.name, reason=reason, priority=priority))
    return gaps


def get_api_documentation() -> Dict[str, Any]:
    """
    Build endpoint-centric API documentation from the route mapper.
    """
    stats = get_statistics()
    resources: Dict[str, Dict[str, Any]] = {}

    for name, resource in OPENPROJECT_RESOURCES.items():
        endpoints = []
        for endpoint in resource.endpoints:
            endpoints.append(
                {
                    "method": endpoint.method,
                    "path": endpoint.path,
                    "description": endpoint.description,
                    "requires_auth": endpoint.requires_auth,
                    "safe_for_coverage": endpoint.safe_for_coverage,
                }
            )

        resources[name] = {
            "name": resource.name,
            "base_path": resource.base_path,
            "description": resource.description,
            "total_endpoints": len(resource.endpoints),
            "safe_endpoints": sum(1 for e in resource.endpoints if e.safe_for_coverage),
            "auth_required": sum(1 for e in resource.endpoints if e.requires_auth),
            "endpoints": endpoints,
        }

    return {
        "total_resources": stats["total_resources"],
        "total_endpoints": stats["total_endpoints"],
        "public_endpoints": stats["public_endpoints"],
        "authenticated_endpoints": stats["authenticated_endpoints"],
        "safe_endpoints": stats["safe_endpoints"],
        "by_method": stats["by_method"],
        "resources": resources,
    }


def generate_markdown_report(
    api_docs: Dict[str, Any],
    tests: List[TestCaseInfo],
    resource_coverage: List[ResourceCoverage],
    gaps: List[UncoveredReason],
) -> str:
    zero_coverage_count = sum(1 for r in resource_coverage if r.covered_percent == 0)
    well_covered_count = sum(1 for r in resource_coverage if r.covered_percent >= 80)
    total_safe_endpoints = sum(r.total_endpoints for r in resource_coverage)
    total_hit_endpoints = sum(r.tested_endpoints for r in resource_coverage)
    endpoint_coverage_percent = (
        (total_hit_endpoints / total_safe_endpoints * 100.0) if total_safe_endpoints else 0.0
    )
    public_safe_endpoints = sum(
        1
        for resource in api_docs["resources"].values()
        for endpoint in resource["endpoints"]
        if endpoint["safe_for_coverage"] and not endpoint["requires_auth"]
    )
    authenticated_safe_endpoints = sum(
        1
        for resource in api_docs["resources"].values()
        for endpoint in resource["endpoints"]
        if endpoint["safe_for_coverage"] and endpoint["requires_auth"]
    )

    lines = [
        "# OpenProject Test Generation Report",
        f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n---\n",
        "## 1. API Endpoint Coverage Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Resources | {api_docs['total_resources']} |",
        f"| Total Endpoints | {api_docs['total_endpoints']} |",
        f"| Zero Coverage Resources | {zero_coverage_count} |",
        f"| Well Covered (>80%) | {well_covered_count} |",
        f"| Endpoint Coverage (Safe) | {endpoint_coverage_percent:.2f}% |",
        f"| Safe Endpoints Hit / Total | {total_hit_endpoints} / {total_safe_endpoints} |",
        f"| Public Safe Endpoints | {public_safe_endpoints} |",
        f"| Authenticated Safe Endpoints | {authenticated_safe_endpoints} |",
        "",
        "### 1.1 Endpoint Coverage by Resource",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Well Covered Resources (>80%) | {well_covered_count} |",
        f"| Zero Coverage Resources | {zero_coverage_count} |",
        "",
        "## 2. Endpoint Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Public Endpoints | {api_docs['public_endpoints']} |",
        f"| Authenticated Endpoints | {api_docs['authenticated_endpoints']} |",
        f"| Safe Endpoints | {api_docs['safe_endpoints']} |",
        "",
        "| Method | Count |",
        "|--------|-------|",
    ]

    for method, count in api_docs["by_method"].items():
        lines.append(f"| {method} | {count} |")

    lines.extend(
        [
            "",
            "## 3. API Endpoint Catalog",
            "",
        ]
    )

    for resource_name, info in api_docs["resources"].items():
        lines.extend(
            [
                f"### {resource_name}",
                "",
                f"- Base Path: `{info['base_path']}`",
                f"- Description: {info['description']}",
                f"- Total Endpoints: {info['total_endpoints']}",
                f"- Safe Endpoints: {info['safe_endpoints']}",
                f"- Auth Required Endpoints: {info['auth_required']}",
                "",
                "| Method | Path | Auth | Safe | Description |",
                "|--------|------|------|------|-------------|",
            ]
        )
        for endpoint in info["endpoints"]:
            auth = "Yes" if endpoint["requires_auth"] else "No"
            safe = "Yes" if endpoint["safe_for_coverage"] else "No"
            lines.append(
                f"| {endpoint['method']} | `{endpoint['path']}` | {auth} | {safe} | {endpoint['description']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## 4. Resource Coverage",
            "",
            "| Resource | Endpoints | Endpoints Hit | Coverage | Auth Required |",
            "|----------|-----------|-------|----------|---------------|",
        ]
    )

    for rc in sorted(resource_coverage, key=lambda x: -x.covered_percent):
        lines.append(
            f"| {rc.name} | {rc.total_endpoints} | {rc.tested_endpoints} | "
            f"{rc.covered_percent:.1f}% | {rc.auth_required} |"
        )

    lines.extend(
        [
            "",
            "## 5. Generated Test Cases",
            "",
            f"**Total Test Cases Parsed:** {len(tests)}",
            "",
            "| # | Test Name | Resource | Method | Auth | Endpoint |",
            "|---|-----------|----------|--------|------|----------|",
        ]
    )

    for i, test in enumerate(tests, 1):
        auth = "Yes" if test.requires_auth else "No"
        name = test.name[:40] + "..." if len(test.name) > 40 else test.name
        endpoint = test.endpoint[:45] + "..." if len(test.endpoint) > 45 else test.endpoint
        lines.append(f"| {i} | {name} | {test.resource} | {test.method} | {auth} | `{endpoint}` |")

    lines.extend(
        [
            "",
            "## 6. Coverage Gaps",
            "",
            "| Resource | Reason | Priority |",
            "|----------|--------|----------|",
        ]
    )

    for gap in sorted(gaps, key=lambda g: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(g.priority, 3)):
        lines.append(f"| {gap.resource} | {gap.reason} | {gap.priority} |")

    lines.extend(
        [
            "",
            "---",
            "*Report generated by ENS 491-2 Automated Test Generation System*",
        ]
    )

    return "\n".join(lines)


def generate_json_report(
    api_docs: Dict[str, Any],
    tests: List[TestCaseInfo],
    resource_coverage: List[ResourceCoverage],
    gaps: List[UncoveredReason],
) -> Dict[str, Any]:
    return {
        "generated_at": datetime.now().isoformat(),
        "api_endpoint_coverage_summary": {
            "total_resources": api_docs["total_resources"],
            "total_endpoints": api_docs["total_endpoints"],
            "safe_endpoints": api_docs["safe_endpoints"],
            "public_endpoints": api_docs["public_endpoints"],
            "authenticated_endpoints": api_docs["authenticated_endpoints"],
        },
        "api_documentation": api_docs,
        "generated_tests": {
            "total": len(tests),
            "tests": [asdict(t) for t in tests],
        },
        "resource_coverage": [asdict(r) for r in resource_coverage],
        "coverage_gaps": [asdict(g) for g in gaps],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test generation report for OpenProject"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output path (default: openproject_clean/reports/openproject_report.md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of Markdown",
    )
    args = parser.parse_args()

    api_docs = get_api_documentation()
    test_files = discover_generated_spec_files()
    tests: List[TestCaseInfo] = []
    for test_file in test_files:
        tests.extend(parse_generated_tests(test_file))
    resource_coverage = get_resource_coverage(tests)
    gaps = analyze_coverage_gaps(resource_coverage)

    if args.json:
        report = json.dumps(
            generate_json_report(
                api_docs,
                tests,
                resource_coverage,
                gaps,
            ),
            indent=2,
        )
    else:
        report = generate_markdown_report(
            api_docs,
            tests,
            resource_coverage,
            gaps,
        )

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"Report written to: {out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
