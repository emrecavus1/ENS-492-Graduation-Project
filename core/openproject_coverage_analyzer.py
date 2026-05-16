"""
OpenProject Coverage Analyzer Module

Parses SimpleCov .resultset.json and provides focused coverage statistics
for OpenProject controllers and API-heavy Ruby files.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FileCoverage:
    name: str
    file_path: str
    category: str
    covered_percent: float
    total_lines: int
    lines_covered: int
    lines_missed: int

    @property
    def priority_score(self) -> float:
        if self.total_lines == 0:
            return 0.0
        coverage_factor = 1 - (self.covered_percent / 100.0)
        size_factor = min(self.total_lines / 300.0, 1.0)
        return round(coverage_factor * 0.7 + size_factor * 0.3, 3)

    @property
    def priority_label(self) -> str:
        if self.covered_percent == 0 and self.total_lines >= 80:
            return "CRITICAL"
        if self.covered_percent < 20:
            return "HIGH"
        if self.covered_percent < 50:
            return "MEDIUM"
        if self.covered_percent < 80:
            return "LOW"
        return "SKIP"


class OpenProjectCoverageAnalyzer:
    """Analyze SimpleCov output for OpenProject."""

    def __init__(self, openproject_root: Path):
        self.openproject_root = Path(openproject_root)
        self.coverage_path = self.openproject_root / "coverage" / ".resultset.json"
        self.files: List[FileCoverage] = []

    def load_coverage(self) -> bool:
        if not self.coverage_path.exists():
            return False

        try:
            data = json.loads(self.coverage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False

        self.files = []
        merged = self._merge_suites(data)
        self._extract_openproject_targets(merged)
        return len(self.files) > 0

    def _merge_suites(self, data: Dict[str, Any]) -> Dict[str, List[Optional[int]]]:
        suites: List[Dict[str, Any]] = []
        for value in data.values():
            if isinstance(value, dict) and "coverage" in value:
                suites.append(value["coverage"])

        merged: Dict[str, List[Optional[int]]] = {}
        for suite in suites:
            for file_path, file_data in suite.items():
                lines = file_data.get("lines", []) if isinstance(file_data, dict) else file_data
                if file_path not in merged:
                    merged[file_path] = list(lines)
                    continue

                existing = merged[file_path]
                for idx, hit in enumerate(lines):
                    if idx >= len(existing):
                        existing.append(hit)
                        continue
                    if hit is None:
                        continue
                    if existing[idx] is None:
                        existing[idx] = hit
                    else:
                        existing[idx] = max(existing[idx], hit)
        return merged

    def _extract_openproject_targets(self, merged: Dict[str, List[Optional[int]]]) -> None:
        for file_path, lines in merged.items():
            category = self._categorize(file_path)
            if category is None:
                continue

            relevant = [line for line in lines if line is not None]
            if not relevant:
                continue

            covered = sum(1 for line in relevant if line and line > 0)
            total = len(relevant)

            self.files.append(
                FileCoverage(
                    name=Path(file_path).stem,
                    file_path=file_path,
                    category=category,
                    covered_percent=round(100.0 * covered / total, 2) if total > 0 else 0.0,
                    total_lines=total,
                    lines_covered=covered,
                    lines_missed=total - covered,
                )
            )

    def _categorize(self, file_path: str) -> Optional[str]:
        normalized = file_path.replace("\\", "/")
        if "/app/controllers/" in normalized and normalized.endswith(".rb"):
            return "controllers"
        if "/lib/api/" in normalized and normalized.endswith(".rb"):
            return "api_lib"
        return None

    def get_summary(self) -> Dict[str, Any]:
        return self._summary_for_files(self.files)

    def get_summary_for_patterns(self, path_patterns: List[str]) -> Dict[str, Any]:
        """
        Get summary limited to files whose paths include any of the patterns.
        """
        selected = self._files_matching_patterns(path_patterns)
        summary = self._summary_for_files(selected)
        summary["path_patterns"] = path_patterns
        return summary

    def get_prioritized_files(self, max_count: int = 10, min_lines: int = 30) -> List[FileCoverage]:
        filtered = [f for f in self.files if f.total_lines >= min_lines and f.covered_percent < 80]
        filtered.sort(key=lambda f: f.priority_score, reverse=True)
        return filtered[:max_count]

    def get_prioritized_files_for_patterns(
        self,
        path_patterns: List[str],
        max_count: int = 10,
        min_lines: int = 20,
    ) -> List[FileCoverage]:
        selected = self._files_matching_patterns(path_patterns)
        filtered = [f for f in selected if f.total_lines >= min_lines and f.covered_percent < 80]
        filtered.sort(key=lambda f: f.priority_score, reverse=True)
        return filtered[:max_count]

    def _files_matching_patterns(self, path_patterns: List[str]) -> List[FileCoverage]:
        if not path_patterns:
            return self.files
        return [
            f
            for f in self.files
            if any(pattern in f.file_path.replace("\\", "/") for pattern in path_patterns)
        ]

    def _summary_for_files(self, files: List[FileCoverage]) -> Dict[str, Any]:
        if not files:
            return {"available": False}

        total_lines = sum(f.total_lines for f in files)
        covered_lines = sum(f.lines_covered for f in files)
        controllers = [f for f in files if f.category == "controllers"]
        api_lib = [f for f in files if f.category == "api_lib"]
        zero_coverage = [f for f in files if f.covered_percent == 0]

        return {
            "available": True,
            "total_files": len(files),
            "controller_files": len(controllers),
            "api_files": len(api_lib),
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "overall_coverage_percent": round(100.0 * covered_lines / total_lines, 2) if total_lines > 0 else 0.0,
            "zero_coverage_count": len(zero_coverage),
            "zero_coverage_files": [f.file_path for f in zero_coverage[:10]],
        }
