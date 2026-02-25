Feature: Modbus TCP Energy Meter Simulation (Janitza-compatible)
  As a system integrator
  I want a Modbus TCP server emulating Janitza energy meters
  So that I can test industrial energy monitoring integrations

  Background:
    Given the Modbus TCP server is running on port 502
    And the meter is configured as Janitza UMG 96RM

  Scenario: Read active power registers
    When I read Modbus registers 19000-19001 (Active Power L1)
    Then I should receive a valid IEEE 754 float value
    And the value should be within range 0-50000 W

  Scenario: Read voltage registers
    When I read Modbus registers 19020-19021 (Voltage L1-N)
    Then I should receive a value between 220-240 V
    And the value should fluctuate realistically

  Scenario: Read energy counters
    When I read Modbus registers 19062-19063 (Total Active Energy)
    Then I should receive a monotonically increasing value
    And the increment rate should match current power consumption

  Scenario: Modbus exception handling
    When I read an invalid register address 99999
    Then I should receive Modbus exception code 0x02 (Illegal Data Address)

  Scenario: Multiple client connections
    Given 3 Modbus clients are connected simultaneously
    When all clients read the same registers
    Then all clients should receive consistent data
    And no connection should be dropped
