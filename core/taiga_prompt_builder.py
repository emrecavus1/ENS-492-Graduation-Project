"""
Taiga Prompt Builder Module

Generates focused pytest test prompts based on coverage analysis.
Creates prompts that prioritize uncovered API endpoints for test generation.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
from pathlib import Path

from core.taiga_coverage_analyzer import TaigaCoverageAnalyzer, ViewSetCoverage
from core.taiga_viewset_mapper import (
    TAIGA_VIEWSETS,
    ViewSetInfo,
    EndpointInfo,
    get_endpoints_for_viewsets,
    format_endpoints_for_prompt,
    get_safe_get_endpoints,
)


PRESCRIPTIVE_PROMPT_TEMPLATE = '''Generate a Python pytest test file for Taiga API (http://localhost:9000). Output ONLY Python code, no markdown.

COMPLETE EXAMPLE (follow this exact format):

import pytest
import requests

BASE_URL = "http://localhost:9000/api/v1"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token."""
    response = requests.post(
        f"{{BASE_URL}}/auth",
        json={{"username": "admin", "password": "123123", "type": "normal"}}
    )
    assert response.status_code == 200
    return response.json()["auth_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Return headers with authentication."""
    return {{"Authorization": f"Bearer {{auth_token}}", "Content-Type": "application/json"}}


class TestTaigaAPI:
    """Generated test suite for Taiga API."""

    def test_list_projects(self, auth_headers):
        """Test listing all projects."""
        response = requests.get(f"{{BASE_URL}}/projects", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_current_user(self, auth_headers):
        """Test getting current user info."""
        response = requests.get(f"{{BASE_URL}}/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data

    def test_list_user_stories(self, auth_headers):
        """Test listing user stories."""
        response = requests.get(f"{{BASE_URL}}/userstories", headers=auth_headers)
        assert response.status_code == 200

    def test_list_tasks(self, auth_headers):
        """Test listing tasks."""
        response = requests.get(f"{{BASE_URL}}/tasks", headers=auth_headers)
        assert response.status_code == 200


NOW GENERATE TESTS FOR THESE ENDPOINTS (priority APIs needing coverage):
{mandatory_tests}

AVAILABLE API ENDPOINTS:
{endpoints}

RULES:
1. Use pytest with requests library
2. Import: import pytest, import requests
3. Use BASE_URL = "http://localhost:9000/api/v1"
4. Create auth_token and auth_headers fixtures
5. Use class TestTaigaAPI for all tests
6. Use requests.get/post/put/patch/delete
7. Assert response.status_code for all requests
8. For endpoints with path params, use fixture data or query existing resources
9. Default credentials: username="admin", password="123123"
10. Handle 200, 201, 400, 401, 403, 404 status codes appropriately

Generate {test_count} tests covering the endpoints above. Output ONLY Python code.
'''


class TaigaPromptBuilder:
    """
    Builds focused pytest prompts based on coverage analysis.
    """
    
    def __init__(self, taiga_root: Path):
        self.taiga_root = Path(taiga_root)
        self.analyzer = TaigaCoverageAnalyzer(taiga_root)
        
    def build_prompt(
        self,
        max_priority_viewsets: int = 10,
        test_count: int = 20,
    ) -> str:
        """
        Build a prescriptive prompt based on coverage analysis.
        """
        has_coverage = self.analyzer.load_coverage()
        
        if has_coverage:
            priority_viewsets = self.analyzer.get_prioritized_viewsets(
                max_count=max_priority_viewsets,
                min_lines=10,
                coverage_threshold=65.0,
            )
            viewset_names = [self._map_coverage_to_viewset(v) for v in priority_viewsets]
            viewset_names = [n for n in viewset_names if n]
        else:
            viewset_names = ["projects", "userstories", "tasks", "issues", "users", "auth"]
        
        mandatory_tests = self._generate_mandatory_tests(viewset_names)
        endpoints = self._format_all_endpoints(viewset_names)
        
        return PRESCRIPTIVE_PROMPT_TEMPLATE.format(
            mandatory_tests=mandatory_tests,
            endpoints=endpoints,
            test_count=test_count,
        )
    
    def _map_coverage_to_viewset(self, coverage: ViewSetCoverage) -> Optional[str]:
        """Map a coverage module name to a ViewSet name."""
        name_lower = coverage.name.lower()
        
        mapping = {
            "projects": ["project", "projects"],
            "userstories": ["userstory", "userstories", "user_story"],
            "tasks": ["task", "tasks"],
            "issues": ["issue", "issues"],
            "milestones": ["milestone", "milestones", "sprint"],
            "users": ["user", "users"],
            "memberships": ["membership", "memberships"],
            "roles": ["role", "roles"],
            "wiki": ["wiki"],
            "epics": ["epic", "epics"],
            "auth": ["auth", "authentication"],
            "search": ["search"],
            "timeline": ["timeline", "activity"],
        }
        
        for viewset_name, keywords in mapping.items():
            if any(kw in name_lower for kw in keywords):
                return viewset_name
        
        return None
    
    def _generate_mandatory_tests(self, viewset_names: List[str]) -> str:
        """Generate test specifications for priority ViewSets."""
        lines = []
        
        for name in viewset_names[:8]:
            if name not in TAIGA_VIEWSETS:
                continue
            viewset = TAIGA_VIEWSETS[name]
            lines.append(f"\n{name.upper()} ({viewset.priority} priority):")
            
            for ep in viewset.endpoints[:4]:
                if ep.is_get and ep.safe_for_coverage:
                    auth = "(needs auth)" if ep.requires_auth else "(public)"
                    lines.append(f"  - {ep.method} {ep.path} {auth}")
        
        lines.extend([
            "",
            "Additional important endpoints:",
            "- GET /api/v1/projects (list all projects)",
            "- GET /api/v1/users/me (current user)",
            "- GET /api/v1/userstories (list stories)",
            "- GET /api/v1/tasks (list tasks)",
            "- GET /api/v1/issues (list issues)",
            "- GET /api/v1/milestones (list sprints)",
            "- POST /api/v1/auth (login - test this first)",
        ])
        
        return "\n".join(lines)
    
    def _format_all_endpoints(self, viewset_names: List[str]) -> str:
        """Format all endpoints for the prompt."""
        return format_endpoints_for_prompt(viewset_names)
    
    def build_focused_prompt(
        self,
        focus_viewsets: List[str],
        test_count: int = 15,
    ) -> str:
        """
        Build a highly focused prompt for specific ViewSets.
        """
        viewset_specs = []
        for name in focus_viewsets:
            if name not in TAIGA_VIEWSETS:
                continue
            viewset = TAIGA_VIEWSETS[name]
            endpoints_str = "\n".join(
                f"    - {ep.method} {ep.path}"
                for ep in viewset.endpoints
            )
            viewset_specs.append(f"""
{viewset.name} ({viewset.base_path}):
  Description: {viewset.description}
  Endpoints:
{endpoints_str}
""")
        
        return f'''Generate Python pytest tests for Taiga API.
Focus ONLY on these ViewSets: {", ".join(focus_viewsets)}

BASE_URL = "http://localhost:9000/api/v1"
Credentials: username="admin", password="123123"

=== VIEWSETS TO TEST ===
{"".join(viewset_specs)}

=== OUTPUT FORMAT ===
- Output ONLY Python code (no markdown)
- Use pytest with requests library
- Create auth_token and auth_headers fixtures
- Use class TestTaigaAPI
- Test each endpoint with appropriate assertions

Generate {test_count} tests covering ALL endpoints above. Output ONLY Python code.
'''

    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get coverage summary for reporting."""
        self.analyzer.load_coverage()
        return self.analyzer.get_coverage_summary()


def build_focused_prompt(taiga_root: Path, **kwargs) -> str:
    """Convenience function to build a focused prompt."""
    builder = TaigaPromptBuilder(taiga_root)
    return builder.build_prompt(**kwargs)
