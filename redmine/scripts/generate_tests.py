import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()

REDMINE_ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = REDMINE_ROOT / "test" / "generated" / "generated_suite_test.rb"

PROMPT = """
You are generating Ruby Minitest integration tests for a Redmine (Rails) app.

OUTPUT FORMAT (STRICT):
- Output ONLY a single Ruby file (no markdown, no explanations).
- First non-comment line must be exactly: require_relative '../test_helper'
- Define exactly ONE test class inheriting from ActionDispatch::IntegrationTest.
- Use only HTTP requests (get/post/patch/delete) and follow_redirect! when needed.
- Do NOT use Capybara, Selenium, or JS-based assertions.

SUITE SIZE (STRICT):
- Generate 18–25 separate `test` blocks.
- Each test should make 1–5 HTTP requests.

CRITICAL REDMINE BEHAVIOR RULES (MUST FOLLOW):

- Many endpoints redirect when accessed anonymously, but the final page is NOT guaranteed
  to be the login page (it may be a public page, error page, permission page, or non-HTML response).

- NEVER assume that an anonymous request ends on the login page.

- NEVER assert_response :success immediately after a request unless redirects are fully handled.

- After EVERY request:
  - If response.redirect?, call follow_redirect! (repeat up to 3 times).
  - Then assert that response.status is in an allowed set:
    - Default allowed statuses: [200, 403, 404]
    - For XHR/JS endpoints and known “Not Acceptable” cases: [200, 403, 404, 406]

- IMPORTANT: Only assert HTML selectors when:
    response.status == 200
    AND the response appears to be HTML (Content-Type includes 'html' OR body contains '<html' OR '<body' OR '<!DOCTYPE').

- After redirects (and ONLY if the response appears to be HTML as defined above):
  - FIRST check whether the page is actually a login page.
    - A page is considered a login page ONLY IF a login form exists.
  - If (and only if) the login form exists:
        assert_select 'form[action^="/login"]', minimum: 1
  - Otherwise (NOT a login page):
      - If div#content exists, assert it:
          assert_select 'div#content', minimum: 1
      - If div#content does NOT exist, DO NOT fail the test. Do not assert body/html/title.
        Status being allowed is sufficient.

- The generated Ruby file MUST implement this via a helper method (e.g., assert_html_page_or_login)
  and MUST NOT contain raw duplicated selector logic in every test.

XHR / JS ENDPOINT RULE (VERY IMPORTANT):
- Some Redmine endpoints require XHR / JS Accept headers; otherwise they may return 406.
- For these endpoints, send headers:
    'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest'
    'HTTP_ACCEPT' => 'text/javascript'
- Apply these headers to:
  - GET /issues/context_menu
  - GET /users/context_menu
  - GET /issues/auto_complete
  - GET /wiki_pages/auto_complete
  - POST /preview/text
  - POST /issues/preview
  - POST /news/preview

AUTHENTICATION (VERY IMPORTANT FOR COVERAGE):
- At least 6 tests MUST be authenticated flows:
  - POST /login with admin/admin once inside the test
  - If it redirects, follow_redirect! (up to 3 times)
  - Then immediately request several routes that would otherwise redirect.
- If admin/admin login fails (no redirect / not logged in), do NOT fail; proceed but accept redirects.

ID RULES (STRICT):
- NEVER hardcode numeric IDs like /issues/1 or /attachments/1.
- Use fixture-safe lookups:
  - user = User.find_by(login: 'admin') || User.first
  - project identifier: 'ecookbook'
  - issue = Issue.where(project: Project.find_by(identifier: 'ecookbook')).first || Issue.first
  - attachment = Attachment.first
  - board = Board.joins(:project).where(projects: { identifier: 'ecookbook' }).first || Board.first
  - repository = Repository.first

ASSERTION RULES:
- Do NOT assert unstable selectors:
  div.activity, div.versions, div#wiki, div#wiki-content
- Prefer (when HTML assertions are allowed by the rule above):
  assert_select 'div#content', minimum: 1
  assert_select 'form[action^="/login"]', minimum: 1

LOGIN TESTS (REQUIRED):
- One test with invalid credentials → login form still shown (assert form[action^="/login"] exists) ONLY if response appears to be HTML.
- One test with admin/admin:
  - If redirect, follow and assert logout indicator only if it exists in the HTML:
    a.logout OR a[href="/logout"] OR #loggedas
  - If not redirected, accept [200, 403, 404] without failing.

ROUTES TO EXERCISE:
- Use these existing routes (and do NOT invent others):

Core:
  GET /, GET /login, GET /projects, GET /projects/ecookbook

Project:
  GET /projects/ecookbook/issues
  GET /projects/ecookbook/issues/new
  GET /projects/ecookbook/wiki
  GET /projects/ecookbook/roadmap
  GET /projects/ecookbook/boards
  GET /projects/ecookbook/documents
  GET /projects/ecookbook/files
  GET /projects/ecookbook/issues/gantt
  GET /projects/ecookbook/issue_categories

Calendars:
  GET /issues/calendar
  GET /projects/ecookbook/issues/calendar

Admin/settings:
  GET /admin, /groups, /custom_fields, /enumerations, /issue_statuses, /auth_sources

Context menus (XHR headers required; accept 406):
  GET /issues/context_menu (params ids[])
  GET /users/context_menu (params ids[])

Imports:
  GET /issues/imports/new
  GET /users/imports/new
  GET /time_entries/imports/new

Email addresses:
  GET /users/:user_id/email_addresses

Attachments:
  GET /attachments/:id (ONLY if Attachment.first exists; accept 404 in allowed statuses)

Auto-complete (REAL ROUTES, XHR headers required; accept 406/404):
  GET /issues/auto_complete?q=a
  GET /wiki_pages/auto_complete?q=a

Additional routes to hit 0% controllers (from rails routes):
  Activities:
    GET /activity
    GET /projects/ecookbook/activity
  Journals:
    GET /issues/changes
  Reports (may return 406; accept it):
    GET /projects/ecookbook/issues/report
  Members (may return 406; accept it):
    GET /projects/ecookbook/memberships
    GET /projects/ecookbook/memberships/new
  News:
    GET /news
    GET /news/new
    GET /projects/ecookbook/news
    GET /projects/ecookbook/news/new
  Previews (XHR headers required; accept 406):
    POST /preview/text (params: text)
    POST /issues/preview (params: text)
    POST /news/preview (params: text)
  Queries (may return 406; accept it):
    GET /queries
    GET /queries/new
    GET /projects/ecookbook/queries/new
  Repositories:
    GET /projects/ecookbook/repositories/new
    (Optional if Repository.first exists) GET /repositories/:id/committers
  Issue relations (only if Issue exists):
    GET /issues/:issue_id/relations
  Messages (only if Board exists):
    GET /boards/:board_id/topics/new

COVERAGE GOAL:
- Maximize controller coverage by hitting routes both anonymously and (more importantly) after login.
- Never fail due to missing fixtures, permissions, optional features, non-HTML 200 responses, status 403/404, or 406 on XHR-required endpoints.
Generate the Ruby test file now.
"""



def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY env var. Set it before running.")

    llm = ChatOpenAI(
        model="gpt-4.1-mini",  # good balance for codegen/cost
        temperature=0
    )

    ruby_code = llm.invoke(PROMPT).content

    # --- quick sanity checks so bad generations fail fast ---
    if "```" in ruby_code:
        raise SystemExit("Model returned markdown fences. Refine prompt / strip fences.")

    if "require_relative '../test_helper'" not in ruby_code and 'require_relative "../test_helper"' not in ruby_code:
        raise SystemExit("Generated code is missing require_relative '../test_helper'.")

    if "ActionDispatch::IntegrationTest" not in ruby_code:
        raise SystemExit("Generated code is not an IntegrationTest.")

    if "test " not in ruby_code:
        raise SystemExit("No Minitest test blocks found.")


    (REDMINE_ROOT / "test" / "generated").mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(ruby_code, encoding="utf-8")
    print(f"Wrote: {OUT_FILE}")

if __name__ == "__main__":
    main()
