# Redmine Test Generation Report

**Generated:** 2026-04-17 18:04:23

---

## 1. Code Coverage Summary

| Metric | Value |
|--------|-------|
| Total Controllers | 48 |
| Zero Coverage | 1 |
| Well Covered (>70%) | 46 |
| Overall Coverage | 94.5% |

## 2. API Documentation

### 2.1 API Statistics

| Metric | Count |
|--------|-------|
| Total Controllers | 47 |
| Total Routes/Endpoints | 144 |
| Routes Requiring Authentication | 88 |
| Routes Requiring XHR Headers | 10 |
| Routes with Dynamic Parameters | 23 |
| Unsafe Routes (filtered out) | 7 |

### 2.2 Routes by HTTP Method

| Method | Count |
|--------|-------|
| GET | 116 |
| POST | 22 |
| PUT | 1 |
| DELETE | 5 |

### 2.3 Controller Route Details


#### Account (`account_controller`)
- Total Routes: 5
- Auth Required: 0
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/login` | Login page | No | No | No |
| POST | `/login` | Login submit | No | No | No |
| GET | `/logout` | Logout | No | No | No |
| GET | `/account/register` | Register page | No | No | No |
| GET | `/account/lost_password` | Lost password page | No | No | No |

#### Activities (`activities_controller`)
- Total Routes: 2
- Auth Required: 0
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/activity` | Global activity | No | No | No |
| GET | `/projects/ecookbook/activity` | Project activity | No | No | No |

#### Admin (`admin_controller`)
- Total Routes: 4
- Auth Required: 4
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/admin` | Admin dashboard | Yes | No | No |
| GET | `/admin/projects` | Admin projects | Yes | No | No |
| GET | `/admin/plugins` | Admin plugins | Yes | No | No |
| GET | `/admin/info` | Admin info | Yes | No | No |

#### Attachments (`attachments_controller`)
- Total Routes: 3
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/attachments/:id` | Download attachment | No | No | Yes |
| GET | `/attachments/:id/:filename` | Download attachment with name | No | No | Yes |
| DELETE | `/attachments/:id` | Delete attachment | Yes | No | Yes |

#### Auth_Sources (`auth_sources_controller`)
- Total Routes: 2
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/auth_sources` | List auth sources | Yes | No | No |
| GET | `/auth_sources/new` | New auth source form | Yes | No | No |

#### Auto_Completes (`auto_completes_controller`)
- Total Routes: 2
- Auth Required: 0
- XHR Routes: 2

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/issues/auto_complete` | Issue autocomplete | No | Yes | No |
| GET | `/wiki_pages/auto_complete` | Wiki autocomplete | No | Yes | No |

#### Boards (`boards_controller`)
- Total Routes: 3
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/boards` | Project boards | No | No | No |
| GET | `/projects/ecookbook/boards/new` | New board form | Yes | No | No |
| GET | `/boards/:id` | Show board | No | No | Yes |

#### Calendars (`calendars_controller`)
- Total Routes: 2
- Auth Required: 0
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/issues/calendar` | Issues calendar | No | No | No |
| GET | `/projects/ecookbook/issues/calendar` | Project calendar | No | No | No |

#### Comments (`comments_controller`)
- Total Routes: 2
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| POST | `/news/:news_id/comments` | Create comment | Yes | No | No |
| DELETE | `/comments/:id` | Delete comment | Yes | No | Yes |

#### Context_Menus (`context_menus_controller`)
- Total Routes: 2
- Auth Required: 0
- XHR Routes: 2

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/issues/context_menu` | Issues context menu | No | Yes | No |
| GET | `/time_entries/context_menu` | Time entries context menu | No | Yes | No |

#### Custom_Field_Enumerations (`custom_field_enumerations_controller`)
- Total Routes: 2
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/custom_fields/:custom_field_id/enumerations` | List CF enumerations | Yes | No | No |
| POST | `/custom_fields/:custom_field_id/enumerations` | Create CF enumeration | Yes | No | No |

#### Custom_Fields (`custom_fields_controller`)
- Total Routes: 2
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/custom_fields` | List custom fields | Yes | No | No |
| GET | `/custom_fields/new` | New custom field form | Yes | No | No |

#### Documents (`documents_controller`)
- Total Routes: 3
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/documents` | Project documents | No | No | No |
| GET | `/projects/ecookbook/documents/new` | New document form | Yes | No | No |
| GET | `/documents/:id` | Show document | No | No | Yes |

#### Email_Addresses (`email_addresses_controller`)
- Total Routes: 2
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/users/:user_id/email_addresses` | User email addresses | Yes | No | Yes |
| POST | `/users/:user_id/email_addresses` | Add email address | Yes | No | Yes |

#### Enumerations (`enumerations_controller`)
- Total Routes: 2
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/enumerations` | List enumerations | Yes | No | No |
| GET | `/enumerations/new` | New enumeration form | Yes | No | No |

#### Files (`files_controller`)
- Total Routes: 2
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/files` | Project files | No | No | No |
| GET | `/projects/ecookbook/files/new` | Upload file form | Yes | No | No |

#### Gantts (`gantts_controller`)
- Total Routes: 2
- Auth Required: 0
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/issues/gantt` | Issues Gantt chart | No | No | No |
| GET | `/projects/ecookbook/issues/gantt` | Project Gantt chart | No | No | No |

#### Groups (`groups_controller`)
- Total Routes: 3
- Auth Required: 3
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/groups` | List groups | Yes | No | No |
| GET | `/groups/new` | New group form | Yes | No | No |
| POST | `/groups` | Create group | Yes | No | No |

#### Imports (`imports_controller`)
- Total Routes: 3
- Auth Required: 3
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/issues/imports/new` | Import issues | Yes | No | No |
| GET | `/users/imports/new` | Import users | Yes | No | No |
| GET | `/time_entries/imports/new` | Import time entries | Yes | No | No |

#### Issue_Categories (`issue_categories_controller`)
- Total Routes: 2
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/issue_categories` | Project categories | No | No | No |
| GET | `/projects/ecookbook/issue_categories/new` | New category form | Yes | No | No |

#### Issue_Relations (`issue_relations_controller`)
- Total Routes: 2
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/issues/:issue_id/relations` | Issue relations | No | No | No |
| POST | `/issues/:issue_id/relations` | Create relation | Yes | No | No |

#### Issue_Statuses (`issue_statuses_controller`)
- Total Routes: 2
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/issue_statuses` | List issue statuses | Yes | No | No |
| GET | `/issue_statuses/new` | New status form | Yes | No | No |

#### Issues (`issues_controller`)
- Total Routes: 7
- Auth Required: 3
- XHR Routes: 1

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/issues` | List issues | No | No | No |
| GET | `/projects/ecookbook/issues` | Project issues | No | No | No |
| GET | `/projects/ecookbook/issues/new` | New issue form | Yes | No | No |
| POST | `/projects/ecookbook/issues` | Create issue | Yes | No | No |
| GET | `/issues/:id` | Show issue | No | No | Yes |
| GET | `/issues/:id/edit` | Edit issue | Yes | No | Yes |
| GET | `/issues/context_menu` | Issues context menu | No | Yes | No |

#### Journals (`journals_controller`)
- Total Routes: 2
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/issues/changes` | Issue changes feed | No | No | No |
| GET | `/journals/:id/edit` | Edit journal | Yes | No | Yes |

#### Members (`members_controller`)
- Total Routes: 3
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/memberships` | Project members | No | No | No |
| GET | `/projects/ecookbook/memberships/new` | New membership form | Yes | No | No |
| POST | `/projects/ecookbook/memberships` | Add member | Yes | No | No |

#### Messages (`messages_controller`)
- Total Routes: 3
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/boards/:board_id/topics/new` | New topic form | Yes | No | No |
| POST | `/boards/:board_id/topics` | Create topic | Yes | No | No |
| GET | `/boards/:board_id/topics/:id` | Show topic | No | No | Yes |

#### My (`my_controller`)
- Total Routes: 3
- Auth Required: 3
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/my/account` | My account | Yes | No | No |
| GET | `/my/page` | My page | Yes | No | No |
| GET | `/my/password` | Change password | Yes | No | No |

#### News (`news_controller`)
- Total Routes: 5
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/news` | All news | No | No | No |
| GET | `/projects/ecookbook/news` | Project news | No | No | No |
| GET | `/projects/ecookbook/news/new` | New news form | Yes | No | No |
| POST | `/projects/ecookbook/news` | Create news | Yes | No | No |
| GET | `/news/:id` | Show news | No | No | Yes |

#### Previews (`previews_controller`)
- Total Routes: 3
- Auth Required: 0
- XHR Routes: 3

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| POST | `/preview/text` | Preview text | No | Yes | No |
| POST | `/issues/preview` | Preview issue | No | Yes | No |
| POST | `/news/preview` | Preview news | No | Yes | No |

#### Principal_Memberships (`principal_memberships_controller`)
- Total Routes: 3
- Auth Required: 3
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/users/:user_id/memberships` | User memberships | Yes | No | Yes |
| GET | `/groups/:group_id/memberships` | Group memberships | Yes | No | No |
| POST | `/users/:user_id/memberships` | Add user membership | Yes | No | Yes |

#### Project_Enumerations (`project_enumerations_controller`)
- Total Routes: 2
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/enumerations` | Project enumerations | Yes | No | No |
| PUT | `/projects/ecookbook/enumerations` | Update project enumerations | Yes | No | No |

#### Projects (`projects_controller`)
- Total Routes: 5
- Auth Required: 3
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects` | List projects | No | No | No |
| GET | `/projects/ecookbook` | Show project | No | No | No |
| GET | `/projects/new` | New project form | Yes | No | No |
| POST | `/projects` | Create project | Yes | No | No |
| GET | `/projects/ecookbook/settings` | Project settings | Yes | No | No |

#### Queries (`queries_controller`)
- Total Routes: 3
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/queries` | List queries | No | No | No |
| GET | `/queries/new` | New query form | Yes | No | No |
| GET | `/projects/ecookbook/queries/new` | New project query | Yes | No | No |

#### Reports (`reports_controller`)
- Total Routes: 2
- Auth Required: 0
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/issues/report` | Issue report | No | No | No |
| GET | `/projects/ecookbook/issues/report/:detail` | Detailed report | No | No | No |

#### Repositories (`repositories_controller`)
- Total Routes: 2
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/repositories/new` | New repository form | Yes | No | No |
| GET | `/projects/ecookbook/repository` | Project repository | No | No | No |

#### Roles (`roles_controller`)
- Total Routes: 5
- Auth Required: 5
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/roles` | List roles | Yes | No | No |
| GET | `/roles/new` | New role form | Yes | No | No |
| POST | `/roles` | Create role ⚠️ | Yes | No | No |
| GET | `/roles/:id` | Show role | Yes | No | Yes |
| GET | `/roles/:id/edit` | Edit role | Yes | No | Yes |

#### Search (`search_controller`)
- Total Routes: 2
- Auth Required: 0
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/search` | Global search | No | No | No |
| GET | `/projects/ecookbook/search` | Project search | No | No | No |

#### Settings (`settings_controller`)
- Total Routes: 3
- Auth Required: 3
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/settings` | Application settings | Yes | No | No |
| GET | `/settings/edit` | Edit settings | Yes | No | No |
| GET | `/settings/plugin/:id` | Plugin settings | Yes | No | Yes |

#### Timelog (`timelog_controller`)
- Total Routes: 6
- Auth Required: 4
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/time_entries` | List time entries | No | No | No |
| GET | `/time_entries/new` | New time entry form | Yes | No | No |
| POST | `/time_entries` | Create time entry ⚠️ | Yes | No | No |
| GET | `/projects/ecookbook/time_entries` | Project time entries | No | No | No |
| GET | `/projects/ecookbook/time_entries/new` | New project time entry | Yes | No | No |
| GET | `/time_entries/imports/new` | Import time entries | Yes | No | No |

#### Trackers (`trackers_controller`)
- Total Routes: 4
- Auth Required: 4
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/trackers` | List trackers | Yes | No | No |
| GET | `/trackers/new` | New tracker form | Yes | No | No |
| POST | `/trackers` | Create tracker | Yes | No | No |
| GET | `/trackers/:id/edit` | Edit tracker | Yes | No | Yes |

#### Users (`users_controller`)
- Total Routes: 6
- Auth Required: 5
- XHR Routes: 1

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/users` | List users | Yes | No | No |
| GET | `/users/:id` | Show user | No | No | Yes |
| GET | `/users/new` | New user form | Yes | No | No |
| POST | `/users` | Create user ⚠️ | Yes | No | No |
| GET | `/users/:id/edit` | Edit user form | Yes | No | Yes |
| GET | `/users/context_menu` | Users context menu | Yes | Yes | No |

#### Versions (`versions_controller`)
- Total Routes: 4
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/roadmap` | Project roadmap | No | No | No |
| GET | `/projects/ecookbook/versions` | Project versions | No | No | No |
| GET | `/projects/ecookbook/versions/new` | New version form | Yes | No | No |
| GET | `/versions/:id` | Show version | No | No | Yes |

#### Watchers (`watchers_controller`)
- Total Routes: 5
- Auth Required: 5
- XHR Routes: 1

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| POST | `/watchers` | Add watcher ⚠️ | Yes | No | No |
| DELETE | `/watchers/:id` | Remove watcher ⚠️ | Yes | No | Yes |
| GET | `/watchers/autocomplete_for_user` | Autocomplete watchers | Yes | Yes | No |
| POST | `/watchers/watch` | Watch issue ⚠️ | Yes | No | No |
| DELETE | `/watchers/unwatch` | Unwatch issue ⚠️ | Yes | No | No |

#### Welcome (`welcome_controller`)
- Total Routes: 2
- Auth Required: 0
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/` | Home page | No | No | No |
| GET | `/robots.txt` | Robots.txt | No | No | No |

#### Wiki (`wiki_controller`)
- Total Routes: 3
- Auth Required: 1
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/wiki` | Wiki index | No | No | No |
| GET | `/projects/ecookbook/wiki/:page` | Wiki page | No | No | No |
| GET | `/projects/ecookbook/wiki/:page/edit` | Edit wiki page | Yes | No | No |

#### Wikis (`wikis_controller`)
- Total Routes: 3
- Auth Required: 2
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/projects/ecookbook/wiki` | Project wiki | No | No | No |
| POST | `/projects/ecookbook/wiki` | Create wiki | Yes | No | No |
| DELETE | `/projects/ecookbook/wiki` | Delete wiki | Yes | No | No |

#### Workflows (`workflows_controller`)
- Total Routes: 4
- Auth Required: 4
- XHR Routes: 0

| Method | Path | Description | Auth | XHR | Params |
|--------|------|-------------|------|-----|--------|
| GET | `/workflows` | List workflows | Yes | No | No |
| GET | `/workflows/edit` | Edit workflow | Yes | No | No |
| GET | `/workflows/permissions` | Workflow permissions | Yes | No | No |
| GET | `/workflows/copy` | Copy workflow | Yes | No | No |

## 3. Generated Test Cases

**Total Test Cases Generated:** 24

### 3.1 Test Case Summary

| # | Test Name | Controller | Route | Method | Auth | XHR |
|---|-----------|------------|-------|--------|------|-----|
| 1 | users index requires login... | users | `/users` | GET | Yes | No |
| 2 | user show anonymous... | users | `/users/#{user.id}` | GET | Yes | No |
| 3 | users new requires login... | users | `/users/new` | GET | Yes | No |
| 4 | user edit requires login... | users | `/users/#{user.id}/edit` | GET | Yes | No |
| 5 | time entries list anonymous... | timelog | `/time_entries` | GET | Yes | No |
| 6 | time entries new requires login... | timelog | `/time_entries/new` | GET | Yes | No |
| 7 | project ecookbook time entries anonymous... | timelog | `/projects/ecookbook/time_entri` | GET | Yes | No |
| 8 | project ecookbook time entries new requi... | timelog | `/projects/ecookbook/time_entri` | GET | Yes | No |
| 9 | watchers autocomplete_for_user requires ... | watchers | `/watchers/autocomplete_for_use` | GET | Yes | Yes |
| 10 | roles index requires login... | roles | `/roles` | GET | Yes | No |
| 11 | roles new requires login... | roles | `/roles/new` | GET | Yes | No |
| 12 | role show requires login... | roles | `/roles/#{role.id}` | GET | Yes | No |
| 13 | role edit requires login... | roles | `/roles/#{role.id}/edit` | GET | Yes | No |
| 14 | workflows index requires login... | workflows | `/workflows` | GET | Yes | No |
| 15 | workflows edit requires login... | workflows | `/workflows/edit` | GET | Yes | No |
| 16 | workflows permissions requires login... | workflows | `/workflows/permissions` | GET | Yes | No |
| 17 | workflows copy requires login... | workflows | `/workflows/copy` | GET | Yes | No |
| 18 | trackers index requires login... | trackers | `/trackers` | GET | Yes | No |
| 19 | trackers new requires login... | trackers | `/trackers/new` | GET | Yes | No |
| 20 | tracker edit requires login... | trackers | `/trackers/#{tracker.id}/edit` | GET | Yes | No |
| 21 | search index anonymous... | search | `/search` | GET | No | No |
| 22 | project ecookbook search anonymous... | projects | `/projects/ecookbook/search` | GET | No | No |
| 23 | search with query anonymous... | search | `/search?q=test` | GET | No | No |
| 24 | issues gantt anonymous... | issues | `/issues/gantt` | GET | No | No |

### 3.2 Test Coverage by Controller

| Controller | Test Count |
|------------|------------|
| users | 4 |
| timelog | 4 |
| roles | 4 |
| workflows | 4 |
| trackers | 3 |
| search | 2 |
| watchers | 1 |
| projects | 1 |
| issues | 1 |

## 4. Coverage Gaps Analysis

### 4.1 What Couldn't Be Covered and Why

| Controller | Reason | Priority |
|------------|--------|----------|
| context_menus | Requires XHR headers (current: 79.7%) | MEDIUM |
| repositories | Requires VCS repository setup (current: 65.8%) | LOW |
| redmine_plugin_generator | Plugin-related controller (current: 0.0%) | LOW |

### 4.2 Gap Summary

| Priority | Count |
|----------|-------|
| MEDIUM | 1 |
| LOW | 2 |

---
*Report generated by ENS 491-2 Automated Test Generation System*