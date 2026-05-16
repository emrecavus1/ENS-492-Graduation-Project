#!/usr/bin/env python3
"""
Comprehensive Test Generation Report for Spree Commerce

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
SPREE_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))

from core.spree_route_mapper import (
    SPREE_STORE_API_RESOURCES,
    SpreeEndpointInfo,
    SpreeResourceInfo,
    get_all_endpoints,
    get_api_statistics,
)


@dataclass
class TestCaseInfo:
    """Information about a generated test case."""
    name: str
    endpoint: str
    method: str
    resource: str
    requires_auth: bool


@dataclass
class UncoveredReason:
    """Reason why something couldn't be covered."""
    resource: str
    reason: str
    priority: str


@dataclass
class ResourceCoverage:
    """Coverage information for a resource."""
    name: str
    total_endpoints: int
    tested_endpoints: int
    covered_percent: float
    requires_auth: int
    safe_endpoints: int


def parse_coverage_file(coverage_path: Path) -> Dict[str, Any]:
    """Parse SimpleCov .resultset.json file."""
    if not coverage_path.exists():
        return {}
    
    try:
        with open(coverage_path, 'r') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError):
        return {}


def calculate_coverage_stats(coverage_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate coverage statistics from SimpleCov data."""
    if not coverage_data:
        return {
            "available": False,
            "total_lines": 0,
            "covered_lines": 0,
            "coverage_percent": 0.0,
        }
    
    total_lines = 0
    covered_lines = 0
    
    for suite_name, suite_data in coverage_data.items():
        if isinstance(suite_data, dict) and "coverage" in suite_data:
            for file_path, file_data in suite_data["coverage"].items():
                if isinstance(file_data, dict):
                    lines = file_data.get("lines", [])
                else:
                    lines = file_data
                
                for line in lines:
                    if line is not None:
                        total_lines += 1
                        if line > 0:
                            covered_lines += 1
    
    return {
        "available": True,
        "total_lines": total_lines,
        "covered_lines": covered_lines,
        "coverage_percent": (covered_lines / total_lines * 100) if total_lines > 0 else 0.0,
    }


def parse_generated_tests(test_file: Path) -> List[TestCaseInfo]:
    """Parse the generated RSpec test file and extract test case information."""
    tests = []
    
    if not test_file.exists():
        return tests
    
    content = test_file.read_text(encoding="utf-8")
    
    # Parse describe blocks to understand context, then find 'it' blocks within
    # Look for patterns like: describe 'Account Orders API' do ... it 'test name' do
    
    # Find all describe blocks with their content
    lines = content.split('\n')
    current_resource = "unknown"
    
    for i, line in enumerate(lines):
        # Check for describe blocks that indicate resource
        describe_match = re.search(r"describe\s+['\"]([^'\"]+)['\"]", line)
        if describe_match:
            desc_text = describe_match.group(1).lower()
            
            # Map describe block names to resources
            if 'account orders' in desc_text:
                current_resource = 'account_orders'
            elif 'account addresses' in desc_text:
                current_resource = 'account_addresses'
            elif 'account credit cards' in desc_text:
                current_resource = 'account_credit_cards'
            elif 'account api' in desc_text or desc_text == 'account':
                current_resource = 'account'
            elif 'products' in desc_text:
                current_resource = 'products'
            elif 'taxons' in desc_text:
                current_resource = 'taxons'
            elif 'cart' in desc_text:
                current_resource = 'cart'
            elif 'checkout' in desc_text:
                current_resource = 'checkout'
            elif 'countries' in desc_text:
                current_resource = 'countries'
            elif 'states' in desc_text:
                current_resource = 'states'
            elif 'stores' in desc_text or 'store api' in desc_text:
                current_resource = 'stores'
            elif 'menus' in desc_text:
                current_resource = 'menus'
            elif 'pages' in desc_text:
                current_resource = 'pages'
            elif 'wishlists' in desc_text:
                current_resource = 'wishlists'
            elif 'auth' in desc_text and 'oauth' not in desc_text:
                current_resource = 'auth'
        
        # Check for 'it' blocks
        it_match = re.search(r"it\s+['\"]([^'\"]+)['\"]", line)
        if it_match:
            test_name = it_match.group(1)
            
            # Determine HTTP method from test name or nearby get/post/patch/delete calls
            method = "GET"
            # Look at the next few lines for HTTP method
            for j in range(i, min(i + 5, len(lines))):
                check_line = lines[j].strip().lower()
                if check_line.startswith('post ') or 'post ' in check_line[:20]:
                    method = "POST"
                    break
                elif check_line.startswith('patch ') or 'patch ' in check_line[:20]:
                    method = "PATCH"
                    break
                elif check_line.startswith('delete ') or 'delete ' in check_line[:20]:
                    method = "DELETE"
                    break
                elif check_line.startswith('put ') or 'put ' in check_line[:20]:
                    method = "PUT"
                    break
            
            # Check if test uses auth_headers
            requires_auth = False
            for j in range(i, min(i + 10, len(lines))):
                if 'auth_headers' in lines[j]:
                    requires_auth = True
                    break
            
            endpoint = f"/api/v3/store/{current_resource.replace('_', '/')}"
            
            tests.append(TestCaseInfo(
                name=test_name,
                endpoint=endpoint,
                method=method,
                resource=current_resource,
                requires_auth=requires_auth,
            ))
    
    return tests


def get_resource_coverage(tests: List[TestCaseInfo]) -> List[ResourceCoverage]:
    """Calculate coverage for each API resource."""
    coverage_list = []
    
    for name, resource in SPREE_STORE_API_RESOURCES.items():
        total_endpoints = len(resource.endpoints)
        tests_for_resource = [t for t in tests if t.resource == name]
        tested_endpoints = len(tests_for_resource)
        
        covered_percent = (tested_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0.0
        requires_auth = sum(1 for e in resource.endpoints if e.requires_auth)
        safe_endpoints = sum(1 for e in resource.endpoints if e.safe_for_coverage)
        
        coverage_list.append(ResourceCoverage(
            name=name,
            total_endpoints=total_endpoints,
            tested_endpoints=tested_endpoints,
            covered_percent=covered_percent,
            requires_auth=requires_auth,
            safe_endpoints=safe_endpoints,
        ))
    
    return coverage_list


def get_api_documentation() -> Dict[str, Any]:
    """Generate API documentation from route mapper."""
    stats = get_api_statistics()
    
    api_docs = {
        "total_resources": stats["total_resources"],
        "total_endpoints": stats["total_endpoints"],
        "public_endpoints": stats["public_endpoints"],
        "authenticated_endpoints": stats["authenticated_endpoints"],
        "safe_endpoints": stats["safe_endpoints"],
        "unsafe_endpoints": stats["total_endpoints"] - stats["safe_endpoints"],
        "by_method": stats["by_method"],
        "resources": {},
    }
    
    for name, resource in SPREE_STORE_API_RESOURCES.items():
        resource_info = {
            "name": resource.name,
            "base_path": resource.base_path,
            "description": resource.description,
            "endpoints": [],
            "total_endpoints": len(resource.endpoints),
            "auth_required": sum(1 for e in resource.endpoints if e.requires_auth),
            "safe_endpoints": sum(1 for e in resource.endpoints if e.safe_for_coverage),
        }
        
        for endpoint in resource.endpoints:
            resource_info["endpoints"].append({
                "method": endpoint.method,
                "path": endpoint.path,
                "description": endpoint.description,
                "requires_auth": endpoint.requires_auth,
                "safe_for_coverage": endpoint.safe_for_coverage,
            })
        
        api_docs["resources"][name] = resource_info
    
    return api_docs


def analyze_coverage_gaps(
    resource_coverage: List[ResourceCoverage],
    generated_tests: List[TestCaseInfo],
) -> List[UncoveredReason]:
    """Analyze what couldn't be covered and why."""
    gaps = []
    
    for resource in resource_coverage:
        name = resource.name
        
        if resource.covered_percent >= 80:
            continue
        
        if name in ["auth"]:
            reason = f"OAuth routes at /api/oauth/token not /api/v3/store (current: {resource.covered_percent:.1f}%)"
            priority = "LOW"
        elif name in ["checkout"]:
            reason = f"Checkout flow requires cart with line items first (current: {resource.covered_percent:.1f}%)"
            priority = "MEDIUM"
        elif name in ["cart"]:
            reason = f"Cart state-dependent operations need sequential setup (current: {resource.covered_percent:.1f}%)"
            priority = "MEDIUM"
        elif name in ["wishlists"]:
            reason = f"Some wishlist operations need existing wishlist items (current: {resource.covered_percent:.1f}%)"
            priority = "MEDIUM"
        elif name in ["account_orders"]:
            reason = f"Order history requires existing orders in database (current: {resource.covered_percent:.1f}%)"
            priority = "MEDIUM"
        elif name in ["account_addresses"]:
            reason = f"Address operations tested - some require existing address fixtures (current: {resource.covered_percent:.1f}%)"
            priority = "LOW"
        elif name in ["account_credit_cards"]:
            reason = f"Credit card listing tested - payment methods depend on store config (current: {resource.covered_percent:.1f}%)"
            priority = "LOW"
        elif name in ["account"]:
            reason = f"Account endpoints covered with Spree::RefreshToken auth (current: {resource.covered_percent:.1f}%)"
            priority = "LOW"
        elif name in ["stores"]:
            reason = f"Single store endpoint - may need default store in test DB (current: {resource.covered_percent:.1f}%)"
            priority = "LOW"
        elif name in ["menus"]:
            reason = f"No :menu factory available - uses Spree::CmsNavigation (current: {resource.covered_percent:.1f}%)"
            priority = "LOW"
        elif name in ["pages"]:
            reason = f"No :page factory available - uses Spree::CmsPage (current: {resource.covered_percent:.1f}%)"
            priority = "LOW"
        elif resource.safe_endpoints < resource.total_endpoints:
            reason = f"Some endpoints filtered as destructive (DELETE operations) (current: {resource.covered_percent:.1f}%)"
            priority = "LOW"
        else:
            reason = f"Additional test examples would increase coverage (current: {resource.covered_percent:.1f}%)"
            priority = "LOW"
        
        gaps.append(UncoveredReason(
            resource=name,
            reason=reason,
            priority=priority,
        ))
    
    return gaps


def generate_markdown_report(
    coverage_stats: Dict[str, Any],
    api_docs: Dict[str, Any],
    tests: List[TestCaseInfo],
    resource_coverage: List[ResourceCoverage],
    gaps: List[UncoveredReason],
) -> str:
    """Generate a comprehensive Markdown report."""
    
    zero_coverage_count = sum(1 for r in resource_coverage if r.covered_percent == 0)
    well_covered_count = sum(1 for r in resource_coverage if r.covered_percent >= 80)
    
    lines = [
        "# Spree Commerce Test Generation Report",
        f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n---\n",
        
        "## 1. Code Coverage Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Resources | {api_docs['total_resources']} |",
        f"| Total Endpoints | {api_docs['total_endpoints']} |",
        f"| Zero Coverage Resources | {zero_coverage_count} |",
        f"| Well Covered (>80%) | {well_covered_count} |",
        f"| Overall Coverage | {coverage_stats.get('coverage_percent', 0):.1f}% |",
        "",
        
        "### 1.1 Coverage by Resource",
        "",
        "| Resource | Endpoints | Tests | Coverage | Auth Required |",
        "|----------|-----------|-------|----------|---------------|",
    ]
    
    for rc in sorted(resource_coverage, key=lambda x: -x.covered_percent):
        coverage_str = f"{rc.covered_percent:.1f}%"
        lines.append(f"| {rc.name} | {rc.total_endpoints} | {rc.tested_endpoints} | {coverage_str} | {rc.requires_auth} |")
    
    lines.extend([
        "",
        "## 2. API Documentation",
        "",
        "### 2.1 API Statistics",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Resources | {api_docs['total_resources']} |",
        f"| Total Endpoints | {api_docs['total_endpoints']} |",
        f"| Public Endpoints | {api_docs['public_endpoints']} |",
        f"| Authenticated Endpoints | {api_docs['authenticated_endpoints']} |",
        f"| Safe for Testing | {api_docs['safe_endpoints']} |",
        f"| Unsafe (filtered) | {api_docs['unsafe_endpoints']} |",
        "",
        
        "### 2.2 Endpoints by HTTP Method",
        "",
        "| Method | Count |",
        "|--------|-------|",
    ])
    
    for method, count in api_docs['by_method'].items():
        if count > 0:
            lines.append(f"| {method} | {count} |")
    
    lines.extend([
        "",
        "### 2.3 Resource Details",
        "",
    ])
    
    for name, resource in api_docs['resources'].items():
        lines.append(f"\n#### {name.replace('_', ' ').title()} (`{name}`)")
        lines.append(f"- Base Path: `{resource['base_path']}`")
        lines.append(f"- Description: {resource['description']}")
        lines.append(f"- Total Endpoints: {resource['total_endpoints']}")
        lines.append(f"- Auth Required: {resource['auth_required']}")
        lines.append(f"- Safe Endpoints: {resource['safe_endpoints']}")
        lines.append("")
        lines.append("| Method | Path | Description | Auth | Safe |")
        lines.append("|--------|------|-------------|------|------|")
        
        for endpoint in resource['endpoints']:
            auth = "Yes" if endpoint['requires_auth'] else "No"
            safe = "Yes" if endpoint['safe_for_coverage'] else "No ⚠️"
            lines.append(f"| {endpoint['method']} | `{endpoint['path']}` | {endpoint['description']} | {auth} | {safe} |")
    
    lines.extend([
        "",
        "## 3. Generated Test Cases",
        "",
        f"**Total Test Cases Generated:** {len(tests)}",
        "",
    ])
    
    if tests:
        lines.extend([
            "### 3.1 Test Case Summary",
            "",
            "| # | Test Name | Resource | Method | Auth |",
            "|---|-----------|----------|--------|------|",
        ])
        
        for i, test in enumerate(tests, 1):
            auth = "Yes" if test.requires_auth else "No"
            name_truncated = test.name[:45] + "..." if len(test.name) > 45 else test.name
            lines.append(f"| {i} | {name_truncated} | {test.resource} | {test.method} | {auth} |")
        
        lines.extend([
            "",
            "### 3.2 Tests by Resource",
            "",
            "| Resource | Test Count |",
            "|----------|------------|",
        ])
        
        resource_counts = {}
        for test in tests:
            resource_counts[test.resource] = resource_counts.get(test.resource, 0) + 1
        
        for resource, count in sorted(resource_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {resource} | {count} |")
    else:
        lines.append("No generated tests found. Run `python scripts/generate_tests.py` first.")
    
    lines.extend([
        "",
        "## 4. Coverage Gaps Analysis",
        "",
        "### 4.1 What Couldn't Be Covered and Why",
        "",
        "| Resource | Reason | Priority |",
        "|----------|--------|----------|",
    ])
    
    for gap in sorted(gaps, key=lambda g: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "SKIP": 4}.get(g.priority, 5)):
        lines.append(f"| {gap.resource} | {gap.reason} | {gap.priority} |")
    
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
    
    for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "SKIP"]:
        if priority in priority_counts:
            lines.append(f"| {priority} | {priority_counts[priority]} |")
    
    lines.extend([
        "",
        "---",
        "*Report generated by ENS 491-2 Automated Test Generation System*",
    ])
    
    return "\n".join(lines)


def generate_json_report(
    coverage_stats: Dict[str, Any],
    api_docs: Dict[str, Any],
    tests: List[TestCaseInfo],
    resource_coverage: List[ResourceCoverage],
    gaps: List[UncoveredReason],
) -> Dict[str, Any]:
    """Generate a JSON report."""
    return {
        "generated_at": datetime.now().isoformat(),
        "coverage": {
            "overall_coverage": coverage_stats,
            "resource_coverage": [asdict(rc) for rc in resource_coverage],
        },
        "api_documentation": api_docs,
        "generated_tests": {
            "total": len(tests),
            "tests": [asdict(t) for t in tests],
            "by_resource": {
                resource: sum(1 for t in tests if t.resource == resource)
                for resource in set(t.resource for t in tests)
            } if tests else {},
        },
        "coverage_gaps": {
            "total": len(gaps),
            "gaps": [asdict(g) for g in gaps],
            "by_priority": {
                priority: sum(1 for g in gaps if g.priority == priority)
                for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "SKIP"]
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test generation report for Spree Commerce"
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
    coverage_path = SPREE_ROOT / "coverage" / ".resultset.json"
    coverage_data = parse_coverage_file(coverage_path)
    coverage_stats = calculate_coverage_stats(coverage_data)
    
    if not coverage_stats.get("available"):
        print("Warning: No coverage data found. Run tests with COVERAGE=1 first.", file=sys.stderr)
    
    # Get API documentation
    api_docs = get_api_documentation()
    
    # Parse generated tests
    test_file = SPREE_ROOT / "spec" / "generated" / "store_api_spec.rb"
    tests = parse_generated_tests(test_file)
    
    # Calculate resource coverage
    resource_coverage = get_resource_coverage(tests)
    
    # Analyze gaps
    gaps = analyze_coverage_gaps(resource_coverage, tests)
    
    # Generate report
    if args.json:
        report = json.dumps(
            generate_json_report(coverage_stats, api_docs, tests, resource_coverage, gaps),
            indent=2,
        )
    else:
        report = generate_markdown_report(coverage_stats, api_docs, tests, resource_coverage, gaps)
    
    # Output
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
