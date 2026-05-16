"""
OpenProject Route Mapper Module

Maps OpenProject endpoints/resources for request spec generation.
This is intentionally curated and safe-by-default for coverage-oriented testing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class OpenProjectEndpointInfo:
    """Represents an OpenProject endpoint."""

    method: str
    path: str
    description: str = ""
    requires_auth: bool = False
    safe_for_coverage: bool = True
    resource: str = ""
    fixture_hint: Optional[str] = None

    @property
    def is_get(self) -> bool:
        return self.method == "GET"


@dataclass
class OpenProjectResourceInfo:
    """Represents an OpenProject resource family."""

    name: str
    base_path: str
    description: str = ""
    endpoints: List[OpenProjectEndpointInfo] = None
    coverage_targets: List[str] = None

    def __post_init__(self):
        if self.endpoints is None:
            self.endpoints = []
        if self.coverage_targets is None:
            self.coverage_targets = []


OPENPROJECT_RESOURCES: Dict[str, OpenProjectResourceInfo] = {
    "home": OpenProjectResourceInfo(
        name="home",
        base_path="/",
        description="Basic app entry routes",
        coverage_targets=[
            "/app/controllers/homescreen_controller.rb",
        ],
        endpoints=[
            OpenProjectEndpointInfo("GET", "/", "Application home page", resource="home"),
        ],
    ),
    "account": OpenProjectResourceInfo(
        name="account",
        base_path="/login",
        description="Authentication and account entry routes",
        coverage_targets=[
            "/app/controllers/account_controller.rb",
        ],
        endpoints=[
            OpenProjectEndpointInfo("GET", "/login", "Login page", resource="account"),
            OpenProjectEndpointInfo("GET", "/logout", "Logout route", resource="account"),
            OpenProjectEndpointInfo("GET", "/account/register", "Registration page", resource="account"),
            OpenProjectEndpointInfo("GET", "/account/lost_password", "Lost password page", resource="account"),
        ],
    ),
    "projects": OpenProjectResourceInfo(
        name="projects",
        base_path="/projects",
        description="Project listing and detail routes",
        coverage_targets=[
            "/app/controllers/projects_controller.rb",
        ],
        endpoints=[
            OpenProjectEndpointInfo("GET", "/projects", "List projects", resource="projects"),
            OpenProjectEndpointInfo("GET", "/projects/:id", "Project details", resource="projects", fixture_hint="Project.first"),
            OpenProjectEndpointInfo("GET", "/projects/:id/settings", "Project settings", requires_auth=True, resource="projects", fixture_hint="Project.first"),
        ],
    ),
    "admin_statuses": OpenProjectResourceInfo(
        name="admin_statuses",
        base_path="/statuses",
        description="Administrative statuses routes",
        coverage_targets=[
            "/app/controllers/statuses_controller.rb",
        ],
        endpoints=[
            OpenProjectEndpointInfo("GET", "/statuses", "List statuses", requires_auth=True, resource="admin_statuses"),
            OpenProjectEndpointInfo("POST", "/statuses", "Create status", requires_auth=True, resource="admin_statuses", safe_for_coverage=False),
        ],
    ),
    "api_v3_root": OpenProjectResourceInfo(
        name="api_v3_root",
        base_path="/api/v3",
        description="API root and discovery",
        coverage_targets=[
            "/lib/api/root_api.rb",
            "/lib/api/root.rb",
        ],
        endpoints=[
            OpenProjectEndpointInfo("GET", "/api/v3", "API v3 root", resource="api_v3_root"),
            OpenProjectEndpointInfo("GET", "/api/v3/configuration", "API v3 configuration", resource="api_v3_root"),
        ],
    ),
    "api_v3_projects": OpenProjectResourceInfo(
        name="api_v3_projects",
        base_path="/api/v3/projects",
        description="API v3 projects",
        coverage_targets=[
            "/lib/api/v3/projects/projects_api.rb",
            "/lib/api/v3/projects/project_representer.rb",
        ],
        endpoints=[
            OpenProjectEndpointInfo("GET", "/api/v3/projects", "List API projects", requires_auth=True, resource="api_v3_projects"),
            OpenProjectEndpointInfo("GET", "/api/v3/projects/:id", "Show API project", requires_auth=True, resource="api_v3_projects", fixture_hint="Project.first"),
        ],
    ),
    "api_v3_work_packages": OpenProjectResourceInfo(
        name="api_v3_work_packages",
        base_path="/api/v3/work_packages",
        description="API v3 work packages",
        coverage_targets=[
            "/lib/api/v3/work_packages/work_packages_api.rb",
            "/lib/api/v3/work_packages/work_package_representer.rb",
        ],
        endpoints=[
            OpenProjectEndpointInfo("GET", "/api/v3/work_packages", "List work packages", requires_auth=True, resource="api_v3_work_packages"),
            OpenProjectEndpointInfo("GET", "/api/v3/work_packages/:id", "Show work package", requires_auth=True, resource="api_v3_work_packages", fixture_hint="WorkPackage.first"),
        ],
    ),
    "api_v3_users": OpenProjectResourceInfo(
        name="api_v3_users",
        base_path="/api/v3/users",
        description="API v3 users",
        coverage_targets=[
            "/lib/api/v3/users/users_api.rb",
            "/lib/api/v3/users/user_representer.rb",
        ],
        endpoints=[
            OpenProjectEndpointInfo("GET", "/api/v3/users/me", "Current user", requires_auth=True, resource="api_v3_users"),
            OpenProjectEndpointInfo("GET", "/api/v3/users/:id", "Show user", requires_auth=True, resource="api_v3_users", fixture_hint="User.first"),
        ],
    ),
}


def get_all_endpoints() -> List[OpenProjectEndpointInfo]:
    """Return all endpoints across all resources."""
    endpoints: List[OpenProjectEndpointInfo] = []
    for resource in OPENPROJECT_RESOURCES.values():
        endpoints.extend(resource.endpoints)
    return endpoints


def get_safe_endpoints() -> List[OpenProjectEndpointInfo]:
    """Return only safe endpoints for coverage runs."""
    return [e for e in get_all_endpoints() if e.safe_for_coverage]


def get_endpoints_by_resource(resource_name: str) -> List[OpenProjectEndpointInfo]:
    """Return endpoints for a named resource."""
    resource = OPENPROJECT_RESOURCES.get(resource_name)
    return resource.endpoints if resource else []


def get_statistics() -> Dict[str, object]:
    """Return aggregate statistics for reporting."""
    endpoints = get_all_endpoints()
    return {
        "total_resources": len(OPENPROJECT_RESOURCES),
        "total_endpoints": len(endpoints),
        "authenticated_endpoints": len([e for e in endpoints if e.requires_auth]),
        "public_endpoints": len([e for e in endpoints if not e.requires_auth]),
        "safe_endpoints": len([e for e in endpoints if e.safe_for_coverage]),
        "by_method": {
            "GET": len([e for e in endpoints if e.method == "GET"]),
            "POST": len([e for e in endpoints if e.method == "POST"]),
            "PATCH": len([e for e in endpoints if e.method == "PATCH"]),
            "DELETE": len([e for e in endpoints if e.method == "DELETE"]),
        },
    }


def get_coverage_target_patterns(resources: Optional[List[str]] = None) -> List[str]:
    """
    Return file-path substring patterns for line coverage focus.
    If resources is None, returns patterns for all configured resources.
    """
    selected = resources or list(OPENPROJECT_RESOURCES.keys())
    patterns: List[str] = []
    for name in selected:
        resource = OPENPROJECT_RESOURCES.get(name)
        if not resource:
            continue
        patterns.extend(resource.coverage_targets)

    # Preserve order while deduplicating
    return list(dict.fromkeys(patterns))
