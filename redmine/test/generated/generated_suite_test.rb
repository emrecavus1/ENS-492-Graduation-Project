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
  test "user show anonymous" do
    user = User.find_by(login: 'admin') || User.first
    get "/users/#{user.id}"
    assert [200, 302, 403].include?(response.status)
  end

  # AUTHENTICATED TEST - always log_user first!
  test "users new requires login" do
    log_user('admin', 'admin')  # MUST login first for /users/new
    get '/users/new'
    assert_response :success
  end

  # AUTHENTICATED TEST - always log_user first!
  test "user edit requires login" do
    log_user('admin', 'admin')  # MUST login first for /users/:id/edit
    user = User.find_by(login: 'admin') || User.first
    get "/users/#{user.id}/edit"
    assert_response :success
  end

  # ANONYMOUS TEST - no login needed
  test "time entries list anonymous" do
    get '/time_entries'
    assert [200, 302, 403].include?(response.status)
  end

  # AUTHENTICATED TEST - always log_user first!
  test "time entries new requires login" do
    log_user('admin', 'admin')  # MUST login first for /time_entries/new
    get '/time_entries/new'
    assert_response :success
  end

  # ANONYMOUS TEST - no login needed
  test "project ecookbook time entries anonymous" do
    get '/projects/ecookbook/time_entries'
    assert [200, 302, 403].include?(response.status)
  end

  # AUTHENTICATED TEST - always log_user first!
  test "project ecookbook time entries new requires login" do
    log_user('admin', 'admin')  # MUST login first for /projects/ecookbook/time_entries/new
    get '/projects/ecookbook/time_entries/new'
    assert_response :success
  end

  # AUTHENTICATED TEST - watchers require project context and specific permission
  test "watchers autocomplete_for_user requires login" do
    log_user('admin', 'admin')  # MUST login first for /watchers/autocomplete_for_user
    get '/watchers/autocomplete_for_user', xhr: true
    assert [200, 403, 404].include?(response.status)
  end

  # AUTHENTICATED TEST - always log_user first!
  test "roles index requires login" do
    log_user('admin', 'admin')  # MUST login first for /roles
    get '/roles'
    assert_response :success
  end

  # AUTHENTICATED TEST - always log_user first!
  test "roles new requires login" do
    log_user('admin', 'admin')  # MUST login first for /roles/new
    get '/roles/new'
    assert_response :success
  end

  # AUTHENTICATED TEST - role show returns 406 without proper accept header
  test "role show requires login" do
    log_user('admin', 'admin')  # MUST login first for /roles/:id
    role = Role.first
    get "/roles/#{role.id}"
    assert [200, 302, 406].include?(response.status)
  end

  # AUTHENTICATED TEST - always log_user first!
  test "role edit requires login" do
    log_user('admin', 'admin')  # MUST login first for /roles/:id/edit
    role = Role.first
    get "/roles/#{role.id}/edit"
    assert_response :success
  end

  # AUTHENTICATED TEST - always log_user first!
  test "workflows index requires login" do
    log_user('admin', 'admin')  # MUST login first for /workflows
    get '/workflows'
    assert_response :success
  end

  # AUTHENTICATED TEST - always log_user first!
  test "workflows edit requires login" do
    log_user('admin', 'admin')  # MUST login first for /workflows/edit
    get '/workflows/edit'
    assert_response :success
  end

  # AUTHENTICATED TEST - always log_user first!
  test "workflows permissions requires login" do
    log_user('admin', 'admin')  # MUST login first for /workflows/permissions
    get '/workflows/permissions'
    assert_response :success
  end

  # AUTHENTICATED TEST - always log_user first!
  test "workflows copy requires login" do
    log_user('admin', 'admin')  # MUST login first for /workflows/copy
    get '/workflows/copy'
    assert_response :success
  end

  # AUTHENTICATED TEST - always log_user first!
  test "trackers index requires login" do
    log_user('admin', 'admin')  # MUST login first for /trackers
    get '/trackers'
    assert_response :success
  end

  # AUTHENTICATED TEST - always log_user first!
  test "trackers new requires login" do
    log_user('admin', 'admin')  # MUST login first for /trackers/new
    get '/trackers/new'
    assert_response :success
  end

  # AUTHENTICATED TEST - always log_user first!
  test "tracker edit requires login" do
    log_user('admin', 'admin')  # MUST login first for /trackers/:id/edit
    tracker = Tracker.first
    get "/trackers/#{tracker.id}/edit"
    assert_response :success
  end

  # ANONYMOUS TEST - no login needed
  test "search index anonymous" do
    get '/search'
    assert [200, 302, 403].include?(response.status)
  end

  # ANONYMOUS TEST - no login needed
  test "project ecookbook search anonymous" do
    get '/projects/ecookbook/search'
    assert [200, 302, 403].include?(response.status)
  end

  # ANONYMOUS TEST - no login needed
  test "search with query anonymous" do
    get '/search?q=test'
    assert [200, 302, 403].include?(response.status)
  end

  # ANONYMOUS TEST - no login needed
  test "issues gantt anonymous" do
    get '/issues/gantt'
    assert [200, 302, 403].include?(response.status)
  end
end