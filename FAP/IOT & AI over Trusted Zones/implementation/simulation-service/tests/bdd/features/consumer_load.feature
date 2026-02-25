Feature: Consumer Load Simulation
  As a load forecasting system
  I want realistic consumer load patterns
  So that I can validate load prediction models

  Scenario: Oven load profile
    Given an electric oven rated at 3.5 kW
    When the oven is activated at 18:00
    Then power should ramp up over 5 minutes
    And maintain steady state for the cooking duration
    And power should decrease gradually when turned off

  Scenario: HVAC load simulation
    Given ambient temperature is 32°C
    And setpoint temperature is 24°C
    When HVAC is operating
    Then compressor should cycle on/off realistically
    And power draw should vary with outdoor temperature

  Scenario: Base load pattern
    When I request the building base load profile
    Then load should include always-on devices
    And load should vary by time of day
    And weekend patterns should differ from weekdays

  Scenario: Aggregated load profile
    Given multiple consumer devices are active
    When I request total load
    Then values should be the sum of individual loads
    And diversity factor should be applied appropriately
