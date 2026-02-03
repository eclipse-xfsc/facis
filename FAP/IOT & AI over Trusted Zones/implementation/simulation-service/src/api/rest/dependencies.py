"""
FastAPI dependencies for dependency injection.

Provides shared instances of simulation engine and configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.config import Settings, load_config
from src.core import SimulationEngine
from src.models.consumer_load import ConsumerLoadConfig, DeviceType
from src.models.meter import MeterConfig
from src.models.price import PriceConfig
from src.models.pv import PVConfig
from src.models.weather import WeatherConfig
from src.simulators.consumer_load import ConsumerLoadSimulator
from src.simulators.energy_meter import EnergyMeterSimulator
from src.simulators.energy_price import EnergyPriceSimulator
from src.simulators.pv_generation import PVGenerationSimulator
from src.simulators.weather import WeatherSimulator

if TYPE_CHECKING:
    pass


class SimulationState:
    """
    Singleton state container for the simulation service.

    Holds the simulation engine and all registered simulators.
    """

    _instance: SimulationState | None = None

    def __init__(self) -> None:
        """Initialize simulation state."""
        self._settings: Settings | None = None
        self._engine: SimulationEngine | None = None
        self._meters: dict[str, EnergyMeterSimulator] = {}
        self._price_feeds: dict[str, EnergyPriceSimulator] = {}
        self._loads: dict[str, ConsumerLoadSimulator] = {}
        self._weather_stations: dict[str, WeatherSimulator] = {}
        self._pv_systems: dict[str, PVGenerationSimulator] = {}
        self._initialized = False

    @classmethod
    def get_instance(cls) -> SimulationState:
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None

    def initialize(self, settings: Settings | None = None) -> None:
        """
        Initialize the simulation state with configuration.

        Args:
            settings: Configuration settings. Loads from files if None.
        """
        if self._initialized:
            return

        self._settings = settings or load_config()
        self._engine = SimulationEngine(self._settings)

        # Register generator types
        self._engine.register_generator_type("energy_meter", EnergyMeterSimulator)
        self._engine.register_generator_type("energy_price", EnergyPriceSimulator)
        self._engine.register_generator_type("consumer_load", ConsumerLoadSimulator)
        self._engine.register_generator_type("weather", WeatherSimulator)
        self._engine.register_generator_type("pv_generation", PVGenerationSimulator)

        # Create default entities from config
        self._setup_default_entities()

        self._initialized = True

    def _setup_default_entities(self) -> None:
        """Set up default meters, price feeds, and loads from configuration."""
        # Create a default meter
        meter_config = MeterConfig(
            meter_id="janitza-umg96rm-001",
            base_power_kw=10.0,
            peak_power_kw=25.0,
        )
        self.add_meter("janitza-umg96rm-001", meter_config)

        # Create a default price feed
        price_config = PriceConfig(feed_id="epex-spot-de")
        self.add_price_feed("epex-spot-de", price_config)

        # Create a default industrial oven
        oven_config = ConsumerLoadConfig(
            device_id="industrial-oven-001",
            device_type=DeviceType.INDUSTRIAL_OVEN,
            rated_power_kw=3.0,
            duty_cycle_pct=70.0,
            operate_on_weekends=False,
        )
        self.add_load("industrial-oven-001", oven_config)

        # Create a default weather station (Berlin)
        weather_config = WeatherConfig(
            latitude=52.52,
            longitude=13.405,
        )
        self.add_weather_station("berlin-001", weather_config)

        # Create a default PV system (linked to Berlin weather station)
        pv_config = PVConfig(
            system_id="pv-system-001",
            weather_station_id="berlin-001",
            nominal_capacity_kwp=10.0,
            system_losses_percent=15.0,
            temperature_coefficient_pct_per_c=-0.4,
        )
        self.add_pv_system("pv-system-001", pv_config)

    @property
    def settings(self) -> Settings:
        """Get current settings."""
        if self._settings is None:
            self.initialize()
        return self._settings  # type: ignore

    @property
    def engine(self) -> SimulationEngine:
        """Get the simulation engine."""
        if self._engine is None:
            self.initialize()
        return self._engine  # type: ignore

    def add_meter(self, meter_id: str, config: MeterConfig | None = None) -> EnergyMeterSimulator:
        """Add a meter simulator."""
        if config is None:
            config = MeterConfig(meter_id=meter_id)

        simulator = EnergyMeterSimulator(
            entity_id=meter_id,
            rng=self.engine.rng,
            config=config,
        )
        self._meters[meter_id] = simulator
        return simulator

    def get_meter(self, meter_id: str) -> EnergyMeterSimulator | None:
        """Get a meter simulator by ID."""
        return self._meters.get(meter_id)

    def list_meters(self) -> list[str]:
        """List all meter IDs."""
        return list(self._meters.keys())

    def add_price_feed(
        self, feed_id: str, config: PriceConfig | None = None
    ) -> EnergyPriceSimulator:
        """Add a price feed simulator."""
        if config is None:
            config = PriceConfig(feed_id=feed_id)

        simulator = EnergyPriceSimulator(
            entity_id=feed_id,
            rng=self.engine.rng,
            config=config,
        )
        self._price_feeds[feed_id] = simulator
        return simulator

    def get_price_feed(self, feed_id: str) -> EnergyPriceSimulator | None:
        """Get a price feed simulator by ID."""
        return self._price_feeds.get(feed_id)

    def get_default_price_feed(self) -> EnergyPriceSimulator | None:
        """Get the default price feed."""
        return self._price_feeds.get("epex-spot-de")

    def add_load(
        self, device_id: str, config: ConsumerLoadConfig | None = None
    ) -> ConsumerLoadSimulator:
        """Add a consumer load simulator."""
        if config is None:
            config = ConsumerLoadConfig(device_id=device_id)

        simulator = ConsumerLoadSimulator(
            entity_id=device_id,
            rng=self.engine.rng,
            config=config,
        )
        self._loads[device_id] = simulator
        return simulator

    def get_load(self, device_id: str) -> ConsumerLoadSimulator | None:
        """Get a consumer load simulator by ID."""
        return self._loads.get(device_id)

    def list_loads(self) -> list[str]:
        """List all consumer load device IDs."""
        return list(self._loads.keys())

    def add_weather_station(
        self, station_id: str, config: WeatherConfig | None = None
    ) -> WeatherSimulator:
        """Add a weather station simulator."""
        if config is None:
            config = WeatherConfig()

        simulator = WeatherSimulator(
            entity_id=station_id,
            rng=self.engine.rng,
            config=config,
        )
        self._weather_stations[station_id] = simulator
        return simulator

    def get_weather_station(self, station_id: str) -> WeatherSimulator | None:
        """Get a weather station simulator by ID."""
        return self._weather_stations.get(station_id)

    def list_weather_stations(self) -> list[str]:
        """List all weather station IDs."""
        return list(self._weather_stations.keys())

    def add_pv_system(
        self, system_id: str, config: PVConfig | None = None
    ) -> PVGenerationSimulator:
        """Add a PV generation simulator."""
        if config is None:
            config = PVConfig(system_id=system_id)

        # Get the associated weather station
        weather_station = self.get_weather_station(config.weather_station_id)
        if weather_station is None:
            raise ValueError(
                f"Weather station '{config.weather_station_id}' not found. "
                "PV systems require a weather station for irradiance data."
            )

        simulator = PVGenerationSimulator(
            entity_id=system_id,
            rng=self.engine.rng,
            weather_simulator=weather_station,
            config=config,
        )
        self._pv_systems[system_id] = simulator
        return simulator

    def get_pv_system(self, system_id: str) -> PVGenerationSimulator | None:
        """Get a PV system simulator by ID."""
        return self._pv_systems.get(system_id)

    def list_pv_systems(self) -> list[str]:
        """List all PV system IDs."""
        return list(self._pv_systems.keys())

    def reset(self, new_seed: int | None = None) -> None:
        """Reset the simulation state."""
        if self._engine:
            self._engine.reset(new_seed=new_seed)

        # Recreate simulators with new RNG if seed changed
        if new_seed is not None and self._engine:
            for meter_id, meter in list(self._meters.items()):
                self._meters[meter_id] = EnergyMeterSimulator(
                    entity_id=meter_id,
                    rng=self._engine.rng,
                    config=meter.config,
                )
            for feed_id, feed in list(self._price_feeds.items()):
                self._price_feeds[feed_id] = EnergyPriceSimulator(
                    entity_id=feed_id,
                    rng=self._engine.rng,
                    config=feed.config,
                )
            for device_id, load in list(self._loads.items()):
                self._loads[device_id] = ConsumerLoadSimulator(
                    entity_id=device_id,
                    rng=self._engine.rng,
                    config=load.config,
                )
            for station_id, station in list(self._weather_stations.items()):
                self._weather_stations[station_id] = WeatherSimulator(
                    entity_id=station_id,
                    rng=self._engine.rng,
                    config=station.config,
                )
            # Recreate PV systems with updated weather simulators
            for system_id, pv_system in list(self._pv_systems.items()):
                weather_station = self._weather_stations.get(pv_system.config.weather_station_id)
                if weather_station:
                    self._pv_systems[system_id] = PVGenerationSimulator(
                        entity_id=system_id,
                        rng=self._engine.rng,
                        weather_simulator=weather_station,
                        config=pv_system.config,
                    )


def get_simulation_state() -> SimulationState:
    """FastAPI dependency to get simulation state."""
    state = SimulationState.get_instance()
    if not state._initialized:
        state.initialize()
    return state
