"""
Integration tests for Modbus TCP server.

Tests the full Modbus server with client connections.
"""

import asyncio
from datetime import UTC, datetime

import pytest
from pymodbus.client import AsyncModbusTcpClient

from src.api.modbus.server import ModbusTCPServer, create_modbus_server
from src.models.meter import MeterReading, MeterReadings
from src.simulators.energy_meter.ieee754 import registers_to_float32
from src.simulators.energy_meter.register_map import (
    ACTIVE_POWER_L1,
    ACTIVE_POWER_TOTAL,
    CURRENT_L1,
    FREQUENCY,
    POWER_FACTOR,
    TOTAL_ACTIVE_ENERGY,
    VOLTAGE_L1_N,
)


def create_test_reading(meter_id: str = "test-meter-001") -> MeterReading:
    """Create a test meter reading with known values."""
    readings = MeterReadings(
        active_power_l1_w=10234.5,
        active_power_l2_w=10123.4,
        active_power_l3_w=10345.6,
        voltage_l1_v=230.5,
        voltage_l2_v=231.2,
        voltage_l3_v=229.8,
        current_l1_a=45.2,
        current_l2_a=44.8,
        current_l3_a=46.1,
        power_factor=0.97,
        frequency_hz=50.02,
        total_energy_kwh=123456.789,
    )
    return MeterReading(
        timestamp=datetime(2026, 1, 15, 14, 30, 0, tzinfo=UTC),
        meter_id=meter_id,
        readings=readings,
    )


# Store for test readings
_test_readings: dict[str, MeterReading] = {}


def _reading_provider(meter_id: str) -> MeterReading | None:
    """Reading provider that returns stored readings."""
    return _test_readings.get(meter_id)


@pytest.fixture
def meter_reading() -> MeterReading:
    """Create and store a test meter reading."""
    reading = create_test_reading("test-meter-001")
    _test_readings["test-meter-001"] = reading
    return reading


@pytest.fixture
def second_meter_reading() -> MeterReading:
    """Create a second meter reading with different values."""
    readings = MeterReadings(
        active_power_l1_w=5000.0,
        active_power_l2_w=5100.0,
        active_power_l3_w=4900.0,
        voltage_l1_v=229.0,
        voltage_l2_v=230.0,
        voltage_l3_v=231.0,
        current_l1_a=22.0,
        current_l2_a=22.2,
        current_l3_a=21.8,
        power_factor=0.95,
        frequency_hz=49.98,
        total_energy_kwh=50000.0,
    )
    reading = MeterReading(
        timestamp=datetime(2026, 1, 15, 14, 30, 0, tzinfo=UTC),
        meter_id="test-meter-002",
        readings=readings,
    )
    _test_readings["test-meter-002"] = reading
    return reading


class TestModbusTCPServer:
    """Tests for ModbusTCPServer class."""

    def test_server_creation(self, free_tcp_port: int) -> None:
        """Test server can be created with default settings."""
        server = ModbusTCPServer(port=free_tcp_port)
        assert server._port == free_tcp_port
        assert server._host == "0.0.0.0"
        assert not server.is_running

    def test_register_meter(self, free_tcp_port: int) -> None:
        """Test registering a meter to a unit ID."""
        server = ModbusTCPServer(port=free_tcp_port)
        server.register_meter(1, "meter-001")
        assert server.registered_meters == {1: "meter-001"}

    def test_register_multiple_meters(self, free_tcp_port: int) -> None:
        """Test registering multiple meters."""
        server = ModbusTCPServer(port=free_tcp_port)
        server.register_meter(1, "meter-001")
        server.register_meter(2, "meter-002")
        server.register_meter(10, "meter-010")
        assert server.registered_meters == {
            1: "meter-001",
            2: "meter-002",
            10: "meter-010",
        }

    def test_register_meter_invalid_unit_id_zero(self, free_tcp_port: int) -> None:
        """Test that unit ID 0 raises ValueError."""
        server = ModbusTCPServer(port=free_tcp_port)
        with pytest.raises(ValueError, match="Unit ID must be between 1 and 247"):
            server.register_meter(0, "meter-001")

    def test_register_meter_invalid_unit_id_high(self, free_tcp_port: int) -> None:
        """Test that unit ID > 247 raises ValueError."""
        server = ModbusTCPServer(port=free_tcp_port)
        with pytest.raises(ValueError, match="Unit ID must be between 1 and 247"):
            server.register_meter(248, "meter-001")


class TestCreateModbusServer:
    """Tests for create_modbus_server factory function."""

    @pytest.mark.asyncio
    async def test_create_with_meters(self, free_tcp_port: int) -> None:
        """Test creating server with meters dictionary."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "meter-001", 2: "meter-002"},
        )
        assert server.registered_meters == {1: "meter-001", 2: "meter-002"}

    @pytest.mark.asyncio
    async def test_create_without_meters(self, free_tcp_port: int) -> None:
        """Test creating server without meters."""
        server = await create_modbus_server(port=free_tcp_port)
        assert server.registered_meters == {}


@pytest.mark.asyncio
class TestModbusClientConnection:
    """Integration tests with actual Modbus client connections."""

    async def test_server_start_stop(self, free_tcp_port: int, meter_reading: MeterReading) -> None:
        """Test server can start and stop."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001"},
            reading_provider=_reading_provider,
        )

        await server.start()
        assert server.is_running

        # Give server time to start
        await asyncio.sleep(0.1)

        await server.stop()
        assert not server.is_running

    async def test_read_voltage_register(
        self, free_tcp_port: int, meter_reading: MeterReading
    ) -> None:
        """Test reading voltage register via Modbus client."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001"},
            reading_provider=_reading_provider,
        )

        await server.start()
        await asyncio.sleep(0.3)

        try:
            client = AsyncModbusTcpClient("127.0.0.1", port=free_tcp_port)
            connected = await client.connect()
            assert connected, "Failed to connect to Modbus server"

            # Read voltage L1 (address 19020, 2 registers)
            result = await client.read_holding_registers(
                address=VOLTAGE_L1_N.address,
                count=2,
                device_id=1,
            )

            assert not result.isError(), f"Modbus error: {result}"
            voltage = registers_to_float32(result.registers[0], result.registers[1])
            assert abs(voltage - 230.5) < 0.1

            client.close()
        finally:
            await server.stop()

    async def test_read_active_power_register(
        self, free_tcp_port: int, meter_reading: MeterReading
    ) -> None:
        """Test reading active power register via Modbus client."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001"},
            reading_provider=_reading_provider,
        )

        await server.start()
        await asyncio.sleep(0.3)

        try:
            client = AsyncModbusTcpClient("127.0.0.1", port=free_tcp_port)
            connected = await client.connect()
            assert connected, "Failed to connect to Modbus server"

            # Read active power L1 (address 19000, 2 registers)
            result = await client.read_holding_registers(
                address=ACTIVE_POWER_L1.address,
                count=2,
                device_id=1,
            )

            assert not result.isError(), f"Modbus error: {result}"
            power = registers_to_float32(result.registers[0], result.registers[1])
            assert abs(power - 10234.5) < 1.0

            client.close()
        finally:
            await server.stop()

    async def test_read_total_power_register(
        self, free_tcp_port: int, meter_reading: MeterReading
    ) -> None:
        """Test reading total active power register."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001"},
            reading_provider=_reading_provider,
        )

        await server.start()
        await asyncio.sleep(0.3)

        try:
            client = AsyncModbusTcpClient("127.0.0.1", port=free_tcp_port)
            connected = await client.connect()
            assert connected, "Failed to connect to Modbus server"

            # Read total active power (address 19006, 2 registers)
            result = await client.read_holding_registers(
                address=ACTIVE_POWER_TOTAL.address,
                count=2,
                device_id=1,
            )

            assert not result.isError(), f"Modbus error: {result}"
            total_power = registers_to_float32(result.registers[0], result.registers[1])
            expected = 10234.5 + 10123.4 + 10345.6
            assert abs(total_power - expected) < 1.0

            client.close()
        finally:
            await server.stop()

    async def test_read_frequency_register(
        self, free_tcp_port: int, meter_reading: MeterReading
    ) -> None:
        """Test reading frequency register."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001"},
            reading_provider=_reading_provider,
        )

        await server.start()
        await asyncio.sleep(0.3)

        try:
            client = AsyncModbusTcpClient("127.0.0.1", port=free_tcp_port)
            connected = await client.connect()
            assert connected, "Failed to connect to Modbus server"

            result = await client.read_holding_registers(
                address=FREQUENCY.address,
                count=2,
                device_id=1,
            )

            assert not result.isError(), f"Modbus error: {result}"
            frequency = registers_to_float32(result.registers[0], result.registers[1])
            assert abs(frequency - 50.02) < 0.01

            client.close()
        finally:
            await server.stop()

    async def test_read_multiple_registers(
        self, free_tcp_port: int, meter_reading: MeterReading
    ) -> None:
        """Test reading multiple consecutive registers."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001"},
            reading_provider=_reading_provider,
        )

        await server.start()
        await asyncio.sleep(0.3)

        try:
            client = AsyncModbusTcpClient("127.0.0.1", port=free_tcp_port)
            connected = await client.connect()
            assert connected, "Failed to connect to Modbus server"

            # Read all 4 power registers (L1, L2, L3, Total = 8 registers)
            result = await client.read_holding_registers(
                address=ACTIVE_POWER_L1.address,
                count=8,
                device_id=1,
            )

            assert not result.isError(), f"Modbus error: {result}"
            assert len(result.registers) == 8

            power_l1 = registers_to_float32(result.registers[0], result.registers[1])
            power_l2 = registers_to_float32(result.registers[2], result.registers[3])
            power_l3 = registers_to_float32(result.registers[4], result.registers[5])
            power_total = registers_to_float32(result.registers[6], result.registers[7])

            assert abs(power_l1 - 10234.5) < 1.0
            assert abs(power_l2 - 10123.4) < 1.0
            assert abs(power_l3 - 10345.6) < 1.0
            assert abs(power_total - (10234.5 + 10123.4 + 10345.6)) < 1.0

            client.close()
        finally:
            await server.stop()

    async def test_multiple_unit_ids(
        self,
        free_tcp_port: int,
        meter_reading: MeterReading,
        second_meter_reading: MeterReading,
    ) -> None:
        """Test reading from multiple unit IDs."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001", 2: "test-meter-002"},
            reading_provider=_reading_provider,
        )

        await server.start()
        await asyncio.sleep(0.3)

        try:
            client = AsyncModbusTcpClient("127.0.0.1", port=free_tcp_port)
            connected = await client.connect()
            assert connected, "Failed to connect to Modbus server"

            # Read from unit 1
            result1 = await client.read_holding_registers(
                address=ACTIVE_POWER_L1.address,
                count=2,
                device_id=1,
            )
            assert not result1.isError(), f"Modbus error: {result1}"
            power1 = registers_to_float32(result1.registers[0], result1.registers[1])
            assert abs(power1 - 10234.5) < 1.0  # First meter value

            # Read from unit 2
            result2 = await client.read_holding_registers(
                address=ACTIVE_POWER_L1.address,
                count=2,
                device_id=2,
            )
            assert not result2.isError(), f"Modbus error: {result2}"
            power2 = registers_to_float32(result2.registers[0], result2.registers[1])
            assert abs(power2 - 5000.0) < 1.0  # Second meter value

            client.close()
        finally:
            await server.stop()

    async def test_read_current_registers(
        self, free_tcp_port: int, meter_reading: MeterReading
    ) -> None:
        """Test reading current registers."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001"},
            reading_provider=_reading_provider,
        )

        await server.start()
        await asyncio.sleep(0.3)

        try:
            client = AsyncModbusTcpClient("127.0.0.1", port=free_tcp_port)
            connected = await client.connect()
            assert connected, "Failed to connect to Modbus server"

            result = await client.read_holding_registers(
                address=CURRENT_L1.address,
                count=2,
                device_id=1,
            )

            assert not result.isError(), f"Modbus error: {result}"
            current = registers_to_float32(result.registers[0], result.registers[1])
            assert abs(current - 45.2) < 0.1

            client.close()
        finally:
            await server.stop()

    async def test_read_power_factor_register(
        self, free_tcp_port: int, meter_reading: MeterReading
    ) -> None:
        """Test reading power factor register."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001"},
            reading_provider=_reading_provider,
        )

        await server.start()
        await asyncio.sleep(0.3)

        try:
            client = AsyncModbusTcpClient("127.0.0.1", port=free_tcp_port)
            connected = await client.connect()
            assert connected, "Failed to connect to Modbus server"

            result = await client.read_holding_registers(
                address=POWER_FACTOR.address,
                count=2,
                device_id=1,
            )

            assert not result.isError(), f"Modbus error: {result}"
            pf = registers_to_float32(result.registers[0], result.registers[1])
            assert abs(pf - 0.97) < 0.01

            client.close()
        finally:
            await server.stop()

    async def test_read_energy_register(
        self, free_tcp_port: int, meter_reading: MeterReading
    ) -> None:
        """Test reading total energy register."""
        server = await create_modbus_server(
            port=free_tcp_port,
            meters={1: "test-meter-001"},
            reading_provider=_reading_provider,
        )

        await server.start()
        await asyncio.sleep(0.3)

        try:
            client = AsyncModbusTcpClient("127.0.0.1", port=free_tcp_port)
            connected = await client.connect()
            assert connected, "Failed to connect to Modbus server"

            result = await client.read_holding_registers(
                address=TOTAL_ACTIVE_ENERGY.address,
                count=2,
                device_id=1,
            )

            assert not result.isError(), f"Modbus error: {result}"
            energy = registers_to_float32(result.registers[0], result.registers[1])
            # Float32 precision at this magnitude
            assert abs(energy - 123456.789) < 1.0

            client.close()
        finally:
            await server.stop()
