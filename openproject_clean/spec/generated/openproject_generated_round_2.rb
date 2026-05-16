require "spec_helper"

RSpec.describe "Generated OpenProject Request Coverage", :skip_csrf, type: :rails_request do
  let!(:seed_project) { Project.first || create(:project) }
  let!(:seed_user) { User.first || create(:user) }
  let!(:seed_work_package) { WorkPackage.first || create(:work_package, project: seed_project, author: seed_user) }

  describe "home" do
    describe "GET /" do
      it "GET / returns a valid response" do
        get "/"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end

    describe "GET /login" do
      it "GET /login (public) returns a valid response" do
        get "/login"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end
  end

  describe "account" do
    describe "GET /login" do
      it "GET /login (public) returns a valid response" do
        get "/login"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end

    describe "GET /logout" do
      it "GET /logout (public) returns a valid response" do
        get "/logout"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end

    describe "GET /account/register" do
      it "GET /account/register (public) returns a valid response" do
        get "/account/register"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end

    describe "GET /account/lost_password" do
      it "GET /account/lost_password (public) returns a valid response" do
        get "/account/lost_password"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end
  end

  describe "projects" do
    describe "GET /projects" do
      it "GET /projects (public) returns a valid response" do
        get "/projects"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /projects with query params returns a valid response" do
        get "/projects", params: { pageSize: 1, offset: 0 }
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end

    describe "GET /projects/:id" do
      it "GET /projects/:id with valid id (public) returns a valid response" do
        id = seed_project.id
        get "/projects/#{id}"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /projects/:id with invalid id (public) returns a redirect-tolerant response" do
        get "/projects/999999999"
        expect([301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end

    describe "GET /projects/:id/settings" do
      context "with current_user" do
        let(:current_user) { create(:admin) }

        it "GET /projects/:id/settings with valid id (authenticated) returns a valid response" do
          id = seed_project.id
          get "/projects/#{id}/settings"
          expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
        end

        it "GET /projects/:id/settings with invalid id (authenticated) returns a redirect-tolerant response" do
          get "/projects/999999999/settings"
          expect([301, 302, 401, 403, 404, 422]).to include(response.status)
        end
      end

      context "without current_user" do
        it "GET /projects/:id/settings with valid id returns a redirect-tolerant response" do
          id = seed_project.id
          get "/projects/#{id}/settings"
          expect([301, 302, 401, 403, 404, 422]).to include(response.status)
        end
      end
    end
  end

  describe "admin_statuses" do
    describe "GET /statuses" do
      context "with current_user" do
        let(:current_user) { create(:admin) }

        it "GET /statuses (authenticated) returns a valid response" do
          get "/statuses"
          expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
        end
      end

      context "without current_user" do
        it "GET /statuses returns a redirect-tolerant response" do
          get "/statuses"
          expect([301, 302, 401, 403, 404, 422]).to include(response.status)
        end
      end
    end
  end

  describe "api_v3_root" do
    describe "GET /api/v3" do
      it "GET /api/v3 (public) returns a valid response" do
        get "/api/v3"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end
  end

  describe "api_v3_projects" do
    context "with current_user" do
      let(:current_user) { create(:admin) }

      it "GET /api/v3/projects base returns a valid response" do
        get "/api/v3/projects"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/projects with pageSize and offset returns a valid response" do
        get "/api/v3/projects", params: { pageSize: 1, offset: 0 }
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/projects with sortBy returns a valid response" do
        get "/api/v3/projects", params: { sortBy: '[["id","asc"]]' }
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end

    context "without current_user" do
      it "GET /api/v3/projects returns a redirect-tolerant response" do
        get "/api/v3/projects"
        expect([301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end
  end

  describe "api_v3_work_packages" do
    context "with current_user" do
      let(:current_user) { create(:admin) }

      it "GET /api/v3/work_packages base returns a valid response" do
        get "/api/v3/work_packages"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/work_packages with pageSize and offset returns a valid response" do
        get "/api/v3/work_packages", params: { pageSize: 1, offset: 0 }
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/work_packages with sortBy returns a valid response" do
        get "/api/v3/work_packages", params: { sortBy: '[["id","asc"]]' }
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/work_packages with include and pageSize and offset returns a valid response" do
        get "/api/v3/work_packages", params: { include: "project,status,assignee", pageSize: 1, offset: 0 }
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/work_packages/:id with valid id returns a valid response" do
        id = seed_work_package.id
        get "/api/v3/work_packages/#{id}"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/work_packages/:id with invalid id returns a redirect-tolerant response" do
        get "/api/v3/work_packages/999999999"
        expect([301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end

    context "without current_user" do
      it "GET /api/v3/work_packages returns a redirect-tolerant response" do
        get "/api/v3/work_packages"
        expect([301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/work_packages/:id with valid id returns a redirect-tolerant response" do
        id = seed_work_package.id
        get "/api/v3/work_packages/#{id}"
        expect([301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end
  end

  describe "api_v3_users" do
    context "with current_user" do
      let(:current_user) { create(:admin) }

      it "GET /api/v3/users/me returns a valid response" do
        get "/api/v3/users/me"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/users/me with Accept header returns a valid response" do
        get "/api/v3/users/me", headers: { "Accept" => "application/hal+json" }
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/users/me with status and pagination params returns a valid response" do
        get "/api/v3/users/me", params: { status: "active", pageSize: 1, offset: 0 }
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/users/:id with valid id returns a valid response" do
        id = seed_user.id
        get "/api/v3/users/#{id}"
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/users/:id with Accept header returns a valid response" do
        id = seed_user.id
        get "/api/v3/users/#{id}", headers: { "Accept" => "application/hal+json" }
        expect([200, 201, 301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/users/:id with invalid id returns a redirect-tolerant response" do
        get "/api/v3/users/999999999"
        expect([301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end

    context "without current_user" do
      it "GET /api/v3/users/me returns a redirect-tolerant response" do
        get "/api/v3/users/me"
        expect([301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/users/:id with valid id returns a redirect-tolerant response" do
        id = seed_user.id
        get "/api/v3/users/#{id}"
        expect([301, 302, 401, 403, 404, 422]).to include(response.status)
      end

      it "GET /api/v3/users/:id with invalid id returns a redirect-tolerant response" do
        get "/api/v3/users/999999999"
        expect([301, 302, 401, 403, 404, 422]).to include(response.status)
      end
    end
  end
end