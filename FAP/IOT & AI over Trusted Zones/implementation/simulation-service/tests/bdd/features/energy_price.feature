Feature: Energy Price Simulation
  As an optimization system
  I want realistic energy price feeds
  So that I can test demand response algorithms

  Background:
    Given the price model is "EPEX Spot Day-Ahead"
    And the base price is 0.08 EUR/kWh

  Scenario: Daily price pattern
    When I request 24-hour price forecast
    Then prices should show morning peak (07:00-09:00)
    And prices should show evening peak (17:00-20:00)
    And prices should show overnight low (01:00-05:00)

  Scenario: Price spike events
    Given normal market conditions
    When I inject a price spike event
    Then price should increase by 200-500% for 1-2 hours
    And downstream systems should receive price alerts

  Scenario: Negative price scenario
    Given high renewable generation conditions
    When I enable negative price simulation
    Then prices should occasionally go negative during midday
    And this should trigger appropriate system responses
