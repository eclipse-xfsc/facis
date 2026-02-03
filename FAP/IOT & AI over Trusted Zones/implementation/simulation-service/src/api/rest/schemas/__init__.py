# API Schemas

from src.api.rest.schemas.common import (
    ConfigResponse,
    ConfigUpdateRequest,
    ErrorResponse,
    HealthResponse,
    IntervalParam,
    PaginatedResponse,
    TimeRangeQuery,
)
from src.api.rest.schemas.consumer_load import (
    ConsumerLoadCurrentResponse,
    ConsumerLoadHistoryResponse,
    ConsumerLoadInfo,
    ConsumerLoadListResponse,
    ConsumerLoadReadingResponse,
    OperatingWindowSchema,
)
from src.api.rest.schemas.meter import (
    MeterHistoryResponse,
    MeterInfo,
    MeterListResponse,
    MeterReadingResponse,
    MeterReadingsSchema,
)
from src.api.rest.schemas.price import (
    PriceCurrentResponse,
    PriceForecastResponse,
    PriceHistoryResponse,
    PriceReadingResponse,
)
from src.api.rest.schemas.simulation import (
    SimulationPauseResponse,
    SimulationResetRequest,
    SimulationResetResponse,
    SimulationStartRequest,
    SimulationStartResponse,
    SimulationStatusResponse,
)
from src.api.rest.schemas.weather import (
    ConditionsSchema,
    LocationSchema,
    WeatherHistoryResponse,
    WeatherListResponse,
    WeatherReadingResponse,
    WeatherStationInfo,
)

__all__ = [
    # Common
    "IntervalParam",
    "TimeRangeQuery",
    "PaginatedResponse",
    "ErrorResponse",
    "HealthResponse",
    "ConfigResponse",
    "ConfigUpdateRequest",
    # Meter
    "MeterReadingsSchema",
    "MeterReadingResponse",
    "MeterInfo",
    "MeterListResponse",
    "MeterHistoryResponse",
    # Price
    "PriceReadingResponse",
    "PriceCurrentResponse",
    "PriceForecastResponse",
    "PriceHistoryResponse",
    # Consumer Load
    "OperatingWindowSchema",
    "ConsumerLoadReadingResponse",
    "ConsumerLoadInfo",
    "ConsumerLoadListResponse",
    "ConsumerLoadCurrentResponse",
    "ConsumerLoadHistoryResponse",
    # Simulation
    "SimulationStatusResponse",
    "SimulationStartRequest",
    "SimulationStartResponse",
    "SimulationPauseResponse",
    "SimulationResetRequest",
    "SimulationResetResponse",
    # Weather
    "LocationSchema",
    "ConditionsSchema",
    "WeatherReadingResponse",
    "WeatherStationInfo",
    "WeatherListResponse",
    "WeatherHistoryResponse",
]
