Feature: Core Simulation Engine
  As an integration engineer
  I want a deterministic simulation engine
  So that I can reproduce test scenarios reliably

  Background:
    Given the simulation service is configured with seed value "12345"
    And the simulation time range is "2026-01-01T00:00:00Z" to "2026-01-02T00:00:00Z"

  Scenario: Deterministic data generation
    When I run the simulation with the same seed
    Then the generated time-series data should be identical across runs
    And the event sequence should be reproducible

  Scenario: Configurable time acceleration
    Given the time acceleration factor is set to 60
    When I start the simulation
    Then 1 second of real time should produce 1 minute of simulated data

  Scenario: Simulation pause and resume
    Given the simulation is running
    When I pause the simulation
    Then no new data should be generated
    When I resume the simulation
    Then data generation should continue from the paused state

  Scenario: Historical replay mode
    Given historical data exists for "2025-12-15"
    When I request replay mode for that date
    Then the simulation should replay the exact historical pattern
