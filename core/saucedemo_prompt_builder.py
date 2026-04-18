"""
SauceDemo Prompt Builder Module

Generates focused Playwright test prompts based on UI coverage analysis.
Creates prompts that prioritize uncovered pages and critical user flows.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
from pathlib import Path

from core.saucedemo_coverage_analyzer import SauceDemoCoverageAnalyzer, FlowCoverage
from core.saucedemo_page_mapper import (
    SAUCEDEMO_PAGES,
    SAUCEDEMO_FLOWS,
    PageInfo,
    UserFlow,
    get_flows_by_priority,
)


PRESCRIPTIVE_PROMPT_TEMPLATE = '''Generate a Python Playwright test file for SauceDemo (https://www.saucedemo.com). Output ONLY Python code, no markdown.

COMPLETE EXAMPLE (follow this exact format):

import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://www.saucedemo.com"


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Login as standard_user and return the page."""
    page.goto(BASE_URL)
    page.locator("#user-name").fill("standard_user")
    page.locator("#password").fill("secret_sauce")
    page.locator("#login-button").click()
    page.wait_for_url("**/inventory.html")
    return page


class TestSauceDemoSuite:
    """Generated test suite for SauceDemo."""

    def test_successful_login(self, page: Page):
        """Test successful login with valid credentials."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        assert "inventory.html" in page.url
        expect(page.locator(".inventory_list")).to_be_visible()

    def test_failed_login_invalid_user(self, page: Page):
        """Test login failure with invalid credentials."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("invalid_user")
        page.locator("#password").fill("wrong_password")
        page.locator("#login-button").click()
        expect(page.locator('[data-test="error"]')).to_be_visible()

    def test_add_item_to_cart(self, logged_in_page: Page):
        """Test adding an item to cart."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("1")

    def test_complete_checkout(self, logged_in_page: Page):
        """Test complete checkout flow."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        page.locator(".shopping_cart_link").click()
        page.locator('[data-test="checkout"]').click()
        page.locator('[data-test="firstName"]').fill("John")
        page.locator('[data-test="lastName"]').fill("Doe")
        page.locator('[data-test="postalCode"]').fill("12345")
        page.locator('[data-test="continue"]').click()
        page.locator('[data-test="finish"]').click()
        expect(page.locator(".complete-header")).to_have_text("Thank you for your order!")


NOW GENERATE TESTS FOR THESE FLOWS (priority flows needing coverage):
{mandatory_tests}

AVAILABLE SELECTORS:
{selectors}

RULES:
1. Use pytest with playwright fixtures
2. Import: import re and from playwright.sync_api import Page, expect
3. Use BASE_URL = "https://www.saucedemo.com"
4. Create a logged_in_page fixture for authenticated tests
5. Use class TestSauceDemoSuite for all tests
6. Use page.locator() with CSS selectors
7. Use expect() for element assertions
8. For URL assertions use: assert "page_name.html" in page.url (NOT expect(page).to_have_url with glob patterns)
9. Valid users: standard_user, problem_user, performance_glitch_user, error_user, visual_user
10. Password for all users: secret_sauce
11. Locked out user: locked_out_user (should fail login)

Generate {test_count} tests covering the flows above. Output ONLY Python code.
'''


class SauceDemoPromptBuilder:
    """
    Builds focused Playwright test prompts based on UI coverage analysis.
    """
    
    def __init__(self, saucedemo_root: Path):
        self.saucedemo_root = Path(saucedemo_root)
        self.analyzer = SauceDemoCoverageAnalyzer(saucedemo_root)
        
    def build_prompt(
        self,
        max_priority_flows: int = 10,
        test_count: int = 15,
    ) -> str:
        """
        Build a prescriptive prompt based on coverage analysis.
        """
        has_coverage = self.analyzer.load_coverage()
        
        if has_coverage:
            priority_flows = self.analyzer.get_priority_flows(max_count=max_priority_flows)
        else:
            priority_flows = self._get_default_priority_flows()
        
        mandatory_tests = self._generate_mandatory_tests(priority_flows)
        selectors = self._format_selectors()
        
        return PRESCRIPTIVE_PROMPT_TEMPLATE.format(
            mandatory_tests=mandatory_tests,
            selectors=selectors,
            test_count=test_count,
        )
    
    def _generate_mandatory_tests(self, priority_flows: List[FlowCoverage]) -> str:
        """Generate flow descriptions for the prompt."""
        lines = []
        
        if not priority_flows:
            priority_flows = self._get_default_priority_flows()
        
        for i, fc in enumerate(priority_flows, 1):
            flow = fc.flow if isinstance(fc, FlowCoverage) else fc
            pages = ", ".join(flow.pages_involved)
            lines.append(f"\n{i}. {flow.name} [{flow.priority}]")
            lines.append(f"   Description: {flow.description}")
            lines.append(f"   Pages: {pages}")
            lines.append("   Steps:")
            for step in flow.steps:
                lines.append(f"   - {step}")
        
        return "\n".join(lines)
    
    def _format_selectors(self) -> str:
        """Format available selectors for the prompt."""
        lines = []
        for page_name, page_info in SAUCEDEMO_PAGES.items():
            lines.append(f"\n{page_name} page ({page_info.url_pattern}):")
            for selector_name, selector in page_info.selectors.items():
                lines.append(f"  - {selector_name}: {selector}")
        return "\n".join(lines)
    
    def _get_default_priority_flows(self) -> List[FlowCoverage]:
        """Return default priority flows when no coverage data."""
        critical_flows = get_flows_by_priority(["CRITICAL", "HIGH"])
        return [
            FlowCoverage(
                flow=flow,
                pages_covered=0,
                total_pages=len(flow.pages_involved),
            )
            for flow in critical_flows[:10]
        ]
    
    def build_focused_prompt(
        self,
        focus_flows: List[str],
        test_count: int = 10,
    ) -> str:
        """
        Build a highly focused prompt for specific flows.
        Used for iterative improvement after initial run.
        """
        flows = [f for f in SAUCEDEMO_FLOWS if f.name in focus_flows]
        
        if not flows:
            flows = SAUCEDEMO_FLOWS[:5]
        
        flow_specs = []
        for i, flow in enumerate(flows, 1):
            flow_specs.append(f"""
FLOW {i}: {flow.name}
Priority: {flow.priority}
Description: {flow.description}
Pages involved: {', '.join(flow.pages_involved)}
Steps:
{chr(10).join(f'  {j}. {step}' for j, step in enumerate(flow.steps, 1))}
""")
        
        selectors = self._format_selectors()
        
        return f'''Generate Python Playwright tests for SauceDemo.
Focus ONLY on these specific user flows.

BASE_URL = "https://www.saucedemo.com"
Valid users: standard_user, problem_user, performance_glitch_user, error_user, visual_user
Password: secret_sauce (for all users)
Locked user: locked_out_user

=== MANDATORY FLOWS TO TEST ===
{"".join(flow_specs)}

=== AVAILABLE SELECTORS ===
{selectors}

=== OUTPUT FORMAT ===
- Output ONLY Python code (no markdown)
- Use pytest with playwright
- Import: from playwright.sync_api import Page, expect
- Create fixture for login if needed
- Use class TestSauceDemoSuite

Generate {test_count} tests covering ALL flows above. Output ONLY Python code.
'''

    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get coverage summary for reporting."""
        self.analyzer.load_coverage()
        return self.analyzer.get_coverage_summary()


def build_focused_prompt(saucedemo_root: Path, **kwargs) -> str:
    """Convenience function to build a focused prompt."""
    builder = SauceDemoPromptBuilder(saucedemo_root)
    return builder.build_prompt(**kwargs)
