"""
Coverage-Driven Test Generator for SauceDemo

This script generates Python Playwright tests using an LLM,
with prompts focused on user flows that need coverage improvement.

Usage:
    python generate_tests.py                    # Use coverage-driven prompt
    python generate_tests.py --full             # Use full prompt (ignore coverage)
    python generate_tests.py --focus login,checkout  # Focus on specific flows
    python generate_tests.py --report           # Print coverage report only
"""
import os
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAUCEDEMO_ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = SAUCEDEMO_ROOT / "tests" / "generated" / "test_generated_suite.py"

sys.path.insert(0, str(PROJECT_ROOT))

from core.saucedemo_prompt_builder import SauceDemoPromptBuilder
from core.saucedemo_coverage_analyzer import SauceDemoCoverageAnalyzer


FULL_PROMPT = """
You are generating Python Playwright integration tests for SauceDemo (https://www.saucedemo.com).

OUTPUT FORMAT (STRICT):
- Output ONLY a single Python file (no markdown, no explanations).
- Use pytest as the test framework with playwright fixtures.
- Import: from playwright.sync_api import Page, expect

BASE APPLICATION INFO:
- URL: https://www.saucedemo.com
- Valid users: standard_user, problem_user, performance_glitch_user, error_user, visual_user
- Locked user: locked_out_user (login should fail)
- Password for all users: secret_sauce

AVAILABLE PAGES:
1. Login (/) - username field (#user-name), password field (#password), login button (#login-button)
2. Inventory (/inventory.html) - product list, add to cart buttons, sort dropdown, cart icon
3. Cart (/cart.html) - cart items, checkout button, remove buttons
4. Checkout Step One (/checkout-step-one.html) - first name, last name, postal code, continue
5. Checkout Step Two (/checkout-step-two.html) - order summary, finish button
6. Checkout Complete (/checkout-complete.html) - confirmation message

SUITE REQUIREMENTS:
- Generate 15-20 separate test functions
- Use descriptive test names (test_*)
- Create a logged_in_page fixture for tests requiring authentication
- Use page.locator() with CSS selectors
- Use expect() for Playwright assertions
- Handle page navigation with wait_for_url() when needed

CRITICAL FLOWS TO COVER:
1. Successful login with standard_user
2. Failed login with invalid credentials
3. Locked out user error message
4. Add single item to cart
5. Add multiple items to cart
6. Remove item from cart
7. Complete checkout flow (all steps)
8. Checkout form validation (empty fields)
9. Sort products (price, name)
10. View product details
11. Logout functionality

OUTPUT ONLY THE PYTHON CODE. NO MARKDOWN FENCES.
"""


def validate_generated_code(python_code: str) -> None:
    """Validate the generated Python code meets basic requirements."""
    if "```" in python_code:
        raise SystemExit("Model returned markdown fences. Refine prompt / strip fences.")

    if "from playwright" not in python_code:
        raise SystemExit("Generated code is missing playwright import.")

    if "def test_" not in python_code:
        raise SystemExit("No pytest test functions found (must have 'def test_').")

    if "page" not in python_code.lower():
        raise SystemExit("Generated code doesn't use Page fixture.")


def print_coverage_report() -> None:
    """Print coverage report and exit."""
    analyzer = SauceDemoCoverageAnalyzer(SAUCEDEMO_ROOT)
    if analyzer.load_coverage():
        analyzer.print_report()
    else:
        print("No coverage data found. Run tests first to generate coverage.")
        print("\nTo generate initial coverage, run:")
        print("  python -m pytest tests/generated/ --headed")
        sys.exit(1)


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
        description="Generate SauceDemo Playwright tests using coverage-driven prompts"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Use full prompt instead of coverage-driven prompt"
    )
    parser.add_argument(
        "--focus",
        type=str,
        help="Comma-separated list of flows to focus on (e.g., 'successful_login,complete_checkout')"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print coverage report and exit"
    )
    parser.add_argument(
        "--test-count",
        type=int,
        default=15,
        help="Number of test functions to generate (default: 15)"
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

    args = parser.parse_args()

    if args.report:
        print_coverage_report()
        return

    builder = SauceDemoPromptBuilder(SAUCEDEMO_ROOT)

    if args.full:
        prompt = FULL_PROMPT
        print("Using full prompt (ignoring coverage data)")
    elif args.focus:
        focus_flows = [f.strip() for f in args.focus.split(",")]
        prompt = builder.build_focused_prompt(
            focus_flows=focus_flows,
            test_count=args.test_count,
        )
        print(f"Focusing on flows: {', '.join(focus_flows)}")
    else:
        prompt = builder.build_prompt(test_count=args.test_count)
        summary = builder.get_coverage_summary()
        if summary.get("available"):
            print(f"Coverage-driven mode: {summary['page_coverage_percent']}% page coverage")
            print(f"  Uncovered pages: {', '.join(summary.get('uncovered_pages', []))}")
        else:
            print("No previous coverage data - using default priorities")

    if args.dry_run:
        print("\n" + "=" * 60)
        print("PROMPT PREVIEW (dry-run mode)")
        print("=" * 60)
        print(prompt)
        return

    print(f"\nGenerating tests with {args.model}...")
    generated_code = generate_tests(prompt, model=args.model)

    if "```python" in generated_code:
        generated_code = generated_code.split("```python")[1].split("```")[0].strip()
    elif "```" in generated_code:
        generated_code = generated_code.split("```")[1].split("```")[0].strip()

    validate_generated_code(generated_code)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generated_code, encoding="utf-8")
    print(f"\nGenerated tests written to: {OUT_FILE}")

    test_count = generated_code.count("def test_")
    print(f"Generated {test_count} test functions")
    
    print("\nTo run the generated tests:")
    print(f"  cd {SAUCEDEMO_ROOT}")
    print("  python -m pytest tests/generated/ -v")
    print("\nTo run with visible browser:")
    print("  python -m pytest tests/generated/ -v --headed")


if __name__ == "__main__":
    main()
