Feature: MS2 End-to-End Data Slice (FAP ↔ ORCE ↔ Kafka)
  As a project team
  We want an end-to-end demonstrator slice using simulated data
  So that we prove the FAP use cases are technically feasible and demo-ready.

  Background:
    Given the simulation runs in "deterministic" mode with a fixed seed
    And the simulation tick interval is 1 minute
    And all timestamps are in ISO 8601 UTC format (e.g., 2026-02-17T10:15:00Z)
    And all messages include "type" and "schema_version"
    And correlation keys are present:
      | key      |
      | site_id  |
      | asset_id |

  # --------------------------
  # Smart Energy — Simulation
  # --------------------------

  Scenario: Smart Energy meter feed is published with a realistic structure
    Given a Smart Energy site "SITE-001"
    And an energy meter "METER-001" assigned to site "SITE-001"
    When the ORCE energy meter simulator runs for 60 minutes
    Then Kafka topic "sim.smart_energy.meter" receives messages every 1 minute
    And each message contains:
      | field                    |
      | site_id                  |
      | meter_id                 |
      | timestamp                |
      | active_power_kw          |
      | active_energy_kwh_total  |
      | schema_version           |
      | type                     |
    And active_energy_kwh_total is monotonic increasing
    And active_power_kw stays within plausible ranges for the scenario

  Scenario: Smart Energy weather feed is published and time-aligned
    Given a Smart Energy site "SITE-001"
    When the ORCE weather simulator runs for 60 minutes
    Then Kafka topic "sim.smart_energy.weather" receives messages every 1 minute
    And each message contains:
      | field                |
      | site_id              |
      | timestamp            |
      | temperature_c        |
      | solar_irradiance_w_m2|
      | schema_version       |
      | type                 |
    And timestamps align with the meter feed timestamps

  Scenario: Smart Energy PV feed is correlated with irradiance
    Given a Smart Energy site "SITE-001"
    And a PV system "PV-001" assigned to site "SITE-001"
    When the ORCE PV simulator runs for 60 minutes
    Then Kafka topic "sim.smart_energy.pv" receives messages every 1 minute
    And each message contains:
      | field           |
      | site_id         |
      | pv_system_id    |
      | timestamp       |
      | schema_version  |
      | type            |
    And pv_power_kw is correlated with solar_irradiance_w_m2 from the weather feed

  Scenario: Smart Energy dynamic price feed is published
    When the ORCE price simulator runs for 60 minutes
    Then Kafka topic "sim.smart_energy.price" receives messages every 1 minute
    And each message contains:
      | field              |
      | timestamp          |
      | price_eur_per_kwh  |
      | tariff_type        |
      | schema_version     |
      | type               |

  Scenario: Smart Energy controllable consumer feed includes state cycles
    Given a Smart Energy site "SITE-001"
    And a device "OVEN-001" assigned to site "SITE-001"
    When the ORCE consumer simulator runs for 24 hours
    Then Kafka topic "sim.smart_energy.consumer" receives messages every 1 minute
    And each message contains:
      | field           |
      | site_id         |
      | device_id       |
      | timestamp       |
      | device_state    |
      | device_power_kw |
      | schema_version  |
      | type            |
    And there are at least 2 ON cycles during the day
    And at least one ON cycle occurs during a high price window

  Scenario: Smart Energy event day contains an anomaly window
    Given the simulation runs in "event_day" mode
    When the ORCE energy meter simulator runs for 180 minutes
    Then there is an anomaly window of 10 to 20 minutes
    And active_power_kw shows a spike or drop during the anomaly window
    And the anomaly is reflected consistently in the derived energy counter behavior

  # --------------------------
  # Smart City — Simulation
  # --------------------------

  Scenario: Smart City lighting feed is published with zone correlation
    Given a city "CITY-001"
    And a zone "ZONE-007" within city "CITY-001"
    And a light "LIGHT-123" assigned to zone "ZONE-007"
    When the ORCE light simulator runs for 60 minutes
    Then Kafka topic "sim.smart_city.light" receives messages every 1 minute
    And each message contains:
      | field              |
      | city_id            |
      | zone_id            |
      | light_id           |
      | timestamp          |
      | dimming_level_pct  |
      | power_w            |
      | schema_version     |
      | type               |

  Scenario: Smart City event feed is published and can trigger explainable changes
    Given a city "CITY-001"
    And a zone "ZONE-007" within city "CITY-001"
    When the ORCE event simulator emits an event for zone "ZONE-007"
    Then Kafka topic "sim.smart_city.event" receives an event message containing:
      | field          |
      | city_id        |
      | zone_id        |
      | timestamp      |
      | event_type     |
      | severity       |
      | schema_version |
      | type           |
    And within 5 minutes the lighting feed for zone "ZONE-007" shows an explainable dimming change

  Scenario: Smart City traffic feed provides context values per zone
    Given a city "CITY-001"
    And a zone "ZONE-007" within city "CITY-001"
    When the ORCE traffic simulator runs for 60 minutes
    Then Kafka topic "sim.smart_city.traffic" receives messages every 1 minute
    And each message contains:
      | field           |
      | city_id         |
      | zone_id         |
      | timestamp       |
      | traffic_index   |
      | schema_version  |
      | type            |

  # --------------------------
  # End-to-End — Kafka Delivery
  # --------------------------

  Scenario: All required topics receive messages with stable cadence
    When the ORCE end-to-end flow runs for 60 minutes
    Then each configured topic receives messages at least every 1 minute
    And a consumer can read messages from each topic without schema errors

  Scenario: Demonstrate one correlation example for Smart Energy (cost impact)
    Given meter, PV, weather, and price messages exist for the same timestamps
    And consumer device cycles exist for the same timestamps
    When a consumer computes cost for the device ON windows
    Then the computed cost differs between a high-price window and a low-price window
    And the difference is explainable based on price and PV availability

  Scenario: Demonstrate one correlation example for Smart City (event → zone → lighting change)
    Given event and lighting messages exist for the same zone_id
    When an event occurs with severity >= 2
    Then lighting dimming_level_pct increases (or schedule changes) for that zone within 5 minutes
    And the change is explainable and repeatable in deterministic mode
