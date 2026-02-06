"""
Modbus TCP server implementation.

Async pymodbus server emulating Janitza UMG 96RM energy meters.
Supports multiple Unit IDs (one per simulated meter).
"""

import asyncio
import logging
from typing import Callable

from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusServerContext,
    ModbusSparseDataBlock,
)
from pymodbus.server import StartAsyncTcpServer

from src.models.meter import MeterReading
from src.simulators.energy_meter.ieee754 import float32_to_registers
from src.simulators.energy_meter.register_map import (
    ALL_REGISTERS,
    MAX_REGISTER_ADDRESS,
    MIN_REGISTER_ADDRESS,
    get_all_register_values,
)

logger = logging.getLogger(__name__)

# Type alias for meter reading provider
MeterReadingProvider = Callable[[str], MeterReading | None]


class JanitzaDataBlock(ModbusSparseDataBlock):
    """
    Custom data block that provides live meter readings.

    This data block dynamically returns current meter values when
    registers are read, rather than storing static values.
    """

    def __init__(
        self,
        meter_id: str,
        reading_provider: MeterReadingProvider,
    ) -> None:
        """
        Initialize the Janitza data block.

        Args:
            meter_id: The meter identifier for this data block.
            reading_provider: Function that returns current MeterReading for a meter ID.
        """
        # Initialize sparse data block with empty values
        # We'll populate dynamically on read
        super().__init__({0: 0})
        self._meter_id = meter_id
        self._reading_provider = reading_provider
        self._register_cache: dict[int, int] = {}

    def _refresh_registers(self) -> None:
        """Refresh register values from the current meter reading."""
        reading = self._reading_provider(self._meter_id)
        if reading is None:
            logger.warning(f"No reading available for meter {self._meter_id}")
            return

        # Get all values and convert to registers
        values = get_all_register_values(reading)

        self._register_cache.clear()
        for address, value in values.items():
            high, low = float32_to_registers(value)
            # pymodbus adds 1 to the client-requested address when calling getValues
            # So if client requests 19020, getValues receives 19021
            # We store at address+1 to compensate for this offset
            self._register_cache[address + 1] = high
            self._register_cache[address + 2] = low

    def getValues(self, address: int, count: int = 1) -> list[int]:
        """
        Get register values starting at address.

        This method is called by pymodbus when a client reads registers.

        Args:
            address: Starting register address (0-based).
            count: Number of registers to read.

        Returns:
            List of register values.
        """
        # Refresh values on every read to get current meter data
        self._refresh_registers()

        # Return requested registers
        result = []
        for i in range(count):
            addr = address + i
            value = self._register_cache.get(addr, 0)
            result.append(value)

        logger.debug(f"Meter {self._meter_id}: Read {count} registers from {address}: {result}")
        return result

    def validate(self, address: int, count: int = 1) -> bool:
        """
        Validate that the requested address range is valid.

        Args:
            address: Starting register address.
            count: Number of registers.

        Returns:
            True if the address range is valid.
        """
        # Allow reads within the Janitza register range
        # We're more permissive here to allow clients to read any range
        # Even if some registers return 0
        end_address = address + count - 1
        return address >= 0 and end_address <= MAX_REGISTER_ADDRESS + 100


class ModbusTCPServer:
    """
    Async Modbus TCP server emulating Janitza energy meters.

    Supports multiple Unit IDs, with each unit representing a different
    simulated energy meter.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 502,
        reading_provider: MeterReadingProvider | None = None,
    ) -> None:
        """
        Initialize the Modbus TCP server.

        Args:
            host: IP address to bind to.
            port: TCP port to listen on.
            reading_provider: Function that provides meter readings by ID.
        """
        self._host = host
        self._port = port
        self._reading_provider = reading_provider or self._default_provider
        self._context: ModbusServerContext | None = None
        self._server_task: asyncio.Task | None = None
        self._unit_ids: dict[int, str] = {}  # unit_id -> meter_id mapping
        self._running = False

    @staticmethod
    def _default_provider(meter_id: str) -> MeterReading | None:
        """Default provider returns None (no data)."""
        return None

    def register_meter(self, unit_id: int, meter_id: str) -> None:
        """
        Register a meter to be served on a specific Unit ID.

        Args:
            unit_id: Modbus unit/slave ID (1-247).
            meter_id: The meter identifier in the simulation.

        Raises:
            ValueError: If unit_id is out of valid range.
        """
        if not 1 <= unit_id <= 247:
            raise ValueError(f"Unit ID must be between 1 and 247, got {unit_id}")

        self._unit_ids[unit_id] = meter_id
        logger.info(f"Registered meter '{meter_id}' on Unit ID {unit_id}")

    def _build_context(self) -> ModbusServerContext:
        """
        Build the Modbus server context with all registered meters.

        Returns:
            Configured ModbusServerContext.
        """
        slaves: dict[int, ModbusDeviceContext] = {}

        for unit_id, meter_id in self._unit_ids.items():
            # Create a data block for this meter
            data_block = JanitzaDataBlock(meter_id, self._reading_provider)

            # Create device context with the data block for holding registers (FC 0x03)
            # hr = holding registers (function code 3)
            # ir = input registers (function code 4)
            slave = ModbusDeviceContext(
                di=None,  # Discrete inputs - not used
                co=None,  # Coils - not used
                hr=data_block,  # Holding registers - our meter data
                ir=data_block,  # Input registers - same data
            )
            slaves[unit_id] = slave

        # Create context with single=False to support multiple unit IDs
        return ModbusServerContext(devices=slaves, single=False)

    async def start(self) -> None:
        """
        Start the Modbus TCP server.

        The server runs in the background and handles client connections.
        """
        if self._running:
            logger.warning("Modbus server is already running")
            return

        if not self._unit_ids:
            logger.warning("No meters registered, server will not respond to requests")

        self._context = self._build_context()
        self._running = True

        logger.info(
            f"Starting Modbus TCP server on {self._host}:{self._port} "
            f"with {len(self._unit_ids)} meter(s)"
        )

        # Start the server
        self._server_task = asyncio.create_task(
            StartAsyncTcpServer(
                context=self._context,
                address=(self._host, self._port),
            )
        )

    async def stop(self) -> None:
        """Stop the Modbus TCP server."""
        if not self._running:
            return

        self._running = False

        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass
            self._server_task = None

        logger.info("Modbus TCP server stopped")

    @property
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self._running

    @property
    def registered_meters(self) -> dict[int, str]:
        """Get the mapping of unit IDs to meter IDs."""
        return self._unit_ids.copy()


async def create_modbus_server(
    host: str = "0.0.0.0",
    port: int = 502,
    meters: dict[int, str] | None = None,
    reading_provider: MeterReadingProvider | None = None,
) -> ModbusTCPServer:
    """
    Factory function to create and configure a Modbus TCP server.

    Args:
        host: IP address to bind to.
        port: TCP port to listen on.
        meters: Dictionary mapping unit IDs to meter IDs.
        reading_provider: Function that provides meter readings.

    Returns:
        Configured ModbusTCPServer instance (not started).

    Example:
        >>> server = await create_modbus_server(
        ...     port=5020,
        ...     meters={1: "meter-001", 2: "meter-002"},
        ...     reading_provider=get_current_reading,
        ... )
        >>> await server.start()
    """
    server = ModbusTCPServer(
        host=host,
        port=port,
        reading_provider=reading_provider,
    )

    if meters:
        for unit_id, meter_id in meters.items():
            server.register_meter(unit_id, meter_id)

    return server
