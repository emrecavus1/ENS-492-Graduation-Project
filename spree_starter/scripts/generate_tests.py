#!/usr/bin/env python3
"""
Coverage-Driven Test Generator for Spree Commerce

This script generates RSpec request specs for the Spree Store API using an LLM,
with prompts focused on API endpoints that need coverage improvement.

Usage:
    python scripts/generate_tests.py                    # Generate API tests
    python scripts/generate_tests.py --focus cart,products  # Focus on specific resources
    python scripts/generate_tests.py --report           # Print API summary
    python scripts/generate_tests.py --dry-run          # Print prompt without generating
"""
import os
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPREE_ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = SPREE_ROOT / "spec" / "generated" / "store_api_spec.rb"

sys.path.insert(0, str(PROJECT_ROOT))

from core.spree_prompt_builder import SpreePromptBuilder
from core.spree_route_mapper import (
    SPREE_STORE_API_RESOURCES,
    get_api_statistics,
    get_all_endpoints,
)


def validate_generated_code(ruby_code: str) -> None:
    """Validate the generated Ruby code meets basic requirements."""
    if "```" in ruby_code:
        raise SystemExit("Model returned markdown fences. Refine prompt / strip fences.")
    
    if "require 'rails_helper'" not in ruby_code and 'require "rails_helper"' not in ruby_code:
        raise SystemExit("Generated code is missing require 'rails_helper'.")
    
    if "RSpec.describe" not in ruby_code:
        raise SystemExit("Generated code is not an RSpec test (must contain 'RSpec.describe').")
    
    if "it " not in ruby_code and "it(" not in ruby_code:
        raise SystemExit("No RSpec examples found (missing 'it' blocks).")


def print_api_report() -> None:
    """Print API endpoint summary and exit."""
    stats = get_api_statistics()
    
    print("\n" + "=" * 70)
    print("SPREE STORE API REPORT")
    print("=" * 70)
    
    print(f"\nTotal Resources: {stats['total_resources']}")
    print(f"Total Endpoints: {stats['total_endpoints']}")
    print(f"Public Endpoints: {stats['public_endpoints']}")
    print(f"Authenticated Endpoints: {stats['authenticated_endpoints']}")
    print(f"Safe for Testing: {stats['safe_endpoints']}")
    
    print("\nEndpoints by Method:")
    for method, count in stats['by_method'].items():
        print(f"  {method}: {count}")
    
    print("\n" + "-" * 70)
    print("RESOURCES:")
    print("-" * 70)
    
    for name, resource in SPREE_STORE_API_RESOURCES.items():
        endpoint_count = len(resource.endpoints)
        auth_count = sum(1 for e in resource.endpoints if e.requires_auth)
        print(f"\n{name}:")
        print(f"  Base: {resource.base_path}")
        print(f"  Endpoints: {endpoint_count} ({auth_count} authenticated)")
        for endpoint in resource.endpoints:
            auth_marker = " [auth]" if endpoint.requires_auth else ""
            safe_marker = " [skip]" if not endpoint.safe_for_coverage else ""
            print(f"    {endpoint.method:6} {endpoint.path}{auth_marker}{safe_marker}")
    
    print("\n" + "=" * 70)


def generate_tests(prompt: str, model: str = "gpt-4.1-mini") -> str:
    """Generate tests using the LLM."""
    from dotenv import load_dotenv
    from langchain_openai import ChatOpenAI
    
    load_dotenv()
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY env var. Set it before running.")
    
    llm = ChatOpenAI(model=model, temperature=0)
    return llm.invoke(prompt).content


def main():
    parser = argparse.ArgumentParser(
        description="Generate Spree Commerce API tests using coverage-driven prompts"
    )
    parser.add_argument(
        "--focus",
        type=str,
        help="Comma-separated list of resources to focus on (e.g., 'products,cart,checkout')"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print API endpoint report and exit"
    )
    parser.add_argument(
        "--test-count",
        type=int,
        default=20,
        help="Number of test examples to generate (default: 20)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4.1-mini",
        help="OpenAI model to use (default: gpt-4.1-mini)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompt without generating tests"
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Exclude authenticated endpoints from tests"
    )
    
    args = parser.parse_args()
    
    if args.report:
        print_api_report()
        return
    
    builder = SpreePromptBuilder(SPREE_ROOT)
    
    if args.focus:
        focus_list = [r.strip() for r in args.focus.split(",")]
        print(f"Focusing on resources: {focus_list}")
        prompt = builder.build_focused_prompt(
            resources=focus_list,
            test_count=args.test_count,
        )
    else:
        print("Building comprehensive API test prompt...")
        prompt = builder.build_prompt(
            include_auth_tests=not args.no_auth,
            test_count=args.test_count,
        )
        
        summary = builder.get_coverage_summary()
        print(f"\nAPI Summary:")
        print(f"  Total Resources: {summary['total_resources']}")
        print(f"  Total Endpoints: {summary['total_endpoints']}")
        print(f"  Safe Endpoints: {summary['safe_endpoints']}")
        print()
    
    if args.dry_run:
        print("=" * 70)
        print("GENERATED PROMPT (dry run):")
        print("=" * 70)
        print(prompt)
        return
    
    print(f"Generating tests with {args.model}...")
    ruby_code = generate_tests(prompt, model=args.model)
    
    validate_generated_code(ruby_code)
    
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(ruby_code, encoding="utf-8")
    print(f"Wrote: {OUT_FILE}")
    
    example_count = ruby_code.count(" it ") + ruby_code.count(" it(")
    print(f"Generated approximately {example_count} test examples.")
    
    print("\nTo run the generated tests:")
    print(f"  cd {SPREE_ROOT}")
    print("  bundle exec rspec spec/generated/store_api_spec.rb")
    print("\nTo run with coverage:")
    print("  COVERAGE=1 bundle exec rspec spec/generated/store_api_spec.rb")


if __name__ == "__main__":
    main()
