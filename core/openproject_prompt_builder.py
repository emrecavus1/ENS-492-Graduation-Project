"""
OpenProject Prompt Builder Module

Builds prescriptive prompts for generating OpenProject RSpec request specs.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from core.openproject_route_mapper import (
    OPENPROJECT_RESOURCES,
    OpenProjectEndpointInfo,
    get_safe_endpoints,
    get_statistics,
)


OPENPROJECT_RSPEC_PROMPT_TEMPLATE = """Generate RSpec request specs for OpenProject. Output ONLY Ruby code (no markdown).

AUTHENTICATION RULES (CRITICAL):
- For endpoints marked "(authenticated)", declare `current_user {{ create(:admin) }}`.
- For "(public)" endpoints, do not force authentication.
- Keep tests resilient: accept valid response status ranges instead of brittle exact HTML assertions.

OUTPUT RULES:
1. Start with: require "spec_helper"
2. Use EXACTLY: RSpec.describe "Generated OpenProject Request Coverage", :skip_csrf, type: :rails_request do
3. IMPORTANT: `:skip_csrf` must come BEFORE `type: :rails_request` in the describe arguments.
4. Group tests by resource in nested describe blocks.
5. Use factories / shared fixtures for dynamic IDs (Project.first, User.first, WorkPackage.first fallback logic).
6. For each request, use expectations like:
   expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
7. Do not use Capybara. Use request-style get/post/patch/delete.
8. Keep test names endpoint-based and parseable:
   - MUST start with HTTP method and canonical route template, e.g. "GET /api/v3/projects/:id".
   - Avoid decorative suffixes except "(public)" or "(authenticated)".
9. Add deterministic fixture-enrichment setup for API branch tests:
   - Define stable shared fixtures near top-level describe:
     - `let!(:seed_project) {{ Project.first || create(:project) }}`
     - `let!(:seed_user) {{ User.first || create(:user) }}`
     - `let!(:seed_work_package) {{ WorkPackage.first || create(:work_package, project: seed_project, author: seed_user) }}`
   - For user-focused API tests, prefer `seed_user` and `current_user`.
   - For work-package-focused API tests, prefer `seed_work_package` and its project context.
   - If an association might be nil, initialize fallback objects in the example before request.

COVERAGE IMPROVEMENT STRATEGY (CRITICAL):
- Do NOT only generate one smoke test per endpoint. Add branch-oriented scenarios.
- For every authenticated endpoint in the selected list:
  A) one test with `current_user` set (authenticated branch),
  B) one test without `current_user` when possible (anonymous/permission branch).
- For id-based routes (`:id`), include both:
  - valid ID scenario using fixture/factory
  - invalid/missing ID scenario (e.g., very large ID) with redirect-tolerant expectations.
- Minimize duplicates: each test should target a distinct method+path+scenario combination.
- Ensure broad resource balance: every listed resource must have at least one test, and high-priority controller resources should have multiple scenarios.
- Controller-focused depth:
  - For `home`, include both `/` and `/login`, and cover redirect-style statuses (301/302) and non-redirect statuses.
  - For `projects`, include listing, show, and settings with both authorized and unauthorized access patterns.
  - For `admin_statuses`, include multiple role/permission outcomes (admin vs anonymous) and tolerate redirects for anonymous.
- API representer depth (VERY IMPORTANT):
  - For list-style API endpoints (`/api/v3/projects`, `/api/v3/work_packages`, `/api/v3/users/:id` and `/api/v3/users/me`),
    add additional request variants using query parameters and headers to trigger serialization branches.
  - Include variants such as:
    - `get "<endpoint>", params: {{ pageSize: 1, offset: 0 }}`
    - `get "<endpoint>", params: {{ sortBy: "[[\\"id\\",\\"asc\\"]]" }}`
    - `get "<endpoint>", params: {{ filters: "[]" }}`
    - `get "<endpoint>", headers: {{ "Accept" => "application/json" }}`
  - Keep these as additive branch tests (not replacements for base endpoint checks).
  - For each API resource (`api_v3_projects`, `api_v3_work_packages`, `api_v3_users`), generate at least 2 parameterized branch variants.
  - REQUIRED minimum examples per API resource:
    - `api_v3_projects`: 1 base + 2 parameterized variants + 1 anonymous branch
    - `api_v3_work_packages`: 1 base + 2 parameterized variants + 1 anonymous branch
    - `api_v3_users`: include both `/api/v3/users/me` and `/api/v3/users/:id`,
      and add at least 2 variants total (params/header/anonymous split).
  - For authenticated endpoints, prefer explicit context split:
    - `context "with current_user"` and `context "without current_user"`
    - Both contexts should include at least one request for the endpoint.
  - TARGETED BRANCH PACK (HIGHEST PRIORITY):
    - For `/api/v3/work_packages` and `/api/v3/work_packages/:id`, include at least 3 of:
      - `params: {{ pageSize: 1, offset: 0 }}`
      - `params: {{ sortBy: "[[\\"id\\",\\"asc\\"]]" }}`
      - `params: {{ filters: "[]" }}`
      - `params: {{ include: "project,status,assignee" }}`
      - `headers: {{ "Accept" => "application/hal+json" }}`
      - and at least one request using `seed_work_package.id` for deterministic object-backed serialization.
    - For `/api/v3/users/me` and `/api/v3/users/:id`, include at least 3 of:
      - `headers: {{ "Accept" => "application/hal+json" }}`
      - `params: {{ status: "active" }}`
      - `params: {{ sortBy: "[[\\"id\\",\\"asc\\"]]" }}`
      - `params: {{ offset: 0, pageSize: 1 }}`
      - an explicit anonymous request variant for the same endpoint
      - and at least one request using `seed_user.id` for deterministic object-backed user representation.
    - Include one "admin-sensitive" user branch check by requesting `/api/v3/users/:id`
      in both authenticated and anonymous contexts, with redirect-tolerant expectations.
  - Fixture enrichment checks:
    - Include at least one work-package request with enriched params:
      `params: {{ include: "project,status,assignee", pageSize: 1, offset: 0 }}`
    - Include at least one user request with enriched params:
      `params: {{ status: "active", pageSize: 1, offset: 0 }}`
    - Keep all enriched requests redirect-tolerant for stability.

ASSERTION RULES FOR STABILITY (MUST FOLLOW):
- Use these exact expectation sets:
  - General response checks:
    expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
  - Anonymous / permission-limited checks:
    expect([301, 302, 401, 403, 404, 422]).to include(response.status)
  - Invalid-ID checks:
    expect([301, 302, 401, 403, 404, 422]).to include(response.status)
- Do NOT use narrow sets like [401, 403, 404] or [401, 403, 404, 422] alone.

BRANCH SELECTION SAFETY:
- If a route commonly redirects on anonymous access, keep the anonymous test but use redirect-tolerant status expectations.
- For `/projects/:id/settings` and `/statuses`, always allow 301/302 in unauthorized/anonymous scenarios.
- For parameterized API variants, also keep redirect-tolerant expectations to avoid flaky failures.

ENDPOINTS TO COVER:
{endpoints_to_test}

Generate {test_count} examples. Cover all listed resources with at least one example each.
Output ONLY Ruby code.
"""


class OpenProjectPromptBuilder:
    """Build prompt payloads for OpenProject test generation."""

    def __init__(self, openproject_root: Path):
        self.openproject_root = Path(openproject_root)

    def build_prompt(
        self,
        include_auth_tests: bool = True,
        test_count: int = 24,
        focus_resources: Optional[List[str]] = None,
    ) -> str:
        endpoints = self._select_endpoints(include_auth_tests, focus_resources)
        endpoints_text = self._format_endpoints_for_prompt(endpoints)
        return OPENPROJECT_RSPEC_PROMPT_TEMPLATE.format(
            endpoints_to_test=endpoints_text,
            test_count=test_count,
        )

    def build_focused_prompt(
        self,
        resources: List[str],
        test_count: int = 18,
    ) -> str:
        return self.build_prompt(
            include_auth_tests=True,
            test_count=test_count,
            focus_resources=resources,
        )

    def get_summary(self) -> Dict[str, Any]:
        return get_statistics()

    def _select_endpoints(
        self,
        include_auth_tests: bool,
        focus_resources: Optional[List[str]],
    ) -> List[OpenProjectEndpointInfo]:
        if focus_resources:
            selected: List[OpenProjectEndpointInfo] = []
            for resource_name in focus_resources:
                resource = OPENPROJECT_RESOURCES.get(resource_name)
                if resource:
                    selected.extend([e for e in resource.endpoints if e.safe_for_coverage])
            endpoints = selected
        else:
            endpoints = get_safe_endpoints()

        if not include_auth_tests:
            endpoints = [e for e in endpoints if not e.requires_auth]

        return endpoints

    def _format_endpoints_for_prompt(self, endpoints: List[OpenProjectEndpointInfo]) -> str:
        lines: List[str] = []
        lines.append("RESOURCES:")
        lines.append(", ".join(OPENPROJECT_RESOURCES.keys()))
        lines.append("")

        grouped: Dict[str, List[OpenProjectEndpointInfo]] = {}
        for endpoint in endpoints:
            grouped.setdefault(endpoint.resource or "other", []).append(endpoint)

        for resource_name, resource_endpoints in grouped.items():
            lines.append(f"## {resource_name}")
            for endpoint in resource_endpoints:
                auth_marker = "authenticated" if endpoint.requires_auth else "public"
                fixture_note = f" | fixture_hint: {endpoint.fixture_hint}" if endpoint.fixture_hint else ""
                lines.append(
                    f"- {endpoint.method} {endpoint.path} ({auth_marker}){fixture_note}"
                )
            lines.append("")

        return "\n".join(lines).strip()
