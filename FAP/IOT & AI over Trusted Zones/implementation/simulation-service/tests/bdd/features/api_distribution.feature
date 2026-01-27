Feature: API Data Distribution
  As a downstream system
  I want to consume simulation data via standard protocols
  So that I can integrate without protocol-specific dependencies

  Scenario: MQTT data publishing
    Given the MQTT broker is running
    When the simulation generates new data
    Then data should be published to topic "facis/energy/meter/1"
    And message payload should be valid JSON
    And QoS level should be configurable

  Scenario: REST API polling
    Given the HTTP API is running on port 8080
    When I GET /api/v1/meter/1/current
    Then I should receive current meter readings as JSON
    And response should include timestamp
    And response latency should be under 100ms

  Scenario: Bulk historical data export
    When I GET /api/v1/meter/1/history?from=2026-01-01&to=2026-01-02
    Then I should receive all readings for that period
    And data should be in time-sorted order
    And pagination should be supported for large datasets

  Scenario: WebSocket streaming
    Given a WebSocket connection to /ws/stream
    When I subscribe to "meter.1.power"
    Then I should receive real-time updates
    And connection should handle reconnection gracefully
