"""
SauceDemo Coverage Analyzer Module

Tracks UI page and flow coverage for the SauceDemo application.
Unlike code coverage (SimpleCov), this tracks which pages and
user flows have been exercised by tests.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from core.saucedemo_page_mapper import (
    SAUCEDEMO_PAGES,
    SAUCEDEMO_FLOWS,
    PageInfo,
    UserFlow,
    get_uncovered_flows,
)


@dataclass
class PageCoverage:
    """Represents coverage data for a single UI page."""
    name: str
    is_covered: bool
    visit_count: int = 0
    
    @property
    def priority_label(self) -> str:
        """Priority based on coverage status."""
        if not self.is_covered:
            return "CRITICAL"
        elif self.visit_count < 2:
            return "LOW"
        else:
            return "SKIP"


@dataclass 
class FlowCoverage:
    """Represents coverage data for a user flow."""
    flow: UserFlow
    pages_covered: int
    total_pages: int
    
    @property
    def coverage_percent(self) -> float:
        if self.total_pages == 0:
            return 0.0
        return round(100 * self.pages_covered / self.total_pages, 2)
    
    @property
    def is_fully_covered(self) -> bool:
        return self.pages_covered == self.total_pages
    
    @property
    def priority_label(self) -> str:
        """Priority based on flow importance and coverage."""
        if self.coverage_percent == 0:
            if self.flow.priority == "CRITICAL":
                return "CRITICAL"
            return "HIGH"
        elif self.coverage_percent < 50:
            return "HIGH"
        elif self.coverage_percent < 100:
            return "MEDIUM"
        else:
            return "SKIP"


class SauceDemoCoverageAnalyzer:
    """
    Analyzes UI page and flow coverage for SauceDemo.
    
    Coverage can be loaded from:
    1. A JSON file persisted from previous test runs
    2. Programmatically from visited pages set
    """
    
    def __init__(self, saucedemo_root: Path):
        self.saucedemo_root = Path(saucedemo_root)
        self.coverage_path = self.saucedemo_root / "coverage" / "page_coverage.json"
        self.visited_pages: Set[str] = set()
        self.page_visit_counts: Dict[str, int] = {}
        
    def load_coverage(self) -> bool:
        """Load coverage from JSON file. Returns True if successful."""
        if not self.coverage_path.exists():
            return False
        
        try:
            data = json.loads(self.coverage_path.read_text(encoding="utf-8"))
            self.visited_pages = set(data.get("visited_pages", []))
            self.page_visit_counts = data.get("page_visit_counts", {})
            return True
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to parse coverage data: {e}")
            return False
    
    def save_coverage(self) -> None:
        """Save current coverage state to JSON file."""
        self.coverage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "visited_pages": sorted(list(self.visited_pages)),
            "page_visit_counts": self.page_visit_counts,
        }
        self.coverage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def mark_page_visited(self, page_name: str) -> None:
        """Mark a page as visited during test execution."""
        self.visited_pages.add(page_name)
        self.page_visit_counts[page_name] = self.page_visit_counts.get(page_name, 0) + 1
    
    def set_visited_pages(self, pages: Set[str]) -> None:
        """Set visited pages from external source (e.g., adapter)."""
        self.visited_pages = pages
        for page in pages:
            if page not in self.page_visit_counts:
                self.page_visit_counts[page] = 1
    
    def get_page_coverage(self) -> List[PageCoverage]:
        """Get coverage status for all pages."""
        return [
            PageCoverage(
                name=name,
                is_covered=name in self.visited_pages,
                visit_count=self.page_visit_counts.get(name, 0),
            )
            for name in SAUCEDEMO_PAGES.keys()
        ]
    
    def get_flow_coverage(self) -> List[FlowCoverage]:
        """Get coverage status for all flows."""
        result = []
        for flow in SAUCEDEMO_FLOWS:
            pages_covered = sum(1 for p in flow.pages_involved if p in self.visited_pages)
            result.append(FlowCoverage(
                flow=flow,
                pages_covered=pages_covered,
                total_pages=len(flow.pages_involved),
            ))
        return result
    
    def get_uncovered_pages(self) -> List[str]:
        """Get list of pages not yet visited."""
        return [name for name in SAUCEDEMO_PAGES.keys() if name not in self.visited_pages]
    
    def get_priority_flows(self, max_count: int = 10) -> List[FlowCoverage]:
        """
        Get flows sorted by priority for test generation.
        
        Prioritizes:
        1. CRITICAL flows with low coverage
        2. HIGH priority flows with low coverage
        3. Flows with more uncovered pages
        """
        flow_coverage = self.get_flow_coverage()
        
        def priority_score(fc: FlowCoverage) -> tuple:
            priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "SKIP": 4}
            return (
                priority_order.get(fc.priority_label, 4),
                priority_order.get(fc.flow.priority, 4),
                fc.coverage_percent,  # Lower coverage = higher priority
            )
        
        sorted_flows = sorted(flow_coverage, key=priority_score)
        return [f for f in sorted_flows if f.priority_label != "SKIP"][:max_count]
    
    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get summary statistics of coverage data."""
        total_pages = len(SAUCEDEMO_PAGES)
        covered_pages = len(self.visited_pages)
        
        total_flows = len(SAUCEDEMO_FLOWS)
        flow_coverage = self.get_flow_coverage()
        fully_covered_flows = sum(1 for f in flow_coverage if f.is_fully_covered)
        
        critical_flows = [f for f in SAUCEDEMO_FLOWS if f.priority == "CRITICAL"]
        critical_covered = sum(
            1 for f in critical_flows
            if all(p in self.visited_pages for p in f.pages_involved)
        )
        
        return {
            "available": True,
            "type": "ui_page_coverage",
            "total_pages": total_pages,
            "covered_pages": covered_pages,
            "page_coverage_percent": round(100 * covered_pages / total_pages, 2) if total_pages > 0 else 0,
            "uncovered_pages": self.get_uncovered_pages(),
            "total_flows": total_flows,
            "fully_covered_flows": fully_covered_flows,
            "flow_coverage_percent": round(100 * fully_covered_flows / total_flows, 2) if total_flows > 0 else 0,
            "critical_flows_total": len(critical_flows),
            "critical_flows_covered": critical_covered,
        }
    
    def print_report(self) -> None:
        """Print a human-readable coverage report."""
        print("\n" + "=" * 70)
        print("SAUCEDEMO UI COVERAGE REPORT")
        print("=" * 70)
        
        # Page Coverage
        print("\nPAGE COVERAGE:")
        print("-" * 50)
        page_coverage = self.get_page_coverage()
        for pc in page_coverage:
            status = "✓" if pc.is_covered else "✗"
            visits = f"({pc.visit_count} visits)" if pc.visit_count > 0 else ""
            print(f"  {status} {pc.name:<25} {pc.priority_label:>10} {visits}")
        
        # Flow Coverage
        print("\nFLOW COVERAGE:")
        print("-" * 70)
        print(f"{'Flow':<35} {'Priority':>10} {'Coverage':>12} {'Status':>10}")
        print("-" * 70)
        
        flow_coverage = sorted(self.get_flow_coverage(), key=lambda f: f.coverage_percent)
        for fc in flow_coverage:
            print(f"{fc.flow.name:<35} {fc.flow.priority:>10} {fc.coverage_percent:>10.1f}% {fc.priority_label:>10}")
        
        # Summary
        summary = self.get_coverage_summary()
        print("\n" + "-" * 70)
        print(f"Page Coverage: {summary['covered_pages']}/{summary['total_pages']} ({summary['page_coverage_percent']}%)")
        print(f"Flow Coverage: {summary['fully_covered_flows']}/{summary['total_flows']} fully covered ({summary['flow_coverage_percent']}%)")
        print(f"Critical Flows: {summary['critical_flows_covered']}/{summary['critical_flows_total']} covered")
        print("=" * 70 + "\n")
