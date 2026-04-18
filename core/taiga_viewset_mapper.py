"""
Taiga ViewSet Mapper Module

Maps Django REST Framework ViewSets to API endpoints for Taiga.
Equivalent to route_mapper.py but for Django/DRF applications.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class EndpointInfo:
    """Represents an API endpoint in Taiga."""
    method: str
    path: str
    description: str = ""
    requires_auth: bool = True
    request_body: Optional[Dict] = None
    path_params: List[str] = field(default_factory=list)
    safe_for_coverage: bool = True
    
    @property
    def is_get(self) -> bool:
        return self.method == "GET"
    
    @property
    def is_list(self) -> bool:
        return self.is_get and not self.path_params


@dataclass
class ViewSetInfo:
    """Represents a DRF ViewSet with its endpoints."""
    name: str
    base_path: str
    description: str
    endpoints: List[EndpointInfo] = field(default_factory=list)
    priority: str = "MEDIUM"


TAIGA_VIEWSETS: Dict[str, ViewSetInfo] = {
    "projects": ViewSetInfo(
        name="ProjectViewSet",
        base_path="/api/v1/projects",
        description="Project management endpoints",
        priority="CRITICAL",
        endpoints=[
            EndpointInfo("GET", "/api/v1/projects", "List all projects"),
            EndpointInfo("GET", "/api/v1/projects/{id}", "Get project details", path_params=["id"]),
            EndpointInfo("POST", "/api/v1/projects", "Create project", 
                        request_body={"name": "str", "description": "str"}, safe_for_coverage=False),
            EndpointInfo("GET", "/api/v1/projects/by_slug?slug={slug}", "Get project by slug", path_params=["slug"]),
            EndpointInfo("GET", "/api/v1/projects/{id}/stats", "Get project statistics", path_params=["id"]),
            EndpointInfo("GET", "/api/v1/projects/{id}/member_stats", "Get member statistics", path_params=["id"]),
        ],
    ),
    "userstories": ViewSetInfo(
        name="UserStoriesViewSet",
        base_path="/api/v1/userstories",
        description="User story management",
        priority="CRITICAL",
        endpoints=[
            EndpointInfo("GET", "/api/v1/userstories", "List user stories"),
            EndpointInfo("GET", "/api/v1/userstories/{id}", "Get user story details", path_params=["id"]),
            EndpointInfo("POST", "/api/v1/userstories", "Create user story",
                        request_body={"project": "int", "subject": "str"}, safe_for_coverage=False),
            EndpointInfo("GET", "/api/v1/userstories/filters_data?project={project_id}", 
                        "Get filter options", path_params=["project_id"]),
        ],
    ),
    "tasks": ViewSetInfo(
        name="TasksViewSet",
        base_path="/api/v1/tasks",
        description="Task management",
        priority="HIGH",
        endpoints=[
            EndpointInfo("GET", "/api/v1/tasks", "List tasks"),
            EndpointInfo("GET", "/api/v1/tasks/{id}", "Get task details", path_params=["id"]),
            EndpointInfo("POST", "/api/v1/tasks", "Create task",
                        request_body={"project": "int", "subject": "str", "user_story": "int"}, 
                        safe_for_coverage=False),
            EndpointInfo("GET", "/api/v1/tasks/filters_data?project={project_id}", 
                        "Get task filters", path_params=["project_id"]),
        ],
    ),
    "issues": ViewSetInfo(
        name="IssuesViewSet",
        base_path="/api/v1/issues",
        description="Issue tracking",
        priority="HIGH",
        endpoints=[
            EndpointInfo("GET", "/api/v1/issues", "List issues"),
            EndpointInfo("GET", "/api/v1/issues/{id}", "Get issue details", path_params=["id"]),
            EndpointInfo("POST", "/api/v1/issues", "Create issue",
                        request_body={"project": "int", "subject": "str"}, safe_for_coverage=False),
            EndpointInfo("GET", "/api/v1/issues/filters_data?project={project_id}", 
                        "Get issue filters", path_params=["project_id"]),
        ],
    ),
    "milestones": ViewSetInfo(
        name="MilestonesViewSet", 
        base_path="/api/v1/milestones",
        description="Sprint/milestone management",
        priority="HIGH",
        endpoints=[
            EndpointInfo("GET", "/api/v1/milestones", "List milestones"),
            EndpointInfo("GET", "/api/v1/milestones/{id}", "Get milestone details", path_params=["id"]),
            EndpointInfo("GET", "/api/v1/milestones/{id}/stats", "Get milestone stats", path_params=["id"]),
        ],
    ),
    "users": ViewSetInfo(
        name="UsersViewSet",
        base_path="/api/v1/users",
        description="User management",
        priority="MEDIUM",
        endpoints=[
            EndpointInfo("GET", "/api/v1/users", "List users"),
            EndpointInfo("GET", "/api/v1/users/{id}", "Get user details", path_params=["id"]),
            EndpointInfo("GET", "/api/v1/users/me", "Get current user"),
        ],
    ),
    "memberships": ViewSetInfo(
        name="MembershipsViewSet",
        base_path="/api/v1/memberships",
        description="Project membership management",
        priority="MEDIUM",
        endpoints=[
            EndpointInfo("GET", "/api/v1/memberships", "List memberships"),
            EndpointInfo("GET", "/api/v1/memberships/{id}", "Get membership details", path_params=["id"]),
        ],
    ),
    "roles": ViewSetInfo(
        name="RolesViewSet",
        base_path="/api/v1/roles",
        description="Role management",
        priority="MEDIUM",
        endpoints=[
            EndpointInfo("GET", "/api/v1/roles", "List roles"),
            EndpointInfo("GET", "/api/v1/roles/{id}", "Get role details", path_params=["id"]),
        ],
    ),
    "wiki": ViewSetInfo(
        name="WikiViewSet",
        base_path="/api/v1/wiki",
        description="Wiki pages",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/wiki", "List wiki pages"),
            EndpointInfo("GET", "/api/v1/wiki/{id}", "Get wiki page", path_params=["id"]),
            EndpointInfo("GET", "/api/v1/wiki/by_slug?slug={slug}&project={project_id}", 
                        "Get wiki by slug", path_params=["slug", "project_id"]),
        ],
    ),
    "epics": ViewSetInfo(
        name="EpicsViewSet",
        base_path="/api/v1/epics",
        description="Epic management",
        priority="MEDIUM",
        endpoints=[
            EndpointInfo("GET", "/api/v1/epics", "List epics"),
            EndpointInfo("GET", "/api/v1/epics/{id}", "Get epic details", path_params=["id"]),
        ],
    ),
    "userstory_statuses": ViewSetInfo(
        name="UserStoryStatusesViewSet",
        base_path="/api/v1/userstory-statuses",
        description="User story status options",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/userstory-statuses", "List US statuses"),
        ],
    ),
    "task_statuses": ViewSetInfo(
        name="TaskStatusesViewSet",
        base_path="/api/v1/task-statuses",
        description="Task status options",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/task-statuses", "List task statuses"),
        ],
    ),
    "issue_statuses": ViewSetInfo(
        name="IssueStatusesViewSet",
        base_path="/api/v1/issue-statuses",
        description="Issue status options",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/issue-statuses", "List issue statuses"),
        ],
    ),
    "issue_types": ViewSetInfo(
        name="IssueTypesViewSet",
        base_path="/api/v1/issue-types",
        description="Issue type options",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/issue-types", "List issue types"),
        ],
    ),
    "priorities": ViewSetInfo(
        name="PrioritiesViewSet",
        base_path="/api/v1/priorities",
        description="Priority options",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/priorities", "List priorities"),
        ],
    ),
    "severities": ViewSetInfo(
        name="SeveritiesViewSet",
        base_path="/api/v1/severities",
        description="Severity options",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/severities", "List severities"),
        ],
    ),
    "points": ViewSetInfo(
        name="PointsViewSet",
        base_path="/api/v1/points",
        description="Story points options",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/points", "List points"),
        ],
    ),
    "auth": ViewSetInfo(
        name="AuthViewSet",
        base_path="/api/v1/auth",
        description="Authentication",
        priority="CRITICAL",
        endpoints=[
            EndpointInfo("POST", "/api/v1/auth", "Login", requires_auth=False,
                        request_body={"username": "str", "password": "str", "type": "normal"}),
            EndpointInfo("POST", "/api/v1/auth/refresh", "Refresh token"),
        ],
    ),
    "resolver": ViewSetInfo(
        name="ResolverViewSet",
        base_path="/api/v1/resolver",
        description="Reference resolver",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/resolver?project={slug}", "Resolve project refs", path_params=["slug"]),
        ],
    ),
    "search": ViewSetInfo(
        name="SearchViewSet",
        base_path="/api/v1/search",
        description="Search functionality",
        priority="MEDIUM",
        endpoints=[
            EndpointInfo("GET", "/api/v1/search?project={project_id}&text={query}", 
                        "Search in project", path_params=["project_id", "query"]),
        ],
    ),
    "timeline": ViewSetInfo(
        name="TimelineViewSet",
        base_path="/api/v1/timeline",
        description="Activity timeline",
        priority="LOW",
        endpoints=[
            EndpointInfo("GET", "/api/v1/timeline/user/{user_id}", "User timeline", path_params=["user_id"]),
            EndpointInfo("GET", "/api/v1/timeline/project/{project_id}", "Project timeline", path_params=["project_id"]),
        ],
    ),
}


def get_all_viewsets() -> Dict[str, ViewSetInfo]:
    """Return all Taiga ViewSets."""
    return TAIGA_VIEWSETS


def get_viewsets_by_priority(priorities: List[str]) -> List[ViewSetInfo]:
    """Get ViewSets filtered by priority levels."""
    return [v for v in TAIGA_VIEWSETS.values() if v.priority in priorities]


def get_endpoints_for_viewsets(viewset_names: List[str]) -> Dict[str, List[EndpointInfo]]:
    """Get endpoints for specific ViewSets."""
    result = {}
    for name in viewset_names:
        if name in TAIGA_VIEWSETS:
            result[name] = TAIGA_VIEWSETS[name].endpoints
    return result


def get_safe_get_endpoints() -> List[EndpointInfo]:
    """Get all safe GET endpoints for initial coverage."""
    endpoints = []
    for viewset in TAIGA_VIEWSETS.values():
        for endpoint in viewset.endpoints:
            if endpoint.is_get and endpoint.safe_for_coverage and not endpoint.path_params:
                endpoints.append(endpoint)
    return endpoints


def format_endpoints_for_prompt(viewset_names: List[str]) -> str:
    """Format endpoints as a string for LLM prompt."""
    lines = []
    for name in viewset_names:
        if name not in TAIGA_VIEWSETS:
            continue
        viewset = TAIGA_VIEWSETS[name]
        lines.append(f"\n{viewset.name} ({viewset.base_path}):")
        lines.append(f"  Description: {viewset.description}")
        for ep in viewset.endpoints:
            auth = "(auth required)" if ep.requires_auth else "(public)"
            params = f" [params: {', '.join(ep.path_params)}]" if ep.path_params else ""
            lines.append(f"  - {ep.method} {ep.path} {auth}{params}")
    return "\n".join(lines)
