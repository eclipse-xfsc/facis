Feature: PV Generation Simulation
  As an energy analyst
  I want realistic photovoltaic generation data
  So that I can test energy balancing algorithms

  Background:
    Given a PV system with capacity 10 kWp
    And location coordinates 52.52°N, 13.405°E (Berlin)
    And panel orientation azimuth 180° and tilt 35°

  Scenario: Daily generation curve
    Given the simulated date is "2026-06-21" (summer solstice)
    When I request the daily generation profile
    Then generation should start around 05:00
    And peak generation should occur around 12:00-13:00
    And generation should end around 21:00
    And total daily generation should be approximately 50-60 kWh

  Scenario: Cloud cover impact
    Given clear sky conditions
    When a cloud event occurs at 12:00
    Then generation should drop by 40-80% within 2 minutes
    And generation should recover when cloud passes

  Scenario: Winter generation profile
    Given the simulated date is "2026-12-21" (winter solstice)
    When I request the daily generation profile
    Then peak generation should be 20-30% of summer peak
    And daylight hours should be significantly reduced

  Scenario: Temperature derating
    Given ambient temperature is 35°C
    When calculating generation
    Then output should be derated by approximately 4% per °C above 25°C
