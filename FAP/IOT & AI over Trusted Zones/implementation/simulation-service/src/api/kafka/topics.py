"""
Kafka topic definitions.

Defines topic names for all simulation feeds.

Topic Structure:
    sim.smart_energy.meter      - Energy meter readings
    sim.smart_energy.pv         - PV generation data
    sim.smart_energy.weather    - Weather conditions
    sim.smart_energy.price      - Energy prices
    sim.smart_energy.consumer   - Consumer load data
    sim.smart_city.light        - Streetlight telemetry
    sim.smart_city.traffic      - Traffic/movement data
    sim.smart_city.event        - City events
    sim.smart_city.weather      - City weather/visibility
"""


class KafkaTopics:
    """Kafka topic definitions for FACIS simulation service."""

    # Smart Energy topics
    METER = "sim.smart_energy.meter"
    PV = "sim.smart_energy.pv"
    WEATHER = "sim.smart_energy.weather"
    PRICE = "sim.smart_energy.price"
    CONSUMER = "sim.smart_energy.consumer"

    # Smart City topics
    LIGHT = "sim.smart_city.light"
    TRAFFIC = "sim.smart_city.traffic"
    EVENT = "sim.smart_city.event"
    CITY_WEATHER = "sim.smart_city.weather"

    # All topics for auto-creation / validation
    ALL_TOPICS = [
        METER,
        PV,
        WEATHER,
        PRICE,
        CONSUMER,
        LIGHT,
        TRAFFIC,
        EVENT,
        CITY_WEATHER,
    ]
