# OpenProject Test Generation Report

## 1. API Endpoint Coverage Summary

| Metric | Value |
|--------|-------|
| Total Resources | 8 |
| Total Endpoints | 18 |
| Zero Coverage Resources | 0 |
| Well Covered (>80%) | 6 |
| Endpoint Coverage | 88.24% |
| Safe Endpoints Hit / Total | 15 / 17 |
| Public Safe Endpoints | 9 |
| Authenticated Safe Endpoints | 8 |

### 1.1 Endpoint Coverage by Resource

| Metric | Value |
|--------|-------|
| Well Covered Resources (>80%) | 6 |
| Zero Coverage Resources | 0 |

## 2. Endpoint Statistics

| Metric | Value |
|--------|-------|
| Public Endpoints | 9 |
| Authenticated Endpoints | 9 |
| Safe Endpoints | 17 |

| Method | Count |
|--------|-------|
| GET | 17 |
| POST | 1 |
| PATCH | 0 |
| DELETE | 0 |

## 3. API Endpoint Catalog

### home

- Base Path: `/`
- Description: Basic app entry routes
- Total Endpoints: 1
- Safe Endpoints: 1
- Auth Required Endpoints: 0

| Method | Path | Auth | Safe | Description |
|--------|------|------|------|-------------|
| GET | `/` | No | Yes | Application home page |

### account

- Base Path: `/login`
- Description: Authentication and account entry routes
- Total Endpoints: 4
- Safe Endpoints: 4
- Auth Required Endpoints: 0

| Method | Path | Auth | Safe | Description |
|--------|------|------|------|-------------|
| GET | `/login` | No | Yes | Login page |
| GET | `/logout` | No | Yes | Logout route |
| GET | `/account/register` | No | Yes | Registration page |
| GET | `/account/lost_password` | No | Yes | Lost password page |

### projects

- Base Path: `/projects`
- Description: Project listing and detail routes
- Total Endpoints: 3
- Safe Endpoints: 3
- Auth Required Endpoints: 1

| Method | Path | Auth | Safe | Description |
|--------|------|------|------|-------------|
| GET | `/projects` | No | Yes | List projects |
| GET | `/projects/:id` | No | Yes | Project details |
| GET | `/projects/:id/settings` | Yes | Yes | Project settings |

### admin_statuses

- Base Path: `/statuses`
- Description: Administrative statuses routes
- Total Endpoints: 2
- Safe Endpoints: 1
- Auth Required Endpoints: 2

| Method | Path | Auth | Safe | Description |
|--------|------|------|------|-------------|
| GET | `/statuses` | Yes | Yes | List statuses |
| POST | `/statuses` | Yes | No | Create status |

### api_v3_root

- Base Path: `/api/v3`
- Description: API root and discovery
- Total Endpoints: 2
- Safe Endpoints: 2
- Auth Required Endpoints: 0

| Method | Path | Auth | Safe | Description |
|--------|------|------|------|-------------|
| GET | `/api/v3` | No | Yes | API v3 root |
| GET | `/api/v3/configuration` | No | Yes | API v3 configuration |

### api_v3_projects

- Base Path: `/api/v3/projects`
- Description: API v3 projects
- Total Endpoints: 2
- Safe Endpoints: 2
- Auth Required Endpoints: 2

| Method | Path | Auth | Safe | Description |
|--------|------|------|------|-------------|
| GET | `/api/v3/projects` | Yes | Yes | List API projects |
| GET | `/api/v3/projects/:id` | Yes | Yes | Show API project |

### api_v3_work_packages

- Base Path: `/api/v3/work_packages`
- Description: API v3 work packages
- Total Endpoints: 2
- Safe Endpoints: 2
- Auth Required Endpoints: 2

| Method | Path | Auth | Safe | Description |
|--------|------|------|------|-------------|
| GET | `/api/v3/work_packages` | Yes | Yes | List work packages |
| GET | `/api/v3/work_packages/:id` | Yes | Yes | Show work package |

### api_v3_users

- Base Path: `/api/v3/users`
- Description: API v3 users
- Total Endpoints: 2
- Safe Endpoints: 2
- Auth Required Endpoints: 2

| Method | Path | Auth | Safe | Description |
|--------|------|------|------|-------------|
| GET | `/api/v3/users/me` | Yes | Yes | Current user |
| GET | `/api/v3/users/:id` | Yes | Yes | Show user |

## 4. Resource Coverage

| Resource | Endpoints | Endpoints Hit | Coverage | Auth Required |
|----------|-----------|-------|----------|---------------|
| home | 1 | 1 | 100.0% | 0 |
| account | 4 | 4 | 100.0% | 0 |
| projects | 3 | 3 | 100.0% | 1 |
| admin_statuses | 1 | 1 | 100.0% | 2 |
| api_v3_work_packages | 2 | 2 | 100.0% | 2 |
| api_v3_users | 2 | 2 | 100.0% | 2 |
| api_v3_root | 2 | 1 | 50.0% | 0 |
| api_v3_projects | 2 | 1 | 50.0% | 2 |

## 5. Generated Test Cases

**Total Test Cases Parsed:** 36

| # | Test Name | Resource | Method | Auth | Endpoint |
|---|-----------|----------|--------|------|----------|
| 1 | GET / (public) | home | GET | No | `/` |
| 2 | GET /login (public) | account | GET | No | `/login` |
| 3 | GET /login (public) | account | GET | No | `/login` |
| 4 | GET /logout (public) | account | GET | No | `/logout` |
| 5 | GET /account/register (public) | account | GET | No | `/account/register` |
| 6 | GET /account/lost_password (public) | account | GET | No | `/account/lost_password` |
| 7 | GET /projects (public) | projects | GET | No | `/projects` |
| 8 | GET /projects with query params (public) | projects | GET | No | `/projects` |
| 9 | GET /projects/:id with valid id (public) | projects | GET | No | `/projects/:id` |
| 10 | GET /projects/:id with invalid id (publi... | projects | GET | Yes | `/projects/:id` |
| 11 | GET /projects/:id/settings with valid id... | projects | GET | Yes | `/projects/:id/settings` |
| 12 | GET /projects/:id/settings with invalid ... | projects | GET | Yes | `/projects/:id/settings` |
| 13 | GET /projects/:id/settings with valid id... | projects | GET | Yes | `/projects/:id/settings` |
| 14 | GET /statuses (authenticated) | admin_statuses | GET | Yes | `/statuses` |
| 15 | GET /statuses (anonymous) | admin_statuses | GET | No | `/statuses` |
| 16 | GET /api/v3 (public) | api_v3_root | GET | Yes | `/api/v3` |
| 17 | GET /api/v3/projects base | api_v3_projects | GET | No | `/api/v3/projects` |
| 18 | GET /api/v3/projects with pageSize and o... | api_v3_projects | GET | Yes | `/api/v3/projects` |
| 19 | GET /api/v3/projects with sortBy | api_v3_projects | GET | Yes | `/api/v3/projects` |
| 20 | GET /api/v3/projects anonymous | api_v3_projects | GET | Yes | `/api/v3/projects` |
| 21 | GET /api/v3/work_packages base | api_v3_work_packages | GET | No | `/api/v3/work_packages` |
| 22 | GET /api/v3/work_packages with pageSize ... | api_v3_work_packages | GET | No | `/api/v3/work_packages` |
| 23 | GET /api/v3/work_packages with sortBy | api_v3_work_packages | GET | No | `/api/v3/work_packages` |
| 24 | GET /api/v3/work_packages with include a... | api_v3_work_packages | GET | No | `/api/v3/work_packages` |
| 25 | GET /api/v3/work_packages/:id with valid... | api_v3_work_packages | GET | Yes | `/api/v3/work_packages/:id` |
| 26 | GET /api/v3/work_packages/:id with inval... | api_v3_work_packages | GET | Yes | `/api/v3/work_packages/:id` |
| 27 | GET /api/v3/work_packages anonymous | api_v3_work_packages | GET | Yes | `/api/v3/work_packages` |
| 28 | GET /api/v3/users/me base | api_v3_users | GET | No | `/api/v3/users/me` |
| 29 | GET /api/v3/users/me with Accept header | api_v3_users | GET | No | `/api/v3/users/me` |
| 30 | GET /api/v3/users/me with status and pag... | api_v3_users | GET | No | `/api/v3/users/me` |
| 31 | GET /api/v3/users/:id with valid id | api_v3_users | GET | No | `/api/v3/users/:id` |
| 32 | GET /api/v3/users/:id with Accept header | api_v3_users | GET | Yes | `/api/v3/users/:id` |
| 33 | GET /api/v3/users/:id with invalid id | api_v3_users | GET | Yes | `/api/v3/users/:id` |
| 34 | GET /api/v3/users/me anonymous | api_v3_users | GET | No | `/api/v3/users/me` |
| 35 | GET /api/v3/users/:id anonymous with val... | api_v3_users | GET | No | `/api/v3/users/:id` |
| 36 | GET /api/v3/users/:id anonymous with inv... | api_v3_users | GET | No | `/api/v3/users/:id` |

## 6. Coverage Gaps

| Resource | Reason | Priority |
|----------|--------|----------|
| api_v3_root | API v3 resource often needs explicit auth / fixtures (current: 50.0%) | MEDIUM |
| api_v3_projects | API v3 resource often needs explicit auth / fixtures (current: 50.0%) | MEDIUM |
