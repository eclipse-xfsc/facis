"""
Configuration management for FACIS Simulation Service.

Loads configuration from YAML files and environment variables.
"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class SimulationConfig(BaseModel):
    """Simulation engine configuration."""
    seed: int = Field(default=12345, description="Random seed for reproducibility")
    time_acceleration: int = Field(default=1, ge=1, le=1000, description="Time acceleration factor")
    start_time: Optional[str] = Field(default=None, description="Simulation start time (ISO format)")
    end_time: Optional[str] = Field(default=None, description="Simulation end time (ISO format)")


class HttpConfig(BaseModel):
    """HTTP API configuration."""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080)


class MqttConfig(BaseModel):
    """MQTT configuration."""
    broker: str = Field(default="localhost")
    port: int = Field(default=1883)
    qos: int = Field(default=1, ge=0, le=2)


class ModbusConfig(BaseModel):
    """Modbus TCP configuration."""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=502)


class ApiConfig(BaseModel):
    """API layer configuration."""
    http: HttpConfig = Field(default_factory=HttpConfig)
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    modbus: ModbusConfig = Field(default_factory=ModbusConfig)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class Settings(BaseModel):
    """Main settings container."""
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_path: Optional[Path] = None, env: Optional[str] = None) -> Settings:
    """
    Load configuration from YAML files and environment variables.
    
    Priority (highest to lowest):
    1. Environment variables
    2. Environment-specific YAML (e.g., development.yaml)
    3. default.yaml
    """
    # Determine config directory
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config"
    
    settings_dict: dict = {}
    
    # Load default.yaml if exists
    default_file = config_path / "default.yaml"
    if default_file.exists():
        with open(default_file) as f:
            settings_dict = yaml.safe_load(f) or {}
    
    # Load environment-specific config
    env = env or os.getenv("FACIS_ENV", "development")
    env_file = config_path / f"{env}.yaml"
    if env_file.exists():
        with open(env_file) as f:
            env_config = yaml.safe_load(f) or {}
            settings_dict = deep_merge(settings_dict, env_config)
    
    # Override with environment variables
    if seed := os.getenv("SIMULATION_SEED"):
        settings_dict.setdefault("simulation", {})["seed"] = int(seed)
    
    if accel := os.getenv("TIME_ACCELERATION"):
        settings_dict.setdefault("simulation", {})["time_acceleration"] = int(accel)
    
    if port := os.getenv("HTTP_PORT"):
        settings_dict.setdefault("api", {}).setdefault("http", {})["port"] = int(port)
    
    if broker := os.getenv("MQTT_BROKER"):
        settings_dict.setdefault("api", {}).setdefault("mqtt", {})["broker"] = broker
    
    if modbus_port := os.getenv("MODBUS_PORT"):
        settings_dict.setdefault("api", {}).setdefault("modbus", {})["port"] = int(modbus_port)
    
    if log_level := os.getenv("LOG_LEVEL"):
        settings_dict.setdefault("logging", {})["level"] = log_level
    
    return Settings(**settings_dict)


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
