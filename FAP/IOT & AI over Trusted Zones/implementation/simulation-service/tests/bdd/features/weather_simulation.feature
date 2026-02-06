Feature: Weather Data Simulation
  As a data consumer
  I want correlated weather data
  So that I can validate weather-dependent energy models

  Scenario: Temperature simulation
    Given the simulated date is "2026-07-15"
    When I request hourly temperature data
    Then temperatures should follow a realistic diurnal pattern
    And minimum temperature should occur around 05:00-06:00
    And maximum temperature should occur around 14:00-16:00

  Scenario: Solar irradiance correlation
    Given clear sky conditions
    When I request GHI (Global Horizontal Irradiance)
    Then irradiance should correlate with PV generation
    And peak GHI should be approximately 1000 W/m² at solar noon

  Scenario: Wind speed simulation
    When I request wind speed data
    Then values should follow a Weibull distribution
    And gusts should be realistically correlated with mean wind speed

  Scenario: Weather event injection
    Given normal weather conditions
    When I inject a storm event at 14:00
    Then wind speed should increase dramatically
    And cloud cover should increase to 100%
    And solar irradiance should drop significantly
