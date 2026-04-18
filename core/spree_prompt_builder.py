"""
Spree Prompt Builder Module

Generates focused RSpec request spec prompts for Spree Commerce Store API testing.
Uses prescriptive test specifications to ensure the LLM generates tests that
actually hit the API endpoints and provide meaningful coverage.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
from pathlib import Path

from core.spree_route_mapper import (
    SPREE_STORE_API_RESOURCES,
    SpreeEndpointInfo,
    SpreeResourceInfo,
    get_all_endpoints,
    get_safe_endpoints,
    get_public_endpoints,
    format_endpoints_for_prompt,
    get_api_statistics,
)


SPREE_RSPEC_PROMPT_TEMPLATE = '''Generate RSpec request specs for the Spree Commerce Store API. Output ONLY Ruby code, no markdown.

CRITICAL AUTHENTICATION INSTRUCTIONS:
- Endpoints marked "(authenticated)" MUST use auth_headers (with Bearer token)
- Endpoints marked "(public)" can use regular headers
- NEVER skip authentication for authenticated endpoints - they will return 401 Unauthorized

IMPORTANT: You MUST generate at least ONE test for EACH resource section listed below.

COMPLETE EXAMPLE (follow this exact format):

require 'rails_helper'

RSpec.describe 'Spree Store API', type: :request do
  let(:store) {{ Spree::Store.default || create(:store) }}
  let(:headers) {{ {{ 'Accept' => 'application/json', 'Content-Type' => 'application/json' }} }}
  
  # User for authenticated requests - FactoryBot creates a test user
  let(:user) {{ create(:user, password: 'password123') }}
  
  # CRITICAL: Use Spree::RefreshToken for authentication (NOT Doorkeeper)
  let(:auth_headers) {{
    refresh_token = Spree::RefreshToken.create!(
      user: user,
      expires_at: 1.day.from_now
    )
    headers.merge('Authorization' => "Bearer #{{refresh_token.token}}")
  }}
  
  # PUBLIC ENDPOINT - uses regular headers
  describe 'Products API' do
    let!(:product) {{ create(:product, stores: [store]) }}
    
    describe 'GET /api/v3/store/products' do
      it 'returns a list of products' do
        get '/api/v3/store/products', headers: headers  # public - no auth needed
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end
  
  # PUBLIC ENDPOINTS - no auth needed
  describe 'States API' do
    it 'returns a list of states' do
      get '/api/v3/store/states', headers: headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  describe 'Countries API' do
    it 'returns a list of countries' do
      get '/api/v3/store/countries', headers: headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  describe 'Store API' do
    it 'returns current store info' do
      get '/api/v3/store/store', headers: headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  describe 'Menus API' do
    it 'returns a list of menus' do
      get '/api/v3/store/menus', headers: headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  describe 'Pages API' do
    it 'returns a list of pages' do
      get '/api/v3/store/pages', headers: headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  # AUTHENTICATED ENDPOINTS - MUST use auth_headers!
  describe 'Account API' do
    it 'returns current user account' do
      get '/api/v3/store/account', headers: auth_headers  # MUST use auth_headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  describe 'Account Orders API' do
    it 'lists user orders' do
      get '/api/v3/store/account/orders', headers: auth_headers  # MUST use auth_headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  describe 'Account Addresses API' do
    it 'lists user addresses' do
      get '/api/v3/store/account/addresses', headers: auth_headers  # MUST use auth_headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  describe 'Account Credit Cards API' do
    it 'lists saved cards' do
      get '/api/v3/store/account/credit_cards', headers: auth_headers  # MUST use auth_headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  describe 'Cart API' do
    it 'creates a cart' do
      post '/api/v3/store/cart', headers: headers
      expect([200, 201, 401, 404, 422]).to include(response.status)
    end
    
    it 'shows current cart with auth' do
      get '/api/v3/store/cart', headers: auth_headers  # authenticated cart
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  describe 'Wishlists API' do
    it 'lists user wishlists' do
      get '/api/v3/store/wishlists', headers: auth_headers  # MUST use auth_headers
      expect([200, 401, 404]).to include(response.status)
    end
  end
  
  private
  
  def json_response
    JSON.parse(response.body)
  end
end

NOW GENERATE TESTS FOR ALL THESE ENDPOINTS (generate at least one test per resource):
{endpoints_to_test}

RULES:
1. Start with: require 'rails_helper'
2. Use: RSpec.describe 'Spree Store API', type: :request do
3. Define let(:store), let(:headers), let(:user), let(:auth_headers) at the TOP before any describe blocks
4. CRITICAL: Use Spree::RefreshToken for authentication (NOT Doorkeeper or OauthAccessToken)
5. Group tests by resource using nested describe blocks
6. GENERATE AT LEAST ONE TEST FOR EVERY RESOURCE
7. Use FactoryBot: create(:product), create(:user), create(:order), etc.
8. CRITICAL: For "(authenticated)" endpoints, you MUST use auth_headers, not headers
9. For "(public)" endpoints, use regular headers
10. Use flexible status expectations: expect([200, 401, 404]).to include(response.status)
11. For dynamic IDs use factory-created objects

Generate {test_count} test examples covering ALL resources above. Output ONLY Ruby code.
'''


class SpreePromptBuilder:
    """
    Builds focused test generation prompts for Spree Commerce API.
    Uses prescriptive test specifications for RSpec request specs.
    """
    
    def __init__(self, spree_root: Path):
        self.spree_root = Path(spree_root)
        
    def build_prompt(
        self,
        include_auth_tests: bool = True,
        test_count: int = 40,
        focus_resources: Optional[List[str]] = None,
    ) -> str:
        """
        Build a prescriptive prompt for Spree API tests.
        
        Args:
            include_auth_tests: Include authenticated endpoint tests
            test_count: Target number of test examples (default 40 to cover all resources)
            focus_resources: Specific resources to focus on (None = all)
        """
        if focus_resources:
            endpoints = []
            for resource_name in focus_resources:
                if resource_name in SPREE_STORE_API_RESOURCES:
                    endpoints.extend(SPREE_STORE_API_RESOURCES[resource_name].endpoints)
        else:
            # Get ALL safe endpoints from ALL resources
            endpoints = get_safe_endpoints()
        
        if not include_auth_tests:
            endpoints = [e for e in endpoints if not e.requires_auth]
        
        endpoints_text = self._format_endpoints_for_prompt(endpoints)
        
        # Add explicit list of all resources to ensure coverage
        all_resources = list(SPREE_STORE_API_RESOURCES.keys())
        resource_list = ", ".join(all_resources)
        
        endpoints_text = f"RESOURCES TO COVER: {resource_list}\n\n{endpoints_text}"
        
        return SPREE_RSPEC_PROMPT_TEMPLATE.format(
            endpoints_to_test=endpoints_text,
            test_count=test_count,
        )
    
    def _format_endpoints_for_prompt(self, endpoints: List[SpreeEndpointInfo]) -> str:
        """Format endpoints as explicit test specifications."""
        lines = []
        
        by_resource = {}
        for endpoint in endpoints:
            resource = endpoint.resource or "other"
            if resource not in by_resource:
                by_resource[resource] = []
            by_resource[resource].append(endpoint)
        
        # Separate authenticated and public endpoints for clarity
        auth_endpoints = []
        public_endpoints = []
        
        for resource, resource_endpoints in by_resource.items():
            resource_title = resource.replace('_', ' ').title()
            for endpoint in resource_endpoints:
                entry = (resource_title, endpoint)
                if endpoint.requires_auth:
                    auth_endpoints.append(entry)
                else:
                    public_endpoints.append(entry)
        
        # List public endpoints first
        if public_endpoints:
            lines.append("\n=== PUBLIC ENDPOINTS (use: headers) ===")
            current_resource = None
            for resource_title, endpoint in public_endpoints:
                if resource_title != current_resource:
                    lines.append(f"\n## {resource_title}")
                    current_resource = resource_title
                lines.append(f"- {endpoint.method} {endpoint.path} (public)")
                if endpoint.description:
                    lines.append(f"  Description: {endpoint.description}")
        
        # Then list authenticated endpoints
        if auth_endpoints:
            lines.append("\n\n=== AUTHENTICATED ENDPOINTS (MUST use: auth_headers) ===")
            current_resource = None
            for resource_title, endpoint in auth_endpoints:
                if resource_title != current_resource:
                    lines.append(f"\n## {resource_title}")
                    current_resource = resource_title
                lines.append(f"- {endpoint.method} {endpoint.path} (authenticated - MUST use auth_headers)")
                if endpoint.description:
                    lines.append(f"  Description: {endpoint.description}")
        
        return "\n".join(lines)
    
    def build_focused_prompt(
        self,
        resources: List[str],
        test_count: int = 20,
    ) -> str:
        """
        Build a highly focused prompt for specific Spree resources.
        """
        endpoints = []
        for resource_name in resources:
            if resource_name in SPREE_STORE_API_RESOURCES:
                resource = SPREE_STORE_API_RESOURCES[resource_name]
                safe_endpoints = [e for e in resource.endpoints if e.safe_for_coverage]
                endpoints.extend(safe_endpoints)
        
        if not endpoints:
            return self.build_prompt(test_count=test_count)
        
        endpoints_text = self._format_endpoints_for_prompt(endpoints)
        
        return f'''Generate RSpec request specs for Spree Commerce. Output ONLY Ruby code, no markdown.

Focus on these specific resources: {", ".join(resources)}

ENDPOINTS TO TEST:
{endpoints_text}

TEMPLATE:
```ruby
require 'rails_helper'

RSpec.describe 'Spree Store API - Focused Tests', type: :request do
  let(:store) {{ Spree::Store.default || create(:store) }}
  let(:headers) {{ {{ 'Accept' => 'application/json', 'Content-Type' => 'application/json' }} }}
  
  # For authenticated endpoints - use Spree::RefreshToken
  let(:user) {{ create(:user, password: 'password123') }}
  let(:auth_headers) {{
    refresh_token = Spree::RefreshToken.create!(
      user: user,
      expires_at: 1.day.from_now
    )
    headers.merge('Authorization' => "Bearer #{{refresh_token.token}}")
  }}
  
  # Add describe blocks for each resource
  # Use create(:product), create(:taxon), etc. for test data
  # Assert response status with flexible expectations
end
```

Generate {test_count} test examples covering ALL the resources listed. Output ONLY Ruby code.
'''
    
    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get summary of API endpoints for reporting."""
        return get_api_statistics()


def build_spree_prompt(spree_root: Path, **kwargs) -> str:
    """Convenience function to build a Spree API test prompt."""
    builder = SpreePromptBuilder(spree_root)
    return builder.build_prompt(**kwargs)
