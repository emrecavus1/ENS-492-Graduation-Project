# frozen_string_literal: true
require_relative '../test_helper'

class GeneratedSmokeTest < ActiveSupport::TestCase
  test "smoke: app boots" do
    assert defined?(Redmine)
  end
end
