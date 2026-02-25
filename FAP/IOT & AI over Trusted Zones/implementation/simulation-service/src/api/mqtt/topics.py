"""
MQTT topic definitions.

Defines topic structure and QoS levels for all simulation feeds.

Topic Structure:
    facis/energy/meter/{id}     - Energy meter readings (QoS 1)
    facis/energy/pv/{id}        - PV generation data (QoS 1)
    facis/weather/current       - Weather conditions (QoS 0)
    facis/prices/spot           - Spot prices (QoS 1)
    facis/prices/forecast       - Price forecasts (QoS 1)
    facis/loads/{type}          - Consumer load data (QoS 0)
    facis/events/alerts         - System alerts (QoS 2)
    facis/simulation/status     - Simulation state (QoS 1)
"""

from dataclasses import dataclass
from enum import IntEnum


class QoS(IntEnum):
    """MQTT Quality of Service levels."""

    AT_MOST_ONCE = 0  # Fire and forget
    AT_LEAST_ONCE = 1  # Guaranteed delivery (may duplicate)
    EXACTLY_ONCE = 2  # Guaranteed exactly once


@dataclass(frozen=True)
class TopicConfig:
    """Configuration for an MQTT topic."""

    pattern: str
    qos: QoS
    retained: bool = False
    description: str = ""


class MQTTTopics:
    """MQTT topic definitions for FACIS simulation service."""

    # Base topic prefix
    PREFIX = "facis"

    # Energy meter readings
    METER = TopicConfig(
        pattern=f"{PREFIX}/energy/meter/{{meter_id}}",
        qos=QoS.AT_LEAST_ONCE,
        retained=False,
        description="Energy meter readings (3-phase power, voltage, current)",
    )

    # PV generation data
    PV = TopicConfig(
        pattern=f"{PREFIX}/energy/pv/{{system_id}}",
        qos=QoS.AT_LEAST_ONCE,
        retained=False,
        description="PV generation data (power output, efficiency)",
    )

    # Weather conditions (retained for late subscribers)
    WEATHER = TopicConfig(
        pattern=f"{PREFIX}/weather/current",
        qos=QoS.AT_MOST_ONCE,
        retained=True,
        description="Current weather conditions (temperature, irradiance, wind)",
    )

    # Spot prices (retained for late subscribers)
    PRICE_SPOT = TopicConfig(
        pattern=f"{PREFIX}/prices/spot",
        qos=QoS.AT_LEAST_ONCE,
        retained=True,
        description="Current spot electricity price",
    )

    # Price forecast
    PRICE_FORECAST = TopicConfig(
        pattern=f"{PREFIX}/prices/forecast",
        qos=QoS.AT_LEAST_ONCE,
        retained=True,
        description="Electricity price forecast (next 24 hours)",
    )

    # Consumer load data
    LOAD = TopicConfig(
        pattern=f"{PREFIX}/loads/{{device_type}}",
        qos=QoS.AT_MOST_ONCE,
        retained=False,
        description="Consumer device load data",
    )

    # System alerts (QoS 2 for critical messages)
    ALERTS = TopicConfig(
        pattern=f"{PREFIX}/events/alerts",
        qos=QoS.EXACTLY_ONCE,
        retained=False,
        description="System alerts and critical events",
    )

    # Simulation status
    SIMULATION_STATUS = TopicConfig(
        pattern=f"{PREFIX}/simulation/status",
        qos=QoS.AT_LEAST_ONCE,
        retained=True,
        description="Simulation engine state and time",
    )

    @classmethod
    def meter_topic(cls, meter_id: str) -> str:
        """Get the topic for a specific meter."""
        return cls.METER.pattern.format(meter_id=meter_id)

    @classmethod
    def pv_topic(cls, system_id: str) -> str:
        """Get the topic for a specific PV system."""
        return cls.PV.pattern.format(system_id=system_id)

    @classmethod
    def load_topic(cls, device_type: str) -> str:
        """Get the topic for a specific device type."""
        return cls.LOAD.pattern.format(device_type=device_type)

    @classmethod
    def weather_topic(cls) -> str:
        """Get the weather topic."""
        return cls.WEATHER.pattern

    @classmethod
    def spot_price_topic(cls) -> str:
        """Get the spot price topic."""
        return cls.PRICE_SPOT.pattern

    @classmethod
    def forecast_price_topic(cls) -> str:
        """Get the price forecast topic."""
        return cls.PRICE_FORECAST.pattern

    @classmethod
    def alerts_topic(cls) -> str:
        """Get the alerts topic."""
        return cls.ALERTS.pattern

    @classmethod
    def simulation_status_topic(cls) -> str:
        """Get the simulation status topic."""
        return cls.SIMULATION_STATUS.pattern
