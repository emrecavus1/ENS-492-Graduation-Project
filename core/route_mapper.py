"""
Route Mapper Module

Maps Redmine controllers to their HTTP routes for test generation.
This provides a static mapping since parsing rails routes dynamically
requires the Rails environment.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RouteInfo:
    """Represents an HTTP route."""
    method: str
    path: str
    description: str = ""
    requires_auth: bool = False
    requires_xhr: bool = False
    fixture_lookup: Optional[str] = None
    safe_for_coverage: bool = True  # False for POST/DELETE that need params
    
    @property
    def is_get(self) -> bool:
        return self.method == "GET"


CONTROLLER_ROUTES: Dict[str, List[RouteInfo]] = {
    "users_controller": [
        RouteInfo("GET", "/users", "List users", requires_auth=True),
        RouteInfo("GET", "/users/:id", "Show user", fixture_lookup="User.find_by(login: 'admin') || User.first"),
        RouteInfo("GET", "/users/new", "New user form", requires_auth=True),
        RouteInfo("POST", "/users", "Create user", requires_auth=True, safe_for_coverage=False),
        RouteInfo("GET", "/users/:id/edit", "Edit user form", requires_auth=True, fixture_lookup="User.find_by(login: 'admin') || User.first"),
        RouteInfo("GET", "/users/context_menu", "Users context menu", requires_auth=True, requires_xhr=True),
    ],
    
    "timelog_controller": [
        RouteInfo("GET", "/time_entries", "List time entries"),
        RouteInfo("GET", "/time_entries/new", "New time entry form", requires_auth=True),
        RouteInfo("POST", "/time_entries", "Create time entry", requires_auth=True, safe_for_coverage=False),
        RouteInfo("GET", "/projects/ecookbook/time_entries", "Project time entries"),
        RouteInfo("GET", "/projects/ecookbook/time_entries/new", "New project time entry", requires_auth=True),
        RouteInfo("GET", "/time_entries/imports/new", "Import time entries", requires_auth=True),
    ],
    
    "watchers_controller": [
        RouteInfo("POST", "/watchers", "Add watcher", requires_auth=True, safe_for_coverage=False),
        RouteInfo("DELETE", "/watchers/:id", "Remove watcher", requires_auth=True, safe_for_coverage=False),
        RouteInfo("GET", "/watchers/autocomplete_for_user", "Autocomplete watchers", requires_auth=True, requires_xhr=True),
        RouteInfo("POST", "/watchers/watch", "Watch issue", requires_auth=True, safe_for_coverage=False),
        RouteInfo("DELETE", "/watchers/unwatch", "Unwatch issue", requires_auth=True, safe_for_coverage=False),
    ],
    
    "workflows_controller": [
        RouteInfo("GET", "/workflows", "List workflows", requires_auth=True),
        RouteInfo("GET", "/workflows/edit", "Edit workflow", requires_auth=True),
        RouteInfo("GET", "/workflows/permissions", "Workflow permissions", requires_auth=True),
        RouteInfo("GET", "/workflows/copy", "Copy workflow", requires_auth=True),
    ],
    
    "roles_controller": [
        RouteInfo("GET", "/roles", "List roles", requires_auth=True),
        RouteInfo("GET", "/roles/new", "New role form", requires_auth=True),
        RouteInfo("POST", "/roles", "Create role", requires_auth=True, safe_for_coverage=False),
        RouteInfo("GET", "/roles/:id", "Show role", requires_auth=True, fixture_lookup="Role.first"),
        RouteInfo("GET", "/roles/:id/edit", "Edit role", requires_auth=True, fixture_lookup="Role.first"),
    ],
    
    "search_controller": [
        RouteInfo("GET", "/search", "Global search"),
        RouteInfo("GET", "/projects/ecookbook/search", "Project search"),
    ],
    
    "settings_controller": [
        RouteInfo("GET", "/settings", "Application settings", requires_auth=True),
        RouteInfo("GET", "/settings/edit", "Edit settings", requires_auth=True),
        RouteInfo("GET", "/settings/plugin/:id", "Plugin settings", requires_auth=True),
    ],
    
    "trackers_controller": [
        RouteInfo("GET", "/trackers", "List trackers", requires_auth=True),
        RouteInfo("GET", "/trackers/new", "New tracker form", requires_auth=True),
        RouteInfo("POST", "/trackers", "Create tracker", requires_auth=True),
        RouteInfo("GET", "/trackers/:id/edit", "Edit tracker", requires_auth=True),
    ],
    
    "comments_controller": [
        RouteInfo("POST", "/news/:news_id/comments", "Create comment", requires_auth=True),
        RouteInfo("DELETE", "/comments/:id", "Delete comment", requires_auth=True),
    ],
    
    "custom_field_enumerations_controller": [
        RouteInfo("GET", "/custom_fields/:custom_field_id/enumerations", "List CF enumerations", requires_auth=True),
        RouteInfo("POST", "/custom_fields/:custom_field_id/enumerations", "Create CF enumeration", requires_auth=True),
    ],
    
    "gantts_controller": [
        RouteInfo("GET", "/issues/gantt", "Issues Gantt chart"),
        RouteInfo("GET", "/projects/ecookbook/issues/gantt", "Project Gantt chart"),
    ],
    
    "principal_memberships_controller": [
        RouteInfo("GET", "/users/:user_id/memberships", "User memberships", requires_auth=True),
        RouteInfo("GET", "/groups/:group_id/memberships", "Group memberships", requires_auth=True),
        RouteInfo("POST", "/users/:user_id/memberships", "Add user membership", requires_auth=True),
    ],
    
    "project_enumerations_controller": [
        RouteInfo("GET", "/projects/ecookbook/enumerations", "Project enumerations", requires_auth=True),
        RouteInfo("PUT", "/projects/ecookbook/enumerations", "Update project enumerations", requires_auth=True),
    ],
    
    "wikis_controller": [
        RouteInfo("GET", "/projects/ecookbook/wiki", "Project wiki"),
        RouteInfo("POST", "/projects/ecookbook/wiki", "Create wiki", requires_auth=True),
        RouteInfo("DELETE", "/projects/ecookbook/wiki", "Delete wiki", requires_auth=True),
    ],
    
    "projects_controller": [
        RouteInfo("GET", "/projects", "List projects"),
        RouteInfo("GET", "/projects/ecookbook", "Show project"),
        RouteInfo("GET", "/projects/new", "New project form", requires_auth=True),
        RouteInfo("POST", "/projects", "Create project", requires_auth=True),
        RouteInfo("GET", "/projects/ecookbook/settings", "Project settings", requires_auth=True),
    ],
    
    "issues_controller": [
        RouteInfo("GET", "/issues", "List issues"),
        RouteInfo("GET", "/projects/ecookbook/issues", "Project issues"),
        RouteInfo("GET", "/projects/ecookbook/issues/new", "New issue form", requires_auth=True),
        RouteInfo("POST", "/projects/ecookbook/issues", "Create issue", requires_auth=True),
        RouteInfo("GET", "/issues/:id", "Show issue", fixture_lookup="Issue.first"),
        RouteInfo("GET", "/issues/:id/edit", "Edit issue", requires_auth=True, fixture_lookup="Issue.first"),
        RouteInfo("GET", "/issues/context_menu", "Issues context menu", requires_xhr=True),
    ],
    
    "members_controller": [
        RouteInfo("GET", "/projects/ecookbook/memberships", "Project members"),
        RouteInfo("GET", "/projects/ecookbook/memberships/new", "New membership form", requires_auth=True),
        RouteInfo("POST", "/projects/ecookbook/memberships", "Add member", requires_auth=True),
    ],
    
    "news_controller": [
        RouteInfo("GET", "/news", "All news"),
        RouteInfo("GET", "/projects/ecookbook/news", "Project news"),
        RouteInfo("GET", "/projects/ecookbook/news/new", "New news form", requires_auth=True),
        RouteInfo("POST", "/projects/ecookbook/news", "Create news", requires_auth=True),
        RouteInfo("GET", "/news/:id", "Show news", fixture_lookup="News.first"),
    ],
    
    "boards_controller": [
        RouteInfo("GET", "/projects/ecookbook/boards", "Project boards"),
        RouteInfo("GET", "/projects/ecookbook/boards/new", "New board form", requires_auth=True),
        RouteInfo("GET", "/boards/:id", "Show board", fixture_lookup="Board.first"),
    ],
    
    "documents_controller": [
        RouteInfo("GET", "/projects/ecookbook/documents", "Project documents"),
        RouteInfo("GET", "/projects/ecookbook/documents/new", "New document form", requires_auth=True),
        RouteInfo("GET", "/documents/:id", "Show document", fixture_lookup="Document.first"),
    ],
    
    "files_controller": [
        RouteInfo("GET", "/projects/ecookbook/files", "Project files"),
        RouteInfo("GET", "/projects/ecookbook/files/new", "Upload file form", requires_auth=True),
    ],
    
    "queries_controller": [
        RouteInfo("GET", "/queries", "List queries"),
        RouteInfo("GET", "/queries/new", "New query form", requires_auth=True),
        RouteInfo("GET", "/projects/ecookbook/queries/new", "New project query", requires_auth=True),
    ],
    
    "versions_controller": [
        RouteInfo("GET", "/projects/ecookbook/roadmap", "Project roadmap"),
        RouteInfo("GET", "/projects/ecookbook/versions", "Project versions"),
        RouteInfo("GET", "/projects/ecookbook/versions/new", "New version form", requires_auth=True),
        RouteInfo("GET", "/versions/:id", "Show version", fixture_lookup="Version.first"),
    ],
    
    "reports_controller": [
        RouteInfo("GET", "/projects/ecookbook/issues/report", "Issue report"),
        RouteInfo("GET", "/projects/ecookbook/issues/report/:detail", "Detailed report"),
    ],
    
    "activities_controller": [
        RouteInfo("GET", "/activity", "Global activity"),
        RouteInfo("GET", "/projects/ecookbook/activity", "Project activity"),
    ],
    
    "calendars_controller": [
        RouteInfo("GET", "/issues/calendar", "Issues calendar"),
        RouteInfo("GET", "/projects/ecookbook/issues/calendar", "Project calendar"),
    ],
    
    "auto_completes_controller": [
        RouteInfo("GET", "/issues/auto_complete", "Issue autocomplete", requires_xhr=True),
        RouteInfo("GET", "/wiki_pages/auto_complete", "Wiki autocomplete", requires_xhr=True),
    ],
    
    "context_menus_controller": [
        RouteInfo("GET", "/issues/context_menu", "Issues context menu", requires_xhr=True),
        RouteInfo("GET", "/time_entries/context_menu", "Time entries context menu", requires_xhr=True),
    ],
    
    "previews_controller": [
        RouteInfo("POST", "/preview/text", "Preview text", requires_xhr=True),
        RouteInfo("POST", "/issues/preview", "Preview issue", requires_xhr=True),
        RouteInfo("POST", "/news/preview", "Preview news", requires_xhr=True),
    ],
    
    "imports_controller": [
        RouteInfo("GET", "/issues/imports/new", "Import issues", requires_auth=True),
        RouteInfo("GET", "/users/imports/new", "Import users", requires_auth=True),
        RouteInfo("GET", "/time_entries/imports/new", "Import time entries", requires_auth=True),
    ],
    
    "journals_controller": [
        RouteInfo("GET", "/issues/changes", "Issue changes feed"),
        RouteInfo("GET", "/journals/:id/edit", "Edit journal", requires_auth=True),
    ],
    
    "messages_controller": [
        RouteInfo("GET", "/boards/:board_id/topics/new", "New topic form", requires_auth=True, fixture_lookup="Board.first"),
        RouteInfo("POST", "/boards/:board_id/topics", "Create topic", requires_auth=True, fixture_lookup="Board.first"),
        RouteInfo("GET", "/boards/:board_id/topics/:id", "Show topic", fixture_lookup="Message.first"),
    ],
    
    "issue_relations_controller": [
        RouteInfo("GET", "/issues/:issue_id/relations", "Issue relations", fixture_lookup="Issue.first"),
        RouteInfo("POST", "/issues/:issue_id/relations", "Create relation", requires_auth=True, fixture_lookup="Issue.first"),
    ],
    
    "attachments_controller": [
        RouteInfo("GET", "/attachments/:id", "Download attachment", fixture_lookup="Attachment.first"),
        RouteInfo("GET", "/attachments/:id/:filename", "Download attachment with name", fixture_lookup="Attachment.first"),
        RouteInfo("DELETE", "/attachments/:id", "Delete attachment", requires_auth=True),
    ],
    
    "email_addresses_controller": [
        RouteInfo("GET", "/users/:user_id/email_addresses", "User email addresses", requires_auth=True),
        RouteInfo("POST", "/users/:user_id/email_addresses", "Add email address", requires_auth=True),
    ],
    
    "repositories_controller": [
        RouteInfo("GET", "/projects/ecookbook/repositories/new", "New repository form", requires_auth=True),
        RouteInfo("GET", "/projects/ecookbook/repository", "Project repository"),
    ],
    
    "admin_controller": [
        RouteInfo("GET", "/admin", "Admin dashboard", requires_auth=True),
        RouteInfo("GET", "/admin/projects", "Admin projects", requires_auth=True),
        RouteInfo("GET", "/admin/plugins", "Admin plugins", requires_auth=True),
        RouteInfo("GET", "/admin/info", "Admin info", requires_auth=True),
    ],
    
    "groups_controller": [
        RouteInfo("GET", "/groups", "List groups", requires_auth=True),
        RouteInfo("GET", "/groups/new", "New group form", requires_auth=True),
        RouteInfo("POST", "/groups", "Create group", requires_auth=True),
    ],
    
    "custom_fields_controller": [
        RouteInfo("GET", "/custom_fields", "List custom fields", requires_auth=True),
        RouteInfo("GET", "/custom_fields/new", "New custom field form", requires_auth=True),
    ],
    
    "enumerations_controller": [
        RouteInfo("GET", "/enumerations", "List enumerations", requires_auth=True),
        RouteInfo("GET", "/enumerations/new", "New enumeration form", requires_auth=True),
    ],
    
    "issue_statuses_controller": [
        RouteInfo("GET", "/issue_statuses", "List issue statuses", requires_auth=True),
        RouteInfo("GET", "/issue_statuses/new", "New status form", requires_auth=True),
    ],
    
    "auth_sources_controller": [
        RouteInfo("GET", "/auth_sources", "List auth sources", requires_auth=True),
        RouteInfo("GET", "/auth_sources/new", "New auth source form", requires_auth=True),
    ],
    
    "issue_categories_controller": [
        RouteInfo("GET", "/projects/ecookbook/issue_categories", "Project categories"),
        RouteInfo("GET", "/projects/ecookbook/issue_categories/new", "New category form", requires_auth=True),
    ],
    
    "welcome_controller": [
        RouteInfo("GET", "/", "Home page"),
        RouteInfo("GET", "/robots.txt", "Robots.txt"),
    ],
    
    "account_controller": [
        RouteInfo("GET", "/login", "Login page"),
        RouteInfo("POST", "/login", "Login submit"),
        RouteInfo("GET", "/logout", "Logout"),
        RouteInfo("GET", "/account/register", "Register page"),
        RouteInfo("GET", "/account/lost_password", "Lost password page"),
    ],
    
    "my_controller": [
        RouteInfo("GET", "/my/account", "My account", requires_auth=True),
        RouteInfo("GET", "/my/page", "My page", requires_auth=True),
        RouteInfo("GET", "/my/password", "Change password", requires_auth=True),
    ],
    
    "wiki_controller": [
        RouteInfo("GET", "/projects/ecookbook/wiki", "Wiki index"),
        RouteInfo("GET", "/projects/ecookbook/wiki/:page", "Wiki page"),
        RouteInfo("GET", "/projects/ecookbook/wiki/:page/edit", "Edit wiki page", requires_auth=True),
    ],
}


def get_routes_for_controller(controller_name: str) -> List[RouteInfo]:
    """Get all routes for a given controller."""
    return CONTROLLER_ROUTES.get(controller_name, [])


def get_routes_for_controllers(controller_names: List[str]) -> Dict[str, List[RouteInfo]]:
    """Get routes for multiple controllers."""
    return {
        name: get_routes_for_controller(name)
        for name in controller_names
        if name in CONTROLLER_ROUTES
    }


def format_routes_for_prompt(routes: Dict[str, List[RouteInfo]]) -> str:
    """Format routes into a string suitable for LLM prompt."""
    lines = []
    
    for controller, route_list in routes.items():
        if not route_list:
            continue
            
        controller_display = controller.replace("_controller", "").title()
        lines.append(f"\n{controller_display}:")
        
        for route in route_list:
            auth_marker = " (requires auth)" if route.requires_auth else ""
            xhr_marker = " [XHR]" if route.requires_xhr else ""
            fixture_note = f" - use: {route.fixture_lookup}" if route.fixture_lookup else ""
            
            lines.append(f"  {route.method} {route.path}{auth_marker}{xhr_marker}{fixture_note}")
    
    return "\n".join(lines)
