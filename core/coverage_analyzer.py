"""
Coverage Analyzer Module

Parses SimpleCov .resultset.json and categorizes controllers by priority
for focused test generation.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ControllerCoverage:
    """Represents coverage data for a single controller."""
    name: str
    file_path: str
    covered_percent: float
    total_lines: int
    lines_covered: int
    lines_missed: int
    
    @property
    def priority_score(self) -> float:
        """
        Calculate priority score for test generation.
        Lower coverage + more lines = higher priority (closer to 1.0).
        """
        if self.total_lines == 0:
            return 0.0
        coverage_factor = 1 - (self.covered_percent / 100)
        size_factor = min(self.total_lines / 300, 1.0)
        return round(coverage_factor * 0.7 + size_factor * 0.3, 3)
    
    @property
    def priority_label(self) -> str:
        """Human-readable priority label."""
        if self.covered_percent == 0 and self.total_lines > 100:
            return "CRITICAL"
        elif self.covered_percent < 20:
            return "HIGH"
        elif self.covered_percent < 50:
            return "MEDIUM"
        elif self.covered_percent < 80:
            return "LOW"
        else:
            return "SKIP"


EXCLUDE_CONTROLLERS = {
    "application_controller",
    "sys_controller",
    "mail_handler_controller",
    "twofa_controller",
    "twofa_backup_codes_controller",
}

EXCLUDE_PATTERNS = [
    "_helper.rb",
    "concerns/",
]


class CoverageAnalyzer:
    """
    Analyzes SimpleCov coverage results to prioritize controllers
    for test generation.
    """
    
    def __init__(self, redmine_root: Path):
        self.redmine_root = Path(redmine_root)
        self.coverage_path = self.redmine_root / "coverage" / ".resultset.json"
        self.controllers: List[ControllerCoverage] = []
        
    def load_coverage(self) -> bool:
        """Load and parse SimpleCov .resultset.json. Returns True if successful."""
        if not self.coverage_path.exists():
            return False
        
        try:
            data = json.loads(self.coverage_path.read_text(encoding="utf-8"))
            self._parse_coverage_data(data)
            return True
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to parse coverage data: {e}")
            return False
    
    def _parse_coverage_data(self, data: Dict[str, Any]) -> None:
        """Parse SimpleCov JSON structure into ControllerCoverage objects.
        
        SimpleCov stores results from multiple test suites (e.g., 'Unit Tests', 'Minitest').
        This method merges coverage from all suites by taking the maximum hit count for each line,
        matching SimpleCov's merging behavior for accurate reporting.
        """
        # Collect all coverage data from all test suites
        all_suites: List[Dict[str, Any]] = []
        for key, value in data.items():
            if isinstance(value, dict) and "coverage" in value:
                all_suites.append(value["coverage"])
        
        if not all_suites:
            return
        
        # Merge coverage: collect all file paths and merge line data
        merged_coverage: Dict[str, List[Optional[int]]] = {}
        
        for suite_coverage in all_suites:
            for file_path, file_data in suite_coverage.items():
                if isinstance(file_data, dict):
                    lines = file_data.get("lines", [])
                else:
                    lines = file_data
                
                if file_path not in merged_coverage:
                    merged_coverage[file_path] = list(lines)
                else:
                    # Merge by taking max hit count for each line
                    existing = merged_coverage[file_path]
                    for i, hit in enumerate(lines):
                        if i < len(existing):
                            if hit is not None:
                                if existing[i] is None:
                                    existing[i] = hit
                                else:
                                    existing[i] = max(existing[i], hit)
                        else:
                            existing.append(hit)
        
        # Process merged coverage into ControllerCoverage objects
        for file_path, lines in merged_coverage.items():
            if "controller" not in file_path.lower():
                continue
            
            if any(pattern in file_path for pattern in EXCLUDE_PATTERNS):
                continue
            
            name = Path(file_path).stem
            
            if name in EXCLUDE_CONTROLLERS:
                continue
            
            relevant_lines = [l for l in lines if l is not None]
            if not relevant_lines:
                continue
                
            covered = sum(1 for l in relevant_lines if l and l > 0)
            total = len(relevant_lines)
            
            self.controllers.append(ControllerCoverage(
                name=name,
                file_path=file_path,
                covered_percent=round(100 * covered / total, 2) if total > 0 else 0,
                total_lines=total,
                lines_covered=covered,
                lines_missed=total - covered,
            ))
    
    def get_prioritized_controllers(
        self,
        max_count: int = 15,
        min_lines: int = 20,
        exclude_well_covered: bool = True,
        coverage_threshold: float = 70.0,
    ) -> List[ControllerCoverage]:
        """
        Get controllers sorted by priority for test generation.
        
        Args:
            max_count: Maximum number of controllers to return
            min_lines: Minimum lines threshold (skip tiny controllers)
            exclude_well_covered: Skip controllers above coverage_threshold
            coverage_threshold: Coverage % above which to skip
        
        Returns:
            List of ControllerCoverage sorted by priority (highest first)
        """
        filtered = [
            c for c in self.controllers
            if c.total_lines >= min_lines
            and (not exclude_well_covered or c.covered_percent < coverage_threshold)
        ]
        
        filtered.sort(key=lambda c: c.priority_score, reverse=True)
        
        return filtered[:max_count]
    
    def get_zero_coverage_controllers(self, min_lines: int = 30) -> List[ControllerCoverage]:
        """Get controllers with exactly 0% coverage."""
        return [
            c for c in self.controllers
            if c.covered_percent == 0 and c.total_lines >= min_lines
        ]
    
    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get summary statistics of coverage data."""
        if not self.controllers:
            return {"available": False}
        
        total_lines = sum(c.total_lines for c in self.controllers)
        covered_lines = sum(c.lines_covered for c in self.controllers)
        
        zero_coverage = [c for c in self.controllers if c.covered_percent == 0]
        well_covered = [c for c in self.controllers if c.covered_percent >= 70]
        
        return {
            "available": True,
            "total_controllers": len(self.controllers),
            "zero_coverage_count": len(zero_coverage),
            "well_covered_count": len(well_covered),
            "overall_coverage_percent": round(100 * covered_lines / total_lines, 2) if total_lines > 0 else 0,
            "zero_coverage_controllers": [c.name for c in zero_coverage],
        }
    
    def print_report(self) -> None:
        """Print a human-readable coverage report."""
        if not self.controllers:
            print("No coverage data available.")
            return
        
        print("\n" + "=" * 70)
        print("CONTROLLER COVERAGE REPORT")
        print("=" * 70)
        
        sorted_controllers = sorted(self.controllers, key=lambda c: c.covered_percent)
        
        print(f"\n{'Controller':<40} {'Coverage':>10} {'Lines':>8} {'Priority':>10}")
        print("-" * 70)
        
        for c in sorted_controllers:
            print(f"{c.name:<40} {c.covered_percent:>9.1f}% {c.total_lines:>8} {c.priority_label:>10}")
        
        summary = self.get_coverage_summary()
        print("\n" + "-" * 70)
        print(f"Total Controllers: {summary['total_controllers']}")
        print(f"Zero Coverage: {summary['zero_coverage_count']}")
        print(f"Well Covered (>70%): {summary['well_covered_count']}")
        print(f"Overall Coverage: {summary['overall_coverage_percent']:.1f}%")
        print("=" * 70 + "\n")
