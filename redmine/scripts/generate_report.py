#!/usr/bin/env python3
"""
Comprehensive Test Generation Report for Redmine

This script generates a detailed report covering:
1. Code coverage statistics
2. API documentation (routes, parameters, authentication)
3. Test case generation analysis
4. Coverage gaps analysis

Usage:
    python scripts/generate_report.py
    python scripts/generate_report.py --output report.md
    python scripts/generate_report.py --json
"""
import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REDMINE_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))

from core.coverage_analyzer import CoverageAnalyzer, ControllerCoverage, EXCLUDE_CONTROLLERS, EXCLUDE_PATTERNS
from core.route_mapper import CONTROLLER_ROUTES, RouteInfo


@dataclass
class TestCaseInfo:
    """Information about a generated test case."""
    name: str
    controller: str
    route: str
    method: str
    requires_auth: bool
    uses_fixture: bool
    uses_xhr: bool


@dataclass 
class UncoveredReason:
    """Reason why something couldn't be covered."""
    controller: str
    reason: str
    priority: str


def parse_generated_tests(test_file: Path) -> List[TestCaseInfo]:
    """Parse the generated test file and extract test case information."""
    tests = []
    
    if not test_file.exists():
        return tests
    
    content = test_file.read_text(encoding="utf-8")
    
    test_pattern = r'test\s+["\']([^"\']+)["\']\s+do\s*(.*?)(?=\n\s*(?:test\s|end\s*$))'
    matches = re.findall(test_pattern, content, re.DOTALL)
    
    for test_name, test_body in matches:
        route_match = re.search(r"(?:get|post|put|patch|delete)\s+['\"]([^'\"]+)['\"]", test_body)
        route = route_match.group(1) if route_match else "unknown"
        
        method_match = re.search(r"(get|post|put|patch|delete)\s+['\"]", test_body)
        method = method_match.group(1).upper() if method_match else "GET"
        
        requires_auth = "log_user" in test_body
        
        uses_fixture = any(model in test_body for model in 
                         ["User.first", "Role.first", "Issue.first", "Project.first"])
        
        uses_xhr = "xhr: true" in test_body or "xhr:true" in test_body
        
        controller = guess_controller_from_route(route)
        
        tests.append(TestCaseInfo(
            name=test_name,
            controller=controller,
            route=route,
            method=method,
            requires_auth=requires_auth,
            uses_fixture=uses_fixture,
            uses_xhr=uses_xhr,
        ))
    
    return tests


def guess_controller_from_route(route: str) -> str:
    """Guess the controller name from a route path."""
    route = route.split("?")[0]
    
    controller_mappings = {
        "/users": "users_controller",
        "/time_entries": "timelog_controller",
        "/projects": "projects_controller",
        "/issues": "issues_controller",
        "/roles": "roles_controller",
        "/workflows": "workflows_controller",
        "/trackers": "trackers_controller",
        "/search": "search_controller",
        "/watchers": "watchers_controller",
        "/news": "news_controller",
        "/boards": "boards_controller",
        "/wiki": "wiki_controller",
        "/documents": "documents_controller",
        "/admin": "admin_controller",
        "/groups": "groups_controller",
        "/settings": "settings_controller",
    }
    
    for pattern, controller in controller_mappings.items():
        if pattern in route:
            return controller
    
    return "unknown_controller"


def get_api_documentation() -> Dict[str, Any]:
    """Generate API documentation from route mapper."""
    api_docs = {
        "total_controllers": len(CONTROLLER_ROUTES),
        "total_routes": 0,
        "routes_by_method": {"GET": 0, "POST": 0, "PUT": 0, "PATCH": 0, "DELETE": 0},
        "routes_requiring_auth": 0,
        "routes_requiring_xhr": 0,
        "routes_with_params": 0,
        "unsafe_routes": 0,
        "controllers": {}
    }
    
    for controller, routes in CONTROLLER_ROUTES.items():
        controller_info = {
            "display_name": controller.replace("_controller", "").title(),
            "routes": [],
            "total_routes": len(routes),
            "auth_required_routes": 0,
            "xhr_routes": 0,
        }
        
        for route in routes:
            route_info = {
                "method": route.method,
                "path": route.path,
                "description": route.description,
                "requires_auth": route.requires_auth,
                "requires_xhr": route.requires_xhr,
                "has_params": ":id" in route.path or ":user_id" in route.path or "?" in route.path,
                "fixture_lookup": route.fixture_lookup,
                "safe_for_coverage": route.safe_for_coverage,
            }
            controller_info["routes"].append(route_info)
            
            api_docs["total_routes"] += 1
            api_docs["routes_by_method"][route.method] = api_docs["routes_by_method"].get(route.method, 0) + 1
            
            if route.requires_auth:
                api_docs["routes_requiring_auth"] += 1
                controller_info["auth_required_routes"] += 1
            
            if route.requires_xhr:
                api_docs["routes_requiring_xhr"] += 1
                controller_info["xhr_routes"] += 1
            
            if ":id" in route.path or ":user_id" in route.path:
                api_docs["routes_with_params"] += 1
            
            if not route.safe_for_coverage:
                api_docs["unsafe_routes"] += 1
        
        api_docs["controllers"][controller] = controller_info
    
    return api_docs


def analyze_coverage_gaps(
    analyzer: CoverageAnalyzer,
    generated_tests: List[TestCaseInfo],
) -> List[UncoveredReason]:
    """Analyze what couldn't be covered and why."""
    gaps = []
    
    low_coverage = [c for c in analyzer.controllers if c.covered_percent < 80]
    
    for controller in low_coverage:
        name = controller.name
        
        if "repository" in name or "repositories" in name:
            reason = f"Requires VCS repository setup (current: {controller.covered_percent:.1f}%)"
            priority = "LOW" if controller.covered_percent > 50 else "MEDIUM"
        elif "plugin" in name:
            reason = f"Plugin-related controller (current: {controller.covered_percent:.1f}%)"
            priority = "LOW"
        elif "context_menu" in name:
            reason = f"Requires XHR headers (current: {controller.covered_percent:.1f}%)"
            priority = "MEDIUM" if controller.covered_percent > 50 else "HIGH"
        elif name in EXCLUDE_CONTROLLERS:
            reason = "Excluded from coverage (system/internal controller)"
            priority = "SKIP"
        else:
            if name not in CONTROLLER_ROUTES:
                reason = f"No route mappings defined (current: {controller.covered_percent:.1f}%)"
                priority = "HIGH"
            else:
                routes = CONTROLLER_ROUTES[name]
                unsafe_count = sum(1 for r in routes if not r.safe_for_coverage)
                if unsafe_count == len(routes):
                    reason = f"All routes require POST/DELETE with parameters (current: {controller.covered_percent:.1f}%)"
                    priority = "MEDIUM"
                else:
                    reason = f"Tests may not hit all code paths (current: {controller.covered_percent:.1f}%)"
                    priority = "HIGH" if controller.covered_percent < 20 else "MEDIUM"
        
        gaps.append(UncoveredReason(
            controller=name,
            reason=reason,
            priority=priority,
        ))
    
    return gaps


def generate_markdown_report(
    coverage_summary: Dict[str, Any],
    api_docs: Dict[str, Any],
    tests: List[TestCaseInfo],
    gaps: List[UncoveredReason],
) -> str:
    """Generate a comprehensive Markdown report."""
    
    lines = [
        "# Redmine Test Generation Report",
        f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n---\n",
        
        "## 1. Code Coverage Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Controllers | {coverage_summary.get('total_controllers', 'N/A')} |",
        f"| Zero Coverage | {coverage_summary.get('zero_coverage_count', 'N/A')} |",
        f"| Well Covered (>70%) | {coverage_summary.get('well_covered_count', 'N/A')} |",
        f"| Overall Coverage | {coverage_summary.get('overall_coverage_percent', 0):.1f}% |",
        "",
    ]
    
    lines.extend([
        "## 2. API Documentation",
        "",
        "### 2.1 API Statistics",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Controllers | {api_docs['total_controllers']} |",
        f"| Total Routes/Endpoints | {api_docs['total_routes']} |",
        f"| Routes Requiring Authentication | {api_docs['routes_requiring_auth']} |",
        f"| Routes Requiring XHR Headers | {api_docs['routes_requiring_xhr']} |",
        f"| Routes with Dynamic Parameters | {api_docs['routes_with_params']} |",
        f"| Unsafe Routes (filtered out) | {api_docs['unsafe_routes']} |",
        "",
        
        "### 2.2 Routes by HTTP Method",
        "",
        "| Method | Count |",
        "|--------|-------|",
    ])
    
    for method, count in api_docs['routes_by_method'].items():
        if count > 0:
            lines.append(f"| {method} | {count} |")
    
    lines.extend([
        "",
        "### 2.3 Controller Route Details",
        "",
    ])
    
    for controller, info in sorted(api_docs['controllers'].items()):
        lines.append(f"\n#### {info['display_name']} (`{controller}`)")
        lines.append(f"- Total Routes: {info['total_routes']}")
        lines.append(f"- Auth Required: {info['auth_required_routes']}")
        lines.append(f"- XHR Routes: {info['xhr_routes']}")
        lines.append("")
        lines.append("| Method | Path | Description | Auth | XHR | Params |")
        lines.append("|--------|------|-------------|------|-----|--------|")
        
        for route in info['routes']:
            auth = "Yes" if route['requires_auth'] else "No"
            xhr = "Yes" if route['requires_xhr'] else "No"
            params = "Yes" if route['has_params'] else "No"
            safe = "" if route['safe_for_coverage'] else " ⚠️"
            lines.append(f"| {route['method']} | `{route['path']}` | {route['description']}{safe} | {auth} | {xhr} | {params} |")
    
    lines.extend([
        "",
        "## 3. Generated Test Cases",
        "",
        f"**Total Test Cases Generated:** {len(tests)}",
        "",
        "### 3.1 Test Case Summary",
        "",
        "| # | Test Name | Controller | Route | Method | Auth | XHR |",
        "|---|-----------|------------|-------|--------|------|-----|",
    ])
    
    for i, test in enumerate(tests, 1):
        auth = "Yes" if test.requires_auth else "No"
        xhr = "Yes" if test.uses_xhr else "No"
        lines.append(f"| {i} | {test.name[:40]}... | {test.controller.replace('_controller', '')} | `{test.route[:30]}` | {test.method} | {auth} | {xhr} |")
    
    lines.extend([
        "",
        "### 3.2 Test Coverage by Controller",
        "",
    ])
    
    controller_test_counts = {}
    for test in tests:
        controller_test_counts[test.controller] = controller_test_counts.get(test.controller, 0) + 1
    
    lines.append("| Controller | Test Count |")
    lines.append("|------------|------------|")
    for controller, count in sorted(controller_test_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {controller.replace('_controller', '')} | {count} |")
    
    lines.extend([
        "",
        "## 4. Coverage Gaps Analysis",
        "",
        "### 4.1 What Couldn't Be Covered and Why",
        "",
        "| Controller | Reason | Priority |",
        "|------------|--------|----------|",
    ])
    
    for gap in sorted(gaps, key=lambda g: {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "SKIP": 3}.get(g.priority, 4)):
        lines.append(f"| {gap.controller.replace('_controller', '')} | {gap.reason} | {gap.priority} |")
    
    lines.extend([
        "",
        "### 4.2 Gap Summary",
        "",
        "| Priority | Count |",
        "|----------|-------|",
    ])
    
    priority_counts = {}
    for gap in gaps:
        priority_counts[gap.priority] = priority_counts.get(gap.priority, 0) + 1
    
    for priority in ["HIGH", "MEDIUM", "LOW", "SKIP"]:
        if priority in priority_counts:
            lines.append(f"| {priority} | {priority_counts[priority]} |")
    
    lines.extend([
        "",
        "---",
        "*Report generated by ENS 491-2 Automated Test Generation System*",
    ])
    
    return "\n".join(lines)


def generate_json_report(
    coverage_summary: Dict[str, Any],
    api_docs: Dict[str, Any],
    tests: List[TestCaseInfo],
    gaps: List[UncoveredReason],
) -> Dict[str, Any]:
    """Generate a JSON report."""
    return {
        "generated_at": datetime.now().isoformat(),
        "coverage": coverage_summary,
        "api_documentation": api_docs,
        "generated_tests": {
            "total": len(tests),
            "tests": [asdict(t) for t in tests],
            "by_controller": {
                controller: sum(1 for t in tests if t.controller == controller)
                for controller in set(t.controller for t in tests)
            },
        },
        "coverage_gaps": {
            "total": len(gaps),
            "gaps": [asdict(g) for g in gaps],
            "by_priority": {
                priority: sum(1 for g in gaps if g.priority == priority)
                for priority in ["HIGH", "MEDIUM", "LOW", "SKIP"]
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test generation report for Redmine"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of Markdown"
    )
    
    args = parser.parse_args()
    
    # Load coverage data
    analyzer = CoverageAnalyzer(REDMINE_ROOT)
    has_coverage = analyzer.load_coverage()
    
    if has_coverage:
        coverage_summary = analyzer.get_coverage_summary()
    else:
        coverage_summary = {
            "available": False,
            "total_controllers": 0,
            "zero_coverage_count": 0,
            "well_covered_count": 0,
            "overall_coverage_percent": 0,
        }
        print("Warning: No coverage data found. Run tests first.", file=sys.stderr)
    
    # Get API documentation
    api_docs = get_api_documentation()
    
    # Parse generated tests
    test_file = REDMINE_ROOT / "test" / "generated" / "generated_suite_test.rb"
    tests = parse_generated_tests(test_file)
    
    # Analyze gaps
    gaps = analyze_coverage_gaps(analyzer, tests)
    
    # Generate report
    if args.json:
        report = json.dumps(
            generate_json_report(coverage_summary, api_docs, tests, gaps),
            indent=2,
        )
    else:
        report = generate_markdown_report(coverage_summary, api_docs, tests, gaps)
    
    # Output
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
