"""
Configuration management for FACIS Simulation Service.

Loads configuration from YAML files and environment variables.

Priority (highest to lowest):
1. Environment variables (SIMULATOR_ prefix, nested with __)
2. YAML config file
3. Default values
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

logger = logging.getLogger(__name__)


# =============================================================================
# Simulation Configuration
# =============================================================================


class SimulationConfig(BaseModel):
    """Core simulation engine configuration."""

    seed: int = Field(
        default=12345,
        ge=0,
        description="Random seed for reproducibility",
    )
    interval_minutes: int = Field(
        default=1,
        ge=1,
        le=60,
        description="Simulation interval in minutes",
    )
    start_time: str | None = Field(
        default=None,
        description="Simulation start time (ISO 8601 format). If null, uses current time",
    )
    speed_factor: float = Field(
        default=1.0,
        ge=0.1,
        le=1000.0,
        description="Simulation speed factor (1.0 = real-time, 10.0 = 10x faster)",
    )

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, v: str | None) -> str | None:
        """Validate start_time is a valid ISO 8601 datetime string."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError as e:
                raise ValueError(
                    f"Invalid start_time format: '{v}'. Must be ISO 8601 format "
                    f"(e.g., '2024-01-15T08:00:00Z' or '2024-01-15T08:00:00+00:00')"
                ) from e
        return v


# =============================================================================
# Meter Configuration
# =============================================================================


class MeterConfig(BaseModel):
    """Configuration for an individual energy meter."""

    id: str = Field(..., min_length=1, description="Unique meter identifier")
    base_load_kw: float = Field(
        default=10.0,
        ge=0.0,
        description="Base load power in kW (minimum continuous load)",
    )
    peak_load_kw: float = Field(
        default=25.0,
        ge=0.0,
        description="Peak load power in kW (maximum expected load)",
    )
    nominal_voltage_v: float = Field(
        default=230.0,
        ge=100.0,
        le=500.0,
        description="Nominal voltage in volts",
    )
    voltage_variance_pct: float = Field(
        default=5.0,
        ge=0.0,
        le=15.0,
        description="Voltage variance percentage",
    )
    nominal_frequency_hz: float = Field(
        default=50.0,
        ge=45.0,
        le=65.0,
        description="Nominal grid frequency in Hz",
    )
    frequency_variance_hz: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Frequency variance in Hz",
    )
    power_factor_min: float = Field(
        default=0.95,
        ge=0.5,
        le=1.0,
        description="Minimum power factor",
    )
    power_factor_max: float = Field(
        default=0.99,
        ge=0.5,
        le=1.0,
        description="Maximum power factor",
    )
    initial_energy_kwh: float = Field(
        default=0.0,
        ge=0.0,
        description="Initial cumulative energy reading in kWh",
    )

    @model_validator(mode="after")
    def validate_load_range(self) -> "MeterConfig":
        """Ensure base_load_kw <= peak_load_kw."""
        if self.base_load_kw > self.peak_load_kw:
            raise ValueError(
                f"base_load_kw ({self.base_load_kw}) cannot be greater than "
                f"peak_load_kw ({self.peak_load_kw}) for meter '{self.id}'"
            )
        return self

    @model_validator(mode="after")
    def validate_power_factor_range(self) -> "MeterConfig":
        """Ensure power_factor_min <= power_factor_max."""
        if self.power_factor_min > self.power_factor_max:
            raise ValueError(
                f"power_factor_min ({self.power_factor_min}) cannot be greater than "
                f"power_factor_max ({self.power_factor_max}) for meter '{self.id}'"
            )
        return self


# =============================================================================
# PV System Configuration
# =============================================================================


class PVSystemConfig(BaseModel):
    """Configuration for an individual PV (photovoltaic) system."""

    id: str = Field(..., min_length=1, description="Unique PV system identifier")
    nominal_capacity_kw: float = Field(
        default=10.0,
        ge=0.1,
        le=10000.0,
        description="Nominal capacity in kW peak (kWp)",
    )
    losses: float = Field(
        default=0.15,
        ge=0.0,
        le=0.5,
        description="System losses as a fraction (0.15 = 15% losses)",
    )
    temperature_coefficient: float = Field(
        default=-0.004,
        le=0.0,
        description="Power temperature coefficient per °C (typically -0.003 to -0.005)",
    )
    reference_temperature_c: float = Field(
        default=25.0,
        ge=0.0,
        le=50.0,
        description="Reference temperature for rated output (STC = 25°C)",
    )
    azimuth_deg: float = Field(
        default=180.0,
        ge=0.0,
        le=360.0,
        description="Panel azimuth in degrees (180 = south facing)",
    )
    tilt_deg: float = Field(
        default=35.0,
        ge=0.0,
        le=90.0,
        description="Panel tilt angle in degrees from horizontal",
    )
    latitude: float = Field(
        default=52.52,
        ge=-90.0,
        le=90.0,
        description="Installation latitude",
    )
    longitude: float = Field(
        default=13.405,
        ge=-180.0,
        le=180.0,
        description="Installation longitude",
    )

    @field_validator("losses")
    @classmethod
    def validate_losses(cls, v: float) -> float:
        """Warn if losses seem unrealistic."""
        if v > 0.3:
            logger.warning(
                f"PV system losses of {v * 100:.1f}% seem high. Typical values are 10-20%."
            )
        return v


# =============================================================================
# Consumer Configuration
# =============================================================================


class OperatingWindow(BaseModel):
    """Defines an operating time window for a consumer device."""

    start_hour: int = Field(..., ge=0, le=23, description="Start hour (0-23)")
    end_hour: int = Field(..., ge=0, le=23, description="End hour (0-23)")


class ConsumerConfig(BaseModel):
    """Configuration for an individual consumer device."""

    id: str = Field(..., min_length=1, description="Unique consumer device identifier")
    rated_power_kw: float = Field(
        default=3.0,
        ge=0.0,
        le=1000.0,
        description="Rated power consumption in kW",
    )
    duty_cycle: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Duty cycle as a fraction (0.7 = 70% on time during operating windows)",
    )
    device_type: str = Field(
        default="generic",
        description="Device type (industrial_oven, hvac, compressor, pump, generic)",
    )
    power_variance_pct: float = Field(
        default=5.0,
        ge=0.0,
        le=30.0,
        description="Power variance percentage when device is ON",
    )
    operating_windows: list[OperatingWindow] = Field(
        default_factory=lambda: [
            OperatingWindow(start_hour=7, end_hour=9),
            OperatingWindow(start_hour=11, end_hour=13),
            OperatingWindow(start_hour=15, end_hour=17),
        ],
        description="Operating time windows",
    )
    operate_on_weekends: bool = Field(
        default=False,
        description="Whether device operates on weekends",
    )

    @field_validator("device_type")
    @classmethod
    def validate_device_type(cls, v: str) -> str:
        """Validate device type is recognized."""
        valid_types = {"industrial_oven", "hvac", "compressor", "pump", "generic"}
        if v.lower() not in valid_types:
            raise ValueError(
                f"Invalid device_type '{v}'. Must be one of: {', '.join(sorted(valid_types))}"
            )
        return v.lower()


# =============================================================================
# MQTT Configuration
# =============================================================================


class MqttConfig(BaseModel):
    """MQTT broker configuration."""

    host: str = Field(
        default="localhost",
        min_length=1,
        description="MQTT broker hostname or IP address",
    )
    port: int = Field(
        default=1883,
        ge=1,
        le=65535,
        description="MQTT broker port",
    )
    client_id: str = Field(
        default="facis-simulator",
        min_length=1,
        description="MQTT client identifier",
    )
    qos: int = Field(
        default=1,
        ge=0,
        le=2,
        description="MQTT Quality of Service level (0, 1, or 2)",
    )
    username: str | None = Field(
        default=None,
        description="MQTT username (optional)",
    )
    password: str | None = Field(
        default=None,
        description="MQTT password (optional)",
    )


# =============================================================================
# HTTP Configuration
# =============================================================================


class HttpConfig(BaseModel):
    """HTTP/REST API configuration."""

    host: str = Field(
        default="0.0.0.0",
        min_length=1,
        description="HTTP server bind address",
    )
    port: int = Field(
        default=8080,
        ge=1,
        le=65535,
        description="HTTP server port",
    )


# =============================================================================
# Modbus Configuration
# =============================================================================


class ModbusConfig(BaseModel):
    """Modbus TCP server configuration."""

    host: str = Field(
        default="0.0.0.0",
        min_length=1,
        description="Modbus TCP server bind address",
    )
    port: int = Field(
        default=502,
        ge=1,
        le=65535,
        description="Modbus TCP server port",
    )


# =============================================================================
# Logging Configuration
# =============================================================================


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )

    @field_validator("level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is recognized."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(
                f"Invalid log level '{v}'. Must be one of: {', '.join(sorted(valid_levels))}"
            )
        return v.upper()


# =============================================================================
# YAML Settings Source
# =============================================================================


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """Custom settings source that loads from YAML files."""

    _yaml_data: ClassVar[dict[str, Any]] = {}

    @classmethod
    def set_yaml_data(cls, data: dict[str, Any]) -> None:
        """Set the YAML data to be used as a settings source."""
        cls._yaml_data = data

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        """Get the value for a field from YAML data."""
        field_value = self._yaml_data.get(field_name)
        return field_value, field_name, False

    def __call__(self) -> dict[str, Any]:
        """Return all YAML data."""
        return self._yaml_data


# =============================================================================
# Main Settings Class
# =============================================================================


class Settings(BaseSettings):
    """
    Main settings container for FACIS Simulation Service.

    Configuration sources (highest to lowest priority):
    1. Environment variables with SIMULATOR_ prefix
    2. YAML config file
    3. Default values defined in this class

    Environment variable examples:
        SIMULATOR_SIMULATION__SEED=42
        SIMULATOR_SIMULATION__SPEED_FACTOR=10.0
        SIMULATOR_MQTT__HOST=broker.example.com
        SIMULATOR_MQTT__PORT=1883
        SIMULATOR_HTTP__PORT=8000
    """

    model_config = SettingsConfigDict(
        env_prefix="SIMULATOR_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    meters: list[MeterConfig] = Field(
        default_factory=lambda: [MeterConfig(id="meter-001", base_load_kw=10.0, peak_load_kw=25.0)],
        description="List of energy meter configurations",
    )
    pv_systems: list[PVSystemConfig] = Field(
        default_factory=lambda: [PVSystemConfig(id="pv-system-001", nominal_capacity_kw=10.0)],
        description="List of PV system configurations",
    )
    consumers: list[ConsumerConfig] = Field(
        default_factory=lambda: [
            ConsumerConfig(id="oven-001", rated_power_kw=3.5, device_type="industrial_oven"),
            ConsumerConfig(id="hvac-001", rated_power_kw=2.0, device_type="hvac"),
        ],
        description="List of consumer device configurations",
    )
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    http: HttpConfig = Field(default_factory=HttpConfig)
    modbus: ModbusConfig = Field(default_factory=ModbusConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize the settings sources priority.

        Priority (highest to lowest):
        1. Init settings (passed to constructor)
        2. Environment variables
        3. YAML config file
        4. Default values
        """
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls),
        )

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "Settings":
        """Ensure all entity IDs are unique within their category."""
        meter_ids = [m.id for m in self.meters]
        if len(meter_ids) != len(set(meter_ids)):
            duplicates = [id for id in meter_ids if meter_ids.count(id) > 1]
            raise ValueError(f"Duplicate meter IDs found: {set(duplicates)}")

        pv_ids = [p.id for p in self.pv_systems]
        if len(pv_ids) != len(set(pv_ids)):
            duplicates = [id for id in pv_ids if pv_ids.count(id) > 1]
            raise ValueError(f"Duplicate PV system IDs found: {set(duplicates)}")

        consumer_ids = [c.id for c in self.consumers]
        if len(consumer_ids) != len(set(consumer_ids)):
            duplicates = [id for id in consumer_ids if consumer_ids.count(id) > 1]
            raise ValueError(f"Duplicate consumer IDs found: {set(duplicates)}")

        return self


# =============================================================================
# Configuration Loading Functions
# =============================================================================


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge two dictionaries.

    Values from 'override' take precedence over 'base'.
    Nested dictionaries are merged recursively.
    Lists are replaced entirely (not merged).
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_yaml_config(config_path: Path) -> dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dictionary containing the configuration values.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If the YAML is invalid.
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Please create a config file or set SIMULATOR_* environment variables."
        )

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            if config is None:
                return {}
            if not isinstance(config, dict):
                raise ValueError(
                    f"Invalid configuration file: {config_path}\n"
                    f"Expected a YAML dictionary at the root level."
                )
            return config
    except yaml.YAMLError as e:
        raise yaml.YAMLError(
            f"Invalid YAML in configuration file: {config_path}\nError: {e}"
        ) from e


def load_config(
    config_path: Path | str | None = None,
    env: str | None = None,
) -> Settings:
    """
    Load configuration from YAML files and environment variables.

    Priority (highest to lowest):
    1. Environment variables (SIMULATOR_ prefix)
    2. Environment-specific YAML (e.g., development.yaml)
    3. default.yaml
    4. Pydantic default values

    Args:
        config_path: Path to the config directory. If None, uses ./config relative
                    to the project root.
        env: Environment name (development, production, test). If None, reads
            from FACIS_ENV environment variable, defaulting to 'development'.

    Returns:
        Validated Settings object.

    Raises:
        ValidationError: If configuration values fail validation.
    """
    settings_dict: dict[str, Any] = {}

    # Determine config directory
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config"
    elif isinstance(config_path, str):
        config_path = Path(config_path)

    # Load default.yaml if exists
    default_file = config_path / "default.yaml"
    if default_file.exists():
        try:
            settings_dict = load_yaml_config(default_file)
            logger.debug(f"Loaded default configuration from {default_file}")
        except Exception as e:
            logger.warning(f"Failed to load default.yaml: {e}")

    # Load environment-specific config
    env = env or os.getenv("FACIS_ENV", "development")
    env_file = config_path / f"{env}.yaml"
    if env_file.exists():
        try:
            env_config = load_yaml_config(env_file)
            settings_dict = deep_merge(settings_dict, env_config)
            logger.debug(f"Loaded {env} configuration from {env_file}")
        except Exception as e:
            logger.warning(f"Failed to load {env}.yaml: {e}")

    # Set YAML data for the custom settings source
    YamlConfigSettingsSource.set_yaml_data(settings_dict)

    # Create Settings - pydantic-settings will apply env var overrides automatically
    try:
        settings = Settings()
    except Exception as e:
        # Re-raise with more context
        raise type(e)(
            f"Configuration validation failed:\n{e}\n\n"
            f"Check your configuration file at {config_path} "
            f"and SIMULATOR_* environment variables."
        ) from e

    return settings


def log_config(settings: Settings) -> None:
    """
    Log the current configuration values.

    Sensitive values (passwords) are masked.
    """
    logger.info("=" * 60)
    logger.info("FACIS Simulation Service Configuration")
    logger.info("=" * 60)

    # Simulation settings
    logger.info("Simulation:")
    logger.info(f"  seed: {settings.simulation.seed}")
    logger.info(f"  interval_minutes: {settings.simulation.interval_minutes}")
    logger.info(f"  start_time: {settings.simulation.start_time or '(current time)'}")
    logger.info(f"  speed_factor: {settings.simulation.speed_factor}x")

    # Meters
    logger.info(f"Meters ({len(settings.meters)} configured):")
    for meter in settings.meters:
        logger.info(
            f"  - {meter.id}: {meter.base_load_kw}-{meter.peak_load_kw} kW, "
            f"{meter.nominal_voltage_v}V, {meter.nominal_frequency_hz}Hz"
        )

    # PV Systems
    logger.info(f"PV Systems ({len(settings.pv_systems)} configured):")
    for pv in settings.pv_systems:
        logger.info(
            f"  - {pv.id}: {pv.nominal_capacity_kw} kWp, "
            f"losses={pv.losses * 100:.1f}%, "
            f"lat={pv.latitude}, lon={pv.longitude}"
        )

    # Consumers
    logger.info(f"Consumers ({len(settings.consumers)} configured):")
    for consumer in settings.consumers:
        logger.info(
            f"  - {consumer.id}: {consumer.rated_power_kw} kW, "
            f"type={consumer.device_type}, "
            f"duty_cycle={consumer.duty_cycle * 100:.0f}%"
        )

    # MQTT
    logger.info("MQTT:")
    logger.info(f"  host: {settings.mqtt.host}")
    logger.info(f"  port: {settings.mqtt.port}")
    logger.info(f"  client_id: {settings.mqtt.client_id}")
    logger.info(f"  qos: {settings.mqtt.qos}")
    if settings.mqtt.username:
        logger.info(f"  username: {settings.mqtt.username}")
        logger.info("  password: ****")

    # HTTP
    logger.info("HTTP:")
    logger.info(f"  host: {settings.http.host}")
    logger.info(f"  port: {settings.http.port}")

    # Modbus
    logger.info("Modbus:")
    logger.info(f"  host: {settings.modbus.host}")
    logger.info(f"  port: {settings.modbus.port}")

    # Logging
    logger.info("Logging:")
    logger.info(f"  level: {settings.logging.level}")

    logger.info("=" * 60)
