"""
Prompt Builder Module

Generates focused test generation prompts based on coverage analysis
and route mapping. Uses prescriptive test specifications to ensure
the LLM generates tests that actually hit the priority routes.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
from pathlib import Path

from core.coverage_analyzer import CoverageAnalyzer, ControllerCoverage
from core.route_mapper import (
    get_routes_for_controllers,
    format_routes_for_prompt,
    RouteInfo,
    CONTROLLER_ROUTES,
)


PRESCRIPTIVE_PROMPT_TEMPLATE = '''Generate a Ruby Minitest file for Redmine. Output ONLY Ruby code, no markdown.

CRITICAL AUTHENTICATION INSTRUCTIONS:
- Routes marked "(needs log_user)" MUST call log_user('admin', 'admin') BEFORE the request
- Routes marked "(anonymous OK)" do NOT need login
- NEVER skip authentication for routes that require it - tests will fail with 302 redirect

COMPLETE EXAMPLE (follow this exact format):

require_relative '../test_helper'

class GeneratedSuiteTest < Redmine::IntegrationTest
  fixtures :all

  # AUTHENTICATED TEST - always log_user first!
  test "users index requires login" do
    log_user('admin', 'admin')  # MUST login first for /users
    get '/users'
    assert_response :success
  end

  # ANONYMOUS TEST - no login needed
  test "time entries list anonymous" do
    get '/time_entries'
    assert [200, 302, 403].include?(response.status)
  end

  # AUTHENTICATED TEST - admin routes need login
  test "roles index as admin" do
    log_user('admin', 'admin')  # MUST login first for /roles
    get '/roles'
    assert_response :success
  end

  # AUTHENTICATED TEST - settings need admin
  test "settings index as admin" do
    log_user('admin', 'admin')  # MUST login first for /settings
    get '/settings'
    assert_response :success
  end

  # AUTHENTICATED TEST with dynamic ID
  test "user show with dynamic id" do
    log_user('admin', 'admin')
    user = User.first
    get "/users/#{{user.id}}"
    assert_response :success
  end
end

NOW GENERATE TESTS FOR THESE ROUTES:
{mandatory_tests}

RULES:
1. Start with: require_relative '../test_helper'
2. Class must be: class GeneratedSuiteTest < Redmine::IntegrationTest
3. Add: fixtures :all
4. Use test "name" do ... end syntax
5. CRITICAL: For routes marked "(needs log_user)", ALWAYS call log_user('admin', 'admin') as the FIRST line in the test
6. For routes marked "(anonymous OK)", do NOT call log_user
7. Use get/post for requests, assert_response or assert response.status
8. For dynamic IDs use: User.first, Role.first, Issue.first, Project.find('ecookbook'), etc.
9. Generate tests for BOTH authenticated AND anonymous routes

Generate {test_count} tests covering the routes above. Output ONLY Ruby code.
'''


class PromptBuilder:
    """
    Builds focused test generation prompts based on coverage analysis.
    Uses prescriptive test specifications to ensure LLM generates
    tests that actually hit the priority routes.
    """
    
    def __init__(self, redmine_root: Path):
        self.redmine_root = Path(redmine_root)
        self.analyzer = CoverageAnalyzer(redmine_root)
        
    def build_prompt(
        self,
        max_priority_controllers: int = 12,
        test_count: int = 20,
        auth_test_count: int = 8,
    ) -> str:
        """
        Build a prescriptive prompt based on coverage analysis.
        """
        has_coverage = self.analyzer.load_coverage()
        
        if has_coverage:
            priority_controllers = self.analyzer.get_prioritized_controllers(
                max_count=max_priority_controllers,
                min_lines=25,
                coverage_threshold=65.0,
            )
        else:
            priority_controllers = []
        
        mandatory_tests = self._generate_mandatory_tests(priority_controllers, test_count)
        
        return PRESCRIPTIVE_PROMPT_TEMPLATE.format(
            mandatory_tests=mandatory_tests,
            test_count=test_count,
        )
    
    def _generate_mandatory_tests(
        self,
        priority_controllers: List[ControllerCoverage],
        test_count: int,
    ) -> str:
        """Generate simple route list for priority controllers."""
        routes_list = []
        
        if not priority_controllers:
            priority_controllers = self._get_default_priority_controllers()
        
        controller_names = [c.name for c in priority_controllers]
        routes_by_controller = get_routes_for_controllers(controller_names)
        
        for controller in priority_controllers[:10]:
            routes = routes_by_controller.get(controller.name, [])
            if not routes:
                continue
            
            controller_name = controller.name.replace("_controller", "")
            safe_routes = [r for r in routes if r.is_get and r.safe_for_coverage]
            
            for route in safe_routes[:4]:
                auth_note = "(needs log_user)" if route.requires_auth else "(anonymous OK)"
                xhr_note = " [XHR headers needed]" if route.requires_xhr else ""
                fixture_note = f" - use {route.fixture_lookup}" if route.fixture_lookup else ""
                routes_list.append(f"- {controller_name}: {route.method} {route.path} {auth_note}{xhr_note}{fixture_note}")
        
        routes_list.extend([
            "",
            "=== AUTHENTICATED ROUTES (MUST use log_user('admin', 'admin') first) ===",
            "- GET /users (needs log_user)",
            "- GET /users/new (needs log_user)", 
            "- GET /users/:id/edit (needs log_user) - use User.first.id",
            "- GET /time_entries/new (needs log_user)",
            "- GET /roles (needs log_user)",
            "- GET /roles/new (needs log_user)",
            "- GET /roles/:id (needs log_user) - use Role.first.id",
            "- GET /workflows (needs log_user)",
            "- GET /workflows/edit (needs log_user)",
            "- GET /trackers (needs log_user)",
            "- GET /trackers/new (needs log_user)",
            "- GET /settings (needs log_user)",
            "- GET /admin (needs log_user)",
            "- GET /admin/projects (needs log_user)",
            "- GET /groups (needs log_user)",
            "- GET /groups/new (needs log_user)",
            "- GET /my/account (needs log_user)",
            "- GET /my/page (needs log_user)",
            "- GET /custom_fields (needs log_user)",
            "- GET /enumerations (needs log_user)",
            "- GET /issue_statuses (needs log_user)",
            "",
            "=== ANONYMOUS ROUTES (no login needed) ===",
            "- GET /time_entries (anonymous OK)",
            "- GET /search?q=test (anonymous OK)",
            "- GET /issues/gantt (anonymous OK)",
            "- GET /issues/calendar (anonymous OK)",
            "- GET /issues (anonymous OK)",
            "- GET /projects (anonymous OK)",
            "- GET /news (anonymous OK)",
            "- GET /activity (anonymous OK)",
            "- GET /login (anonymous OK)",
        ])
        
        return "\n".join(routes_list)
    
    def _format_route_specs(self, routes: List[RouteInfo]) -> str:
        """Format routes as explicit specifications."""
        lines = []
        for r in routes:
            fixture_note = f" (use: {r.fixture_lookup})" if r.fixture_lookup else ""
            xhr_note = " WITH xhr_headers" if r.requires_xhr else ""
            lines.append(f"  - {r.method} {r.path}{fixture_note}{xhr_note}")
        return "\n".join(lines)
    
    def _get_default_priority_controllers(self) -> List[ControllerCoverage]:
        """Return default priority controllers when no coverage data."""
        defaults = [
            ("users_controller", 208),
            ("timelog_controller", 254),
            ("watchers_controller", 186),
            ("roles_controller", 104),
            ("workflows_controller", 138),
            ("trackers_controller", 88),
            ("search_controller", 65),
        ]
        return [
            ControllerCoverage(
                name=name,
                file_path="",
                covered_percent=0.0,
                total_lines=lines,
                lines_covered=0,
                lines_missed=lines,
            )
            for name, lines in defaults
        ]
    
    def build_iterative_prompt(
        self,
        focus_controllers: List[str],
        test_count: int = 15,
    ) -> str:
        """
        Build a highly focused prompt for specific controllers.
        Used for iterative improvement after initial run.
        """
        routes = get_routes_for_controllers(focus_controllers)
        
        mandatory_tests = []
        test_num = 1
        
        for controller in focus_controllers:
            controller_routes = routes.get(controller, [])
            if not controller_routes:
                continue
            
            display = controller.replace("_controller", "").title()
            
            safe_auth_routes = [r for r in controller_routes if r.requires_auth and r.is_get and r.safe_for_coverage]
            if safe_auth_routes:
                route_specs = self._format_route_specs(safe_auth_routes)
                mandatory_tests.append(f"""
TEST {test_num}: "test_{display.lower()}_authenticated"
- log_user('admin', 'admin') first
- Then hit:
{route_specs}
- Assert response.status is in [200, 302, 403, 404] after each
""")
                test_num += 1
            
            safe_public_routes = [r for r in controller_routes if not r.requires_auth and r.is_get and r.safe_for_coverage]
            if safe_public_routes:
                route_specs = self._format_route_specs(safe_public_routes)
                mandatory_tests.append(f"""
TEST {test_num}: "test_{display.lower()}_anonymous"
- NO login
- Hit:
{route_specs}
- Assert response.status is in [200, 302, 403, 404] after each
""")
                test_num += 1
        
        return f'''You are generating Ruby Minitest integration tests for Redmine.
Focus ONLY on these controllers: {", ".join(focus_controllers)}

CRITICAL OUTPUT FORMAT (MUST FOLLOW EXACTLY):
- Output ONLY a single Ruby file (no markdown).
- First line: require_relative '../test_helper'
- MUST inherit from Redmine::IntegrationTest (NOT ActionDispatch::IntegrationTest)
- MUST include fixtures :all declaration

EXACT CLASS STRUCTURE:
```ruby
require_relative '../test_helper'

class GeneratedSuiteTest < Redmine::IntegrationTest
  fixtures :all

  def xhr_headers
    {{ 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }}
  end

  # test methods here
end
```

AUTHENTICATION: Use log_user('admin', 'admin') - Redmine's built-in login method

=== MANDATORY TESTS ===
{"".join(mandatory_tests)}

Generate the Ruby test file with ALL tests above. Do NOT skip any.
'''

    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get coverage summary for reporting."""
        if not self.analyzer.controllers:
            self.analyzer.load_coverage()
        return self.analyzer.get_coverage_summary()


def build_focused_prompt(redmine_root: Path, **kwargs) -> str:
    """Convenience function to build a focused prompt."""
    builder = PromptBuilder(redmine_root)
    return builder.build_prompt(**kwargs)
