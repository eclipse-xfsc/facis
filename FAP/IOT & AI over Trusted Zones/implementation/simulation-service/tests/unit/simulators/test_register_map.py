"""
Unit tests for Janitza register map definitions.

Tests the register mapping and value extraction from meter readings.
"""

from datetime import UTC, datetime

import pytest

from src.models.meter import MeterReading, MeterReadings
from src.simulators.energy_meter.register_map import (
    ACTIVE_POWER_L1,
    ACTIVE_POWER_L2,
    ACTIVE_POWER_L3,
    ACTIVE_POWER_TOTAL,
    ALL_REGISTERS,
    CURRENT_L1,
    CURRENT_L2,
    CURRENT_L3,
    FREQUENCY,
    MAX_REGISTER_ADDRESS,
    MIN_REGISTER_ADDRESS,
    POWER_FACTOR,
    REGISTER_MAP,
    TOTAL_ACTIVE_ENERGY,
    VOLTAGE_L1_N,
    VOLTAGE_L2_N,
    VOLTAGE_L3_N,
    RegisterDefinition,
    RegisterType,
    get_all_register_values,
    get_register_value,
)


@pytest.fixture
def sample_meter_reading() -> MeterReading:
    """Create a sample meter reading for testing."""
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
        meter_id="test-meter-001",
        readings=readings,
    )


class TestRegisterDefinition:
    """Tests for RegisterDefinition dataclass."""

    def test_float32_register_count(self) -> None:
        """Test that Float32 registers span 2 addresses."""
        reg = RegisterDefinition(
            address=19000,
            name="Test Register",
            unit="W",
            register_type=RegisterType.FLOAT32,
        )
        assert reg.register_count == 2

    def test_register_immutability(self) -> None:
        """Test that register definitions are immutable."""
        with pytest.raises(Exception):  # FrozenInstanceError
            ACTIVE_POWER_L1.address = 0  # type: ignore

    def test_default_scale_is_one(self) -> None:
        """Test that default scale is 1.0."""
        reg = RegisterDefinition(
            address=19000,
            name="Test",
            unit="W",
        )
        assert reg.scale == 1.0


class TestRegisterAddresses:
    """Tests for register address definitions."""

    def test_active_power_addresses(self) -> None:
        """Test active power register addresses match spec."""
        assert ACTIVE_POWER_L1.address == 19000
        assert ACTIVE_POWER_L2.address == 19002
        assert ACTIVE_POWER_L3.address == 19004
        assert ACTIVE_POWER_TOTAL.address == 19006

    def test_voltage_addresses(self) -> None:
        """Test voltage register addresses match spec."""
        assert VOLTAGE_L1_N.address == 19020
        assert VOLTAGE_L2_N.address == 19022
        assert VOLTAGE_L3_N.address == 19024

    def test_current_addresses(self) -> None:
        """Test current register addresses match spec."""
        assert CURRENT_L1.address == 19040
        assert CURRENT_L2.address == 19042
        assert CURRENT_L3.address == 19044

    def test_other_register_addresses(self) -> None:
        """Test power factor, energy, and frequency addresses."""
        assert POWER_FACTOR.address == 19060
        assert TOTAL_ACTIVE_ENERGY.address == 19062
        assert FREQUENCY.address == 19064

    def test_register_units(self) -> None:
        """Test that register units are correctly defined."""
        assert ACTIVE_POWER_L1.unit == "W"
        assert VOLTAGE_L1_N.unit == "V"
        assert CURRENT_L1.unit == "A"
        assert POWER_FACTOR.unit == "-"
        assert TOTAL_ACTIVE_ENERGY.unit == "kWh"
        assert FREQUENCY.unit == "Hz"


class TestAllRegisters:
    """Tests for ALL_REGISTERS list."""

    def test_all_registers_count(self) -> None:
        """Test that all 13 registers are defined."""
        assert len(ALL_REGISTERS) == 13

    def test_all_registers_unique_addresses(self) -> None:
        """Test that all register addresses are unique."""
        addresses = [reg.address for reg in ALL_REGISTERS]
        assert len(addresses) == len(set(addresses))

    def test_register_map_matches_all_registers(self) -> None:
        """Test REGISTER_MAP contains all registers from ALL_REGISTERS."""
        for reg in ALL_REGISTERS:
            assert reg.address in REGISTER_MAP
            assert REGISTER_MAP[reg.address] == reg


class TestMinMaxAddresses:
    """Tests for MIN/MAX register address constants."""

    def test_min_address(self) -> None:
        """Test MIN_REGISTER_ADDRESS is correct."""
        expected_min = min(reg.address for reg in ALL_REGISTERS)
        assert MIN_REGISTER_ADDRESS == expected_min
        assert MIN_REGISTER_ADDRESS == 19000

    def test_max_address(self) -> None:
        """Test MAX_REGISTER_ADDRESS includes the last register pair."""
        # FREQUENCY is at 19064-19065
        expected_max = max(reg.address + reg.register_count - 1 for reg in ALL_REGISTERS)
        assert MAX_REGISTER_ADDRESS == expected_max
        assert MAX_REGISTER_ADDRESS == 19065


class TestGetRegisterValue:
    """Tests for get_register_value function."""

    def test_active_power_l1(self, sample_meter_reading: MeterReading) -> None:
        """Test extracting active power L1."""
        value = get_register_value(sample_meter_reading, ACTIVE_POWER_L1)
        assert value == 10234.5

    def test_active_power_l2(self, sample_meter_reading: MeterReading) -> None:
        """Test extracting active power L2."""
        value = get_register_value(sample_meter_reading, ACTIVE_POWER_L2)
        assert value == 10123.4

    def test_active_power_l3(self, sample_meter_reading: MeterReading) -> None:
        """Test extracting active power L3."""
        value = get_register_value(sample_meter_reading, ACTIVE_POWER_L3)
        assert value == 10345.6

    def test_active_power_total(self, sample_meter_reading: MeterReading) -> None:
        """Test extracting total active power (sum of phases)."""
        value = get_register_value(sample_meter_reading, ACTIVE_POWER_TOTAL)
        expected = 10234.5 + 10123.4 + 10345.6
        assert abs(value - expected) < 0.01

    def test_voltage_values(self, sample_meter_reading: MeterReading) -> None:
        """Test extracting voltage values."""
        assert get_register_value(sample_meter_reading, VOLTAGE_L1_N) == 230.5
        assert get_register_value(sample_meter_reading, VOLTAGE_L2_N) == 231.2
        assert get_register_value(sample_meter_reading, VOLTAGE_L3_N) == 229.8

    def test_current_values(self, sample_meter_reading: MeterReading) -> None:
        """Test extracting current values."""
        assert get_register_value(sample_meter_reading, CURRENT_L1) == 45.2
        assert get_register_value(sample_meter_reading, CURRENT_L2) == 44.8
        assert get_register_value(sample_meter_reading, CURRENT_L3) == 46.1

    def test_power_factor(self, sample_meter_reading: MeterReading) -> None:
        """Test extracting power factor."""
        value = get_register_value(sample_meter_reading, POWER_FACTOR)
        assert value == 0.97

    def test_total_energy(self, sample_meter_reading: MeterReading) -> None:
        """Test extracting total energy."""
        value = get_register_value(sample_meter_reading, TOTAL_ACTIVE_ENERGY)
        assert value == 123456.789

    def test_frequency(self, sample_meter_reading: MeterReading) -> None:
        """Test extracting frequency."""
        value = get_register_value(sample_meter_reading, FREQUENCY)
        assert value == 50.02

    def test_unknown_register_raises(self, sample_meter_reading: MeterReading) -> None:
        """Test that unknown register address raises ValueError."""
        unknown_reg = RegisterDefinition(
            address=99999,
            name="Unknown",
            unit="?",
        )
        with pytest.raises(ValueError, match="Unknown register address"):
            get_register_value(sample_meter_reading, unknown_reg)


class TestGetAllRegisterValues:
    """Tests for get_all_register_values function."""

    def test_returns_all_values(self, sample_meter_reading: MeterReading) -> None:
        """Test that all register values are returned."""
        values = get_all_register_values(sample_meter_reading)
        assert len(values) == len(ALL_REGISTERS)

    def test_all_addresses_present(self, sample_meter_reading: MeterReading) -> None:
        """Test that all register addresses are in the result."""
        values = get_all_register_values(sample_meter_reading)
        for reg in ALL_REGISTERS:
            assert reg.address in values

    def test_values_match_individual_extraction(self, sample_meter_reading: MeterReading) -> None:
        """Test that values match individual get_register_value calls."""
        all_values = get_all_register_values(sample_meter_reading)

        for reg in ALL_REGISTERS:
            individual_value = get_register_value(sample_meter_reading, reg)
            assert all_values[reg.address] == individual_value


class TestRegisterNaming:
    """Tests for register naming conventions."""

    def test_power_register_names(self) -> None:
        """Test power register names follow convention."""
        assert "Active Power L1" in ACTIVE_POWER_L1.name
        assert "Active Power L2" in ACTIVE_POWER_L2.name
        assert "Active Power L3" in ACTIVE_POWER_L3.name
        assert "Active Power Total" in ACTIVE_POWER_TOTAL.name

    def test_voltage_register_names(self) -> None:
        """Test voltage register names follow convention."""
        assert "Voltage L1-N" in VOLTAGE_L1_N.name
        assert "Voltage L2-N" in VOLTAGE_L2_N.name
        assert "Voltage L3-N" in VOLTAGE_L3_N.name

    def test_current_register_names(self) -> None:
        """Test current register names follow convention."""
        assert "Current L1" in CURRENT_L1.name
        assert "Current L2" in CURRENT_L2.name
        assert "Current L3" in CURRENT_L3.name
