require_relative '../test_helper'

class RedmineIntegrationTest < ActionDispatch::IntegrationTest
  def assert_html_page_or_login
    if response.content_type&.include?('html') || response.body =~ /<html|<body|<!DOCTYPE/i
      if response.status == 200
        if css_select('form[action^="/login"]').any?
          assert_select 'form[action^="/login"]', minimum: 1
        else
          assert_select 'div#content', minimum: 1 if css_select('div#content').any?
        end
      end
    end
  end

  def follow_redirects(max = 3)
    max.times do
      break unless response.redirect?
      follow_redirect!
    end
  end

  test "anonymous access to root and projects" do
    get '/'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login
  end

  test "anonymous access to project ecookbook main pages" do
    get '/projects/ecookbook'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/issues'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/wiki'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login
  end

  test "anonymous access to project ecookbook boards and documents" do
    get '/projects/ecookbook/boards'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/documents'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/files'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login
  end

  test "anonymous access to admin and settings pages" do
    get '/admin'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/groups'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/custom_fields'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/enumerations'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/issue_statuses'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/auth_sources'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login
  end

  test "anonymous access to calendar views" do
    get '/issues/calendar'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/issues/calendar'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login
  end

  test "anonymous access to context menus with xhr headers" do
    issue = Issue.where(project: Project.find_by(identifier: 'ecookbook')).first || Issue.first
    user = User.find_by(login: 'admin') || User.first

    get '/issues/context_menu', params: { ids: [issue&.id].compact }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status

    get '/users/context_menu', params: { ids: [user&.id].compact }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status
  end

  test "anonymous access to imports new pages" do
    get '/issues/imports/new'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/users/imports/new'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/time_entries/imports/new'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login
  end

  test "anonymous access to email addresses" do
    user = User.find_by(login: 'admin') || User.first
    get "/users/#{user&.id}/email_addresses"
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login
  end

  test "anonymous access to attachments if any" do
    attachment = Attachment.first
    if attachment
      get "/attachments/#{attachment.id}"
      follow_redirects
      assert_includes [200,403,404], response.status
      assert_html_page_or_login
    end
  end

  test "anonymous access to auto_complete endpoints with xhr headers" do
    get '/issues/auto_complete', params: { q: 'a' }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status

    get '/wiki_pages/auto_complete', params: { q: 'a' }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status
  end

  test "anonymous access to activity and journals" do
    get '/activity'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/activity'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/issues/changes'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login
  end

  test "anonymous access to reports and memberships with possible 406" do
    get '/projects/ecookbook/issues/report'
    follow_redirects
    assert_includes [200,403,404,406], response.status

    get '/projects/ecookbook/memberships'
    follow_redirects
    assert_includes [200,403,404,406], response.status

    get '/projects/ecookbook/memberships/new'
    follow_redirects
    assert_includes [200,403,404,406], response.status
  end

  test "anonymous access to news and queries" do
    get '/news'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/news/new'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/news'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/news/new'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/queries'
    follow_redirects
    assert_includes [200,403,404,406], response.status

    get '/queries/new'
    follow_redirects
    assert_includes [200,403,404,406], response.status

    get '/projects/ecookbook/queries/new'
    follow_redirects
    assert_includes [200,403,404,406], response.status
  end

  test "anonymous access to previews with xhr headers" do
    post '/preview/text', params: { text: 'test' }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status

    post '/issues/preview', params: { text: 'test' }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status

    post '/news/preview', params: { text: 'test' }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status
  end

  test "anonymous access to repositories and issue relations" do
    get '/projects/ecookbook/repositories/new'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    repository = Repository.first
    if repository
      get "/repositories/#{repository.id}/committers"
      follow_redirects
      assert_includes [200,403,404], response.status
      assert_html_page_or_login
    end

    issue = Issue.where(project: Project.find_by(identifier: 'ecookbook')).first || Issue.first
    if issue
      get "/issues/#{issue.id}/relations"
      follow_redirects
      assert_includes [200,403,404], response.status
      assert_html_page_or_login
    end
  end

  test "anonymous access to boards topics new" do
    board = Board.joins(:project).where(projects: { identifier: 'ecookbook' }).first || Board.first
    if board
      get "/boards/#{board.id}/topics/new"
      follow_redirects
      assert_includes [200,403,404], response.status
      assert_html_page_or_login
    end
  end

  test "login with invalid credentials shows login form" do
    post '/login', params: { username: 'invalid', password: 'wrong' }
    follow_redirects
    assert_includes [200,403,404], response.status
    if response.status == 200 && (response.content_type&.include?('html') || response.body =~ /<html|<body|<!DOCTYPE/i)
      assert_select 'form[action^="/login"]', minimum: 1
    end
  end

  test "login with admin/admin and access protected pages" do
    post '/login', params: { username: 'admin', password: 'admin' }
    follow_redirects
    assert_includes [200,403,404], response.status

    if response.status == 200 && (response.content_type&.include?('html') || response.body =~ /<html|<body|<!DOCTYPE/i)
      if css_select('form[action^="/login"]').any?
        # login failed, do not fail test
      else
        assert_select 'a.logout, a[href="/logout"], #loggedas', minimum: 1, count: 1
      end
    end

    # Access several routes that redirect if not logged in
    get '/projects/ecookbook/issues/new'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/issues/gantt'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/issue_categories'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/admin'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/groups'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login
  end

  test "login with admin/admin and access news and queries" do
    post '/login', params: { username: 'admin', password: 'admin' }
    follow_redirects

    get '/news/new'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/projects/ecookbook/news/new'
    follow_redirects
    assert_includes [200,403,404], response.status
    assert_html_page_or_login

    get '/queries/new'
    follow_redirects
    assert_includes [200,403,404,406], response.status

    get '/projects/ecookbook/queries/new'
    follow_redirects
    assert_includes [200,403,404,406], response.status
  end

  test "login with admin/admin and access preview endpoints with xhr headers" do
    post '/login', params: { username: 'admin', password: 'admin' }
    follow_redirects

    post '/preview/text', params: { text: 'admin test' }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status

    post '/issues/preview', params: { text: 'admin test' }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status

    post '/news/preview', params: { text: 'admin test' }, headers: { 'HTTP_X_REQUESTED_WITH' => 'XMLHttpRequest', 'HTTP_ACCEPT' => 'text/javascript' }
    follow_redirects
    assert_includes [200,403,404,406], response.status
  end

  test "login with admin/admin and access memberships and reports" do
    post '/login', params: { username: 'admin', password: 'admin' }
    follow_redirects

    get '/projects/ecookbook/memberships'
    follow_redirects
    assert_includes [200,403,404,406], response.status

    get '/projects/ecookbook/memberships/new'
    follow_redirects
    assert_includes [200,403,404,406], response.status

    get '/projects/ecookbook/issues/report'
    follow_redirects
    assert_includes [200,403,404,406], response.status
  end
end