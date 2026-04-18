"""
Taiga Coverage Analyzer Module

Parses coverage.py JSON output and categorizes ViewSets/API modules by priority
for focused test generation. Similar to coverage_analyzer.py but for Django/Python.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ViewSetCoverage:
    """Represents coverage data for a single Django ViewSet/API module."""
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
        if self.covered_percent == 0 and self.total_lines > 50:
            return "CRITICAL"
        elif self.covered_percent < 20:
            return "HIGH"
        elif self.covered_percent < 50:
            return "MEDIUM"
        elif self.covered_percent < 80:
            return "LOW"
        else:
            return "SKIP"


INCLUDE_PATTERNS = [
    "/api.py",
    "/viewsets.py",
    "/views.py",
    "/api/",
    "/resources/",
]

EXCLUDE_PATTERNS = [
    "/tests/",
    "/test_",
    "/migrations/",
    "/admin.py",
    "/__pycache__/",
    "/management/",
]

EXCLUDE_MODULES = {
    "taiga.base",
    "taiga.conf",
    "taiga.urls",
}


class TaigaCoverageAnalyzer:
    """
    Analyzes coverage.py coverage results to prioritize ViewSets/API modules
    for test generation.
    """
    
    def __init__(self, taiga_root: Path):
        self.taiga_root = Path(taiga_root)
        self.coverage_path = self.taiga_root / "coverage" / "coverage.json"
        self.viewsets: List[ViewSetCoverage] = []
        
    def load_coverage(self) -> bool:
        """Load and parse coverage.py JSON. Returns True if successful."""
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
        """Parse coverage.py JSON structure into ViewSetCoverage objects."""
        files_data = data.get("files", {})
        
        if not files_data:
            return
        
        for file_path, file_info in files_data.items():
            if not self._is_api_file(file_path):
                continue
            
            if any(pattern in file_path for pattern in EXCLUDE_PATTERNS):
                continue
            
            module_name = self._extract_module_name(file_path)
            
            if any(module_name.startswith(excluded) for excluded in EXCLUDE_MODULES):
                continue
            
            summary = file_info.get("summary", {})
            covered_lines = summary.get("covered_lines", 0)
            num_statements = summary.get("num_statements", 0)
            missing_lines = summary.get("missing_lines", 0)
            
            if num_statements == 0:
                executed = file_info.get("executed_lines", [])
                missing = file_info.get("missing_lines", [])
                covered_lines = len(executed)
                missing_lines = len(missing)
                num_statements = covered_lines + missing_lines
            
            if num_statements == 0:
                continue
            
            covered_percent = round(100 * covered_lines / num_statements, 2)
            
            self.viewsets.append(ViewSetCoverage(
                name=module_name,
                file_path=file_path,
                covered_percent=covered_percent,
                total_lines=num_statements,
                lines_covered=covered_lines,
                lines_missed=missing_lines,
            ))
    
    def _is_api_file(self, file_path: str) -> bool:
        """Check if file is an API/ViewSet file."""
        return any(pattern in file_path for pattern in INCLUDE_PATTERNS)
    
    def _extract_module_name(self, file_path: str) -> str:
        """Extract module name from file path."""
        path = Path(file_path)
        parts = path.parts
        
        try:
            taiga_idx = parts.index("taiga")
            relevant_parts = parts[taiga_idx:]
            module = ".".join(relevant_parts)
            if module.endswith(".py"):
                module = module[:-3]
            return module
        except ValueError:
            return path.stem
    
    def get_prioritized_viewsets(
        self,
        max_count: int = 15,
        min_lines: int = 10,
        exclude_well_covered: bool = True,
        coverage_threshold: float = 70.0,
    ) -> List[ViewSetCoverage]:
        """
        Get ViewSets sorted by priority for test generation.
        """
        filtered = [
            v for v in self.viewsets
            if v.total_lines >= min_lines
            and (not exclude_well_covered or v.covered_percent < coverage_threshold)
        ]
        
        filtered.sort(key=lambda v: v.priority_score, reverse=True)
        
        return filtered[:max_count]
    
    def get_zero_coverage_viewsets(self, min_lines: int = 20) -> List[ViewSetCoverage]:
        """Get ViewSets with exactly 0% coverage."""
        return [
            v for v in self.viewsets
            if v.covered_percent == 0 and v.total_lines >= min_lines
        ]
    
    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get summary statistics of coverage data."""
        if not self.viewsets:
            return {"available": False}
        
        total_lines = sum(v.total_lines for v in self.viewsets)
        covered_lines = sum(v.lines_covered for v in self.viewsets)
        
        zero_coverage = [v for v in self.viewsets if v.covered_percent == 0]
        well_covered = [v for v in self.viewsets if v.covered_percent >= 70]
        
        return {
            "available": True,
            "total_viewsets": len(self.viewsets),
            "zero_coverage_count": len(zero_coverage),
            "well_covered_count": len(well_covered),
            "overall_coverage_percent": round(100 * covered_lines / total_lines, 2) if total_lines > 0 else 0,
            "zero_coverage_viewsets": [v.name for v in zero_coverage],
        }
    
    def print_report(self) -> None:
        """Print a human-readable coverage report."""
        if not self.viewsets:
            print("No coverage data available.")
            return
        
        print("\n" + "=" * 80)
        print("TAIGA API COVERAGE REPORT")
        print("=" * 80)
        
        sorted_viewsets = sorted(self.viewsets, key=lambda v: v.covered_percent)
        
        print(f"\n{'Module':<50} {'Coverage':>10} {'Lines':>8} {'Priority':>10}")
        print("-" * 80)
        
        for v in sorted_viewsets:
            name = v.name[-48:] if len(v.name) > 48 else v.name
            print(f"{name:<50} {v.covered_percent:>9.1f}% {v.total_lines:>8} {v.priority_label:>10}")
        
        summary = self.get_coverage_summary()
        print("\n" + "-" * 80)
        print(f"Total API Modules: {summary['total_viewsets']}")
        print(f"Zero Coverage: {summary['zero_coverage_count']}")
        print(f"Well Covered (>70%): {summary['well_covered_count']}")
        print(f"Overall Coverage: {summary['overall_coverage_percent']:.1f}%")
        print("=" * 80 + "\n")
