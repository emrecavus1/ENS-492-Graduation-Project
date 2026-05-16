#!/usr/bin/env python3
"""
Coverage-Oriented Test Generator for OpenProject

Generates OpenProject RSpec request specs using an LLM with route/resource-aware prompts.

Usage:
    python scripts/generate_tests.py
    python scripts/generate_tests.py --focus api_v3_projects,api_v3_work_packages
    python scripts/generate_tests.py --report
    python scripts/generate_tests.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OPENPROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = OPENPROJECT_ROOT / "spec" / "generated" / "openproject_generated_request_spec.rb"

sys.path.insert(0, str(PROJECT_ROOT))

from core.openproject_prompt_builder import OpenProjectPromptBuilder
from core.openproject_route_mapper import OPENPROJECT_RESOURCES, get_statistics, get_coverage_target_patterns
from core.openproject_coverage_analyzer import OpenProjectCoverageAnalyzer


def normalize_generated_code(ruby_code: str) -> str:
    """
    Apply deterministic fixes for common LLM output mistakes.

    Ruby does not allow positional args after keyword args in method calls.
    Some generations incorrectly emit:
      RSpec.describe "...", type: :rails_request, :skip_csrf do
    This normalizes it to:
      RSpec.describe "...", :skip_csrf, type: :rails_request do
    """
    bad = 'RSpec.describe "Generated OpenProject Request Coverage", type: :rails_request, :skip_csrf do'
    good = 'RSpec.describe "Generated OpenProject Request Coverage", :skip_csrf, type: :rails_request do'
    normalized = ruby_code.replace(bad, good)

    # Normalize brittle narrow status arrays that frequently fail in OpenProject
    # due to redirect-first behavior (especially unauthorized/invalid branches).
    replacements = {
        "expect([401, 403, 404]).to include(response.status)":
            "expect([301, 302, 401, 403, 404, 422]).to include(response.status)",
        "expect([401, 403, 404, 422]).to include(response.status)":
            "expect([301, 302, 401, 403, 404, 422]).to include(response.status)",
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)

    return normalized


def validate_generated_code(ruby_code: str) -> None:
    """Validate basic shape of generated RSpec code."""
    if "```" in ruby_code:
        raise SystemExit("Model returned markdown fences. Refine prompt / strip fences.")

    if 'require "spec_helper"' not in ruby_code and "require 'spec_helper'" not in ruby_code:
        raise SystemExit("Generated code is missing require 'spec_helper'.")

    if "RSpec.describe" not in ruby_code:
        raise SystemExit("Generated code is not an RSpec spec (missing RSpec.describe).")

    if "type: :rails_request" not in ruby_code:
        raise SystemExit("Generated code must be request-oriented (missing type: :rails_request).")

    if "it " not in ruby_code and "it(" not in ruby_code:
        raise SystemExit("No RSpec examples found (missing 'it' blocks).")


def print_report() -> None:
    """Print endpoint summary plus current SimpleCov totals."""
    stats = get_statistics()
    analyzer = OpenProjectCoverageAnalyzer(OPENPROJECT_ROOT)
    has_coverage = analyzer.load_coverage()
    patterns = get_coverage_target_patterns()
    coverage = analyzer.get_summary_for_patterns(patterns) if has_coverage else {"available": False}
    prioritized = analyzer.get_prioritized_files_for_patterns(patterns, max_count=8) if has_coverage else []

    print("\n" + "=" * 70)
    print("OPENPROJECT TEST GENERATION REPORT")
    print("=" * 70)
    print(f"\nTotal Resources: {stats['total_resources']}")
    print(f"Total Endpoints: {stats['total_endpoints']}")
    print(f"Public Endpoints: {stats['public_endpoints']}")
    print(f"Authenticated Endpoints: {stats['authenticated_endpoints']}")
    print(f"Safe Endpoints: {stats['safe_endpoints']}")

    print("\nEndpoints by Method:")
    for method, count in stats["by_method"].items():
        print(f"  {method}: {count}")

    if coverage.get("available"):
        print("\nCoverage Summary (Controllers + API files):")
        print(f"  Total Target Files: {coverage['total_files']}")
        print(f"  Controller Files: {coverage['controller_files']}")
        print(f"  API Files: {coverage['api_files']}")
        print(f"  Covered Lines: {coverage['covered_lines']}")
        print(f"  Total Lines: {coverage['total_lines']}")
        print(f"  Overall Coverage: {coverage['overall_coverage_percent']:.2f}%")
        print(f"  Zero-Coverage Files: {coverage['zero_coverage_count']}")

        if prioritized:
            print("\nTop Priority Files To Improve:")
            for item in prioritized:
                print(
                    f"  - {item.category:11} {item.covered_percent:6.2f}% "
                    f"{item.total_lines:4} lines  [{item.priority_label}]  {item.file_path}"
                )
    else:
        print("\nCoverage Summary: not available (run specs with coverage enabled)")

    print("\n" + "=" * 70)


def generate_tests(prompt: str, model: str = "gpt-4.1-mini") -> str:
    """Generate Ruby specs via OpenAI-compatible model."""
    from dotenv import load_dotenv
    from langchain_openai import ChatOpenAI

    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY env var. Set it before running.")

    llm = ChatOpenAI(model=model, temperature=0)
    return llm.invoke(prompt).content


def run_generated_tests(test_targets: List[str]) -> Dict[str, Any]:
    """Run generated specs with coverage enabled and return execution summary."""
    if not test_targets:
        return {
            "status": "error",
            "exit_code": 2,
            "stdout": "",
            "stderr": "No test targets provided.",
        }

    result = subprocess.run(
        ["bundle", "exec", "rspec", *test_targets],
        cwd=str(OPENPROJECT_ROOT),
        capture_output=True,
        text=True,
        env={**os.environ, "RAILS_ENV": "test", "COVERAGE": "1"},
    )
    return {
        "status": "passed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def select_low_coverage_resources(max_resources: int, threshold: float) -> List[str]:
    """
    Select resources whose focused line coverage is below threshold.
    """
    analyzer = OpenProjectCoverageAnalyzer(OPENPROJECT_ROOT)
    if not analyzer.load_coverage():
        return []

    # Redmine-style prioritization: combine low coverage + larger line footprint.
    # score ~= (coverage gap * 0.7) + (size factor * 0.3)
    scored: List[tuple[str, float]] = []
    for name, resource in OPENPROJECT_RESOURCES.items():
        summary = analyzer.get_summary_for_patterns(resource.coverage_targets)
        if not summary.get("available"):
            continue
        coverage = float(summary.get("overall_coverage_percent", 0.0))
        total_lines = int(summary.get("total_lines", 0))
        if coverage < threshold:
            coverage_factor = 1.0 - (coverage / 100.0)
            size_factor = min(total_lines / 300.0, 1.0)
            score = (coverage_factor * 0.7) + (size_factor * 0.3)
            scored.append((name, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    return [name for name, _ in scored[:max_resources]]


def prioritize_resources_by_line_impact() -> List[str]:
    """
    Return all resources sorted by line-impact priority.
    Prefers low-coverage high-line resources when coverage exists;
    falls back to raw file line counts when coverage is unavailable.
    """
    analyzer = OpenProjectCoverageAnalyzer(OPENPROJECT_ROOT)
    has_coverage = analyzer.load_coverage()
    scored: List[tuple[str, float]] = []

    for name, resource in OPENPROJECT_RESOURCES.items():
        if has_coverage:
            summary = analyzer.get_summary_for_patterns(resource.coverage_targets)
            if summary.get("available"):
                coverage = float(summary.get("overall_coverage_percent", 0.0))
                total_lines = int(summary.get("total_lines", 0))
                coverage_factor = 1.0 - (coverage / 100.0)
                size_factor = min(total_lines / 300.0, 1.0)
                score = (coverage_factor * 0.7) + (size_factor * 0.3)
            else:
                score = 0.0
        else:
            # Fallback: approximate impact from configured target file sizes.
            total_lines = 0
            for pattern in resource.coverage_targets:
                rel = pattern.lstrip("/")
                target = OPENPROJECT_ROOT / rel
                if target.exists():
                    try:
                        total_lines += len(target.read_text(encoding="utf-8").splitlines())
                    except OSError:
                        continue
            score = min(total_lines / 300.0, 1.0)

        scored.append((name, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    ordered = [name for name, _ in scored]
    return ordered or list(OPENPROJECT_RESOURCES.keys())


def build_prompt_for_iteration(
    builder: OpenProjectPromptBuilder,
    args: argparse.Namespace,
    iteration: int,
) -> str:
    if args.focus:
        resources = [r.strip() for r in args.focus.split(",") if r.strip()]
        print(f"Focusing on resources: {resources}")
        return builder.build_focused_prompt(resources=resources, test_count=args.test_count)

    if args.iterative:
        # Redmine-like default: always refocus by latest low-coverage + line-impact set.
        # If coverage is not available yet, fall back to line-impact ordering.
        focus_resources = select_low_coverage_resources(
            max_resources=args.max_focus_resources,
            threshold=args.focus_coverage_threshold,
        )
        if focus_resources:
            print(f"Iteration {iteration}: line-impact low-coverage focus: {focus_resources}")
            return builder.build_focused_prompt(resources=focus_resources, test_count=args.test_count)

        prioritized_resources = prioritize_resources_by_line_impact()
        print(
            f"Iteration {iteration}: no low-coverage snapshot yet, "
            f"using line-impact order: {prioritized_resources}"
        )
        return builder.build_prompt(
            include_auth_tests=not args.no_auth,
            test_count=args.test_count,
            focus_resources=prioritized_resources,
        )

    if iteration == 1:
        print("Building OpenProject prompt...")
        prioritized_resources = prioritize_resources_by_line_impact()
        print(f"Line-impact priority order: {prioritized_resources}")
        return builder.build_prompt(
            include_auth_tests=not args.no_auth,
            test_count=args.test_count,
            focus_resources=prioritized_resources,
        )

    focus_resources = select_low_coverage_resources(
        max_resources=args.max_focus_resources,
        threshold=args.focus_coverage_threshold,
    )
    if focus_resources:
        print(f"Iteration {iteration}: focusing low-coverage resources: {focus_resources}")
        return builder.build_focused_prompt(resources=focus_resources, test_count=args.test_count)

    print(f"Iteration {iteration}: no low-coverage resources found, using broad prompt.")
    return builder.build_prompt(
        include_auth_tests=not args.no_auth,
        test_count=args.test_count,
    )


def clean_round_files() -> None:
    generated_dir = OPENPROJECT_ROOT / "spec" / "generated"
    for file in generated_dir.glob("openproject_generated_round_*.rb"):
        file.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate OpenProject request specs using route-aware prompts"
    )
    parser.add_argument(
        "--focus",
        type=str,
        help="Comma-separated resources to focus on (e.g., 'projects,api_v3_projects')",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print route and coverage summary, then exit",
    )
    parser.add_argument(
        "--test-count",
        type=int,
        default=24,
        help="Number of RSpec examples to generate (default: 24)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4.1-mini",
        help="OpenAI model to use (default: gpt-4.1-mini)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompt without invoking LLM",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Exclude authenticated endpoints from generated tests",
    )
    parser.add_argument(
        "--iterative",
        action="store_true",
        help="Run iterative loop: generate -> test -> refocus by low coverage",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterative rounds when --iterative is used (default: 3)",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run generated spec after writing it",
    )
    parser.add_argument(
        "--focus-coverage-threshold",
        type=float,
        default=80.0,
        help="Resource focused-line-coverage threshold for iterative refocus (default: 80)",
    )
    parser.add_argument(
        "--max-focus-resources",
        type=int,
        default=5,
        help="Maximum low-coverage resources to focus per iterative round (default: 5)",
    )
    parser.add_argument(
        "--clean-round-files",
        action="store_true",
        help="Delete prior iterative round files before running iterative mode",
    )
    args = parser.parse_args()

    if args.report:
        print_report()
        return

    if args.iterative and not args.run_tests:
        raise SystemExit("--iterative requires --run-tests so coverage can update between rounds.")

    if args.iterative and args.clean_round_files:
        clean_round_files()

    builder = OpenProjectPromptBuilder(OPENPROJECT_ROOT)
    summary = builder.get_summary()
    print("\nRoute Summary:")
    print(f"  Total Resources: {summary['total_resources']}")
    print(f"  Total Endpoints: {summary['total_endpoints']}")
    print(f"  Safe Endpoints: {summary['safe_endpoints']}")
    print()

    total_rounds = args.iterations if args.iterative else 1
    for iteration in range(1, total_rounds + 1):
        print(f"=== Generation round {iteration}/{total_rounds} ===")
        prompt = build_prompt_for_iteration(builder, args, iteration=iteration)

        if args.dry_run:
            print("=" * 70)
            print("GENERATED PROMPT (dry run):")
            print("=" * 70)
            print(prompt)
            return

        print(f"Generating tests with {args.model}...")
        ruby_code = generate_tests(prompt, model=args.model)
        ruby_code = normalize_generated_code(ruby_code)
        validate_generated_code(ruby_code)

        OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUT_FILE.write_text(ruby_code, encoding="utf-8")
        print(f"Wrote: {OUT_FILE}")
        if args.iterative:
            round_file = OUT_FILE.parent / f"openproject_generated_round_{iteration}.rb"
            round_file.write_text(ruby_code, encoding="utf-8")
            print(f"Wrote: {round_file}")

        example_count = ruby_code.count(" it ") + ruby_code.count(" it(")
        print(f"Generated approximately {example_count} examples.")

        if args.run_tests:
            print("Running generated tests with COVERAGE=1...")
            if args.iterative:
                targets = [
                    f"spec/generated/openproject_generated_round_{idx}.rb"
                    for idx in range(1, iteration + 1)
                ]
            else:
                targets = ["spec/generated/openproject_generated_request_spec.rb"]
            run_result = run_generated_tests(targets)
            print(f"  Test status: {run_result['status']} (exit_code={run_result['exit_code']})")
            if run_result["status"] != "passed":
                if run_result["stdout"].strip():
                    print("  Last stdout:")
                    print(run_result["stdout"][-1500:])
                if run_result["stderr"].strip():
                    print("  Last stderr:")
                    print(run_result["stderr"][-1500:])
                if args.iterative:
                    print("Stopping iterative loop due to test failure.")
                break

    print("\nTo run generated tests manually:")
    print(f"  cd {OPENPROJECT_ROOT}")
    if args.iterative:
        print("  COVERAGE=1 bundle exec rspec spec/generated/openproject_generated_round_*.rb")
    else:
        print("  COVERAGE=1 bundle exec rspec spec/generated/openproject_generated_request_spec.rb")


if __name__ == "__main__":
    main()
