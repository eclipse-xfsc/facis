"""
Unit tests for IEEE 754 float encoding utilities.

Tests the conversion between Python floats and Modbus register pairs.
"""

import struct

import pytest

from src.simulators.energy_meter.ieee754 import (
    decode_register_list_to_float32,
    encode_float32_to_register_list,
    float32_to_registers,
    registers_to_float32,
)


class TestFloat32ToRegisters:
    """Tests for float32_to_registers function."""

    def test_positive_float(self) -> None:
        """Test encoding a positive float value."""
        high, low = float32_to_registers(230.5)
        # Verify round-trip
        result = registers_to_float32(high, low)
        assert abs(result - 230.5) < 0.001

    def test_zero(self) -> None:
        """Test encoding zero."""
        high, low = float32_to_registers(0.0)
        assert high == 0
        assert low == 0
        assert registers_to_float32(high, low) == 0.0

    def test_negative_float(self) -> None:
        """Test encoding a negative float value."""
        high, low = float32_to_registers(-123.456)
        result = registers_to_float32(high, low)
        assert abs(result - (-123.456)) < 0.001

    def test_small_float(self) -> None:
        """Test encoding a small float value."""
        high, low = float32_to_registers(0.001)
        result = registers_to_float32(high, low)
        assert abs(result - 0.001) < 0.0001

    def test_large_float(self) -> None:
        """Test encoding a large float value."""
        high, low = float32_to_registers(123456.789)
        result = registers_to_float32(high, low)
        # Float32 precision limits
        assert abs(result - 123456.789) < 0.1

    def test_big_endian_byte_order(self) -> None:
        """Verify that encoding uses big-endian byte order."""
        # Pack as big-endian float
        packed_be = struct.pack(">f", 230.5)
        expected_high, expected_low = struct.unpack(">HH", packed_be)

        high, low = float32_to_registers(230.5)
        assert high == expected_high
        assert low == expected_low

    def test_known_value_voltage(self) -> None:
        """Test with a typical voltage value (230V)."""
        high, low = float32_to_registers(230.0)
        result = registers_to_float32(high, low)
        assert abs(result - 230.0) < 0.01

    def test_known_value_frequency(self) -> None:
        """Test with a typical frequency value (50Hz)."""
        high, low = float32_to_registers(50.0)
        result = registers_to_float32(high, low)
        assert abs(result - 50.0) < 0.001

    def test_known_value_power_factor(self) -> None:
        """Test with a typical power factor value (0.95)."""
        high, low = float32_to_registers(0.95)
        result = registers_to_float32(high, low)
        assert abs(result - 0.95) < 0.001


class TestRegistersToFloat32:
    """Tests for registers_to_float32 function."""

    def test_zero_registers(self) -> None:
        """Test decoding zero registers."""
        assert registers_to_float32(0, 0) == 0.0

    def test_round_trip(self) -> None:
        """Test encoding then decoding preserves value."""
        test_values = [0.0, 1.0, -1.0, 230.5, 50.0, 0.95, 12345.678]
        for original in test_values:
            high, low = float32_to_registers(original)
            decoded = registers_to_float32(high, low)
            assert abs(decoded - original) < 0.001, f"Round-trip failed for {original}"


class TestEncodeFloat32ToRegisterList:
    """Tests for encode_float32_to_register_list function."""

    def test_single_value(self) -> None:
        """Test encoding a single value."""
        registers = encode_float32_to_register_list([230.5])
        assert len(registers) == 2
        decoded = decode_register_list_to_float32(registers)
        assert len(decoded) == 1
        assert abs(decoded[0] - 230.5) < 0.001

    def test_multiple_values(self) -> None:
        """Test encoding multiple values."""
        values = [230.5, 50.0, 0.95]
        registers = encode_float32_to_register_list(values)
        assert len(registers) == 6  # 2 registers per value

        decoded = decode_register_list_to_float32(registers)
        assert len(decoded) == 3
        for original, decoded_val in zip(values, decoded):
            assert abs(decoded_val - original) < 0.001

    def test_empty_list(self) -> None:
        """Test encoding an empty list."""
        registers = encode_float32_to_register_list([])
        assert registers == []


class TestDecodeRegisterListToFloat32:
    """Tests for decode_register_list_to_float32 function."""

    def test_empty_list(self) -> None:
        """Test decoding an empty list."""
        values = decode_register_list_to_float32([])
        assert values == []

    def test_odd_length_raises(self) -> None:
        """Test that odd-length list raises ValueError."""
        with pytest.raises(ValueError, match="even length"):
            decode_register_list_to_float32([1, 2, 3])

    def test_round_trip_multiple(self) -> None:
        """Test round-trip encoding/decoding multiple values."""
        original = [230.5, 231.2, 229.8, 50.01, 0.97, 12345.0]
        registers = encode_float32_to_register_list(original)
        decoded = decode_register_list_to_float32(registers)

        assert len(decoded) == len(original)
        for orig, dec in zip(original, decoded):
            assert abs(dec - orig) < 0.01


class TestJanitzaMeterValues:
    """Test encoding/decoding with realistic Janitza meter values."""

    def test_voltage_values(self) -> None:
        """Test encoding typical three-phase voltage values."""
        voltages = [230.5, 231.2, 229.8]  # L1, L2, L3
        registers = encode_float32_to_register_list(voltages)
        decoded = decode_register_list_to_float32(registers)

        for original, decoded_val in zip(voltages, decoded):
            assert abs(decoded_val - original) < 0.1

    def test_current_values(self) -> None:
        """Test encoding typical current values."""
        currents = [45.2, 44.8, 46.1]  # L1, L2, L3 in Amps
        registers = encode_float32_to_register_list(currents)
        decoded = decode_register_list_to_float32(registers)

        for original, decoded_val in zip(currents, decoded):
            assert abs(decoded_val - original) < 0.1

    def test_power_values(self) -> None:
        """Test encoding typical power values in watts."""
        powers = [10234.5, 10123.4, 10345.6]  # L1, L2, L3 in Watts
        registers = encode_float32_to_register_list(powers)
        decoded = decode_register_list_to_float32(registers)

        for original, decoded_val in zip(powers, decoded):
            assert abs(decoded_val - original) < 1.0

    def test_energy_value(self) -> None:
        """Test encoding cumulative energy value."""
        energy_kwh = 123456.789
        high, low = float32_to_registers(energy_kwh)
        decoded = registers_to_float32(high, low)
        # Float32 precision at this magnitude
        assert abs(decoded - energy_kwh) < 0.5

    def test_frequency_value(self) -> None:
        """Test encoding frequency value."""
        frequency = 50.02
        high, low = float32_to_registers(frequency)
        decoded = registers_to_float32(high, low)
        assert abs(decoded - frequency) < 0.001

    def test_power_factor_value(self) -> None:
        """Test encoding power factor value."""
        pf = 0.97
        high, low = float32_to_registers(pf)
        decoded = registers_to_float32(high, low)
        assert abs(decoded - pf) < 0.001
