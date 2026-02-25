"""
Janitza UMG 96RM register map definitions.

Maps Modbus registers to measurement parameters.
Based on Janitza UMG 96RM manual section 11.2.

Register addresses use 0-based indexing (Modbus convention).
Float32 values span 2 consecutive registers in big-endian byte order.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from src.models.meter import MeterReading


class RegisterType(Enum):
    """Modbus register data types."""

    FLOAT32 = "float32"  # IEEE 754 single precision, 2 registers


@dataclass(frozen=True)
class RegisterDefinition:
    """Definition of a Modbus register or register pair."""

    address: int  # 0-based register address
    name: str  # Human-readable name
    unit: str  # Unit of measurement
    register_type: RegisterType = RegisterType.FLOAT32
    scale: float = 1.0  # Multiplier (value * scale = register value)

    @property
    def register_count(self) -> int:
        """Number of 16-bit registers this value spans."""
        if self.register_type == RegisterType.FLOAT32:
            return 2
        return 1


# =============================================================================
# Janitza UMG 96RM Register Map (from spec section 11.2)
# =============================================================================
# Register addresses are 0-based (subtract 1 from 1-based addresses in manual)
# Example: Manual says 19001-19002, we use 19000-19001 (0-based)

# Active Power registers (W)
ACTIVE_POWER_L1 = RegisterDefinition(
    address=19000,
    name="Active Power L1",
    unit="W",
)
ACTIVE_POWER_L2 = RegisterDefinition(
    address=19002,
    name="Active Power L2",
    unit="W",
)
ACTIVE_POWER_L3 = RegisterDefinition(
    address=19004,
    name="Active Power L3",
    unit="W",
)
ACTIVE_POWER_TOTAL = RegisterDefinition(
    address=19006,
    name="Active Power Total",
    unit="W",
)

# Voltage registers (V)
VOLTAGE_L1_N = RegisterDefinition(
    address=19020,
    name="Voltage L1-N",
    unit="V",
)
VOLTAGE_L2_N = RegisterDefinition(
    address=19022,
    name="Voltage L2-N",
    unit="V",
)
VOLTAGE_L3_N = RegisterDefinition(
    address=19024,
    name="Voltage L3-N",
    unit="V",
)

# Current registers (A)
CURRENT_L1 = RegisterDefinition(
    address=19040,
    name="Current L1",
    unit="A",
)
CURRENT_L2 = RegisterDefinition(
    address=19042,
    name="Current L2",
    unit="A",
)
CURRENT_L3 = RegisterDefinition(
    address=19044,
    name="Current L3",
    unit="A",
)

# Power Factor and Energy registers
POWER_FACTOR = RegisterDefinition(
    address=19060,
    name="Power Factor",
    unit="-",
)
TOTAL_ACTIVE_ENERGY = RegisterDefinition(
    address=19062,
    name="Total Active Energy",
    unit="kWh",
)
FREQUENCY = RegisterDefinition(
    address=19064,
    name="Frequency",
    unit="Hz",
)

# All register definitions in address order
ALL_REGISTERS: list[RegisterDefinition] = [
    ACTIVE_POWER_L1,
    ACTIVE_POWER_L2,
    ACTIVE_POWER_L3,
    ACTIVE_POWER_TOTAL,
    VOLTAGE_L1_N,
    VOLTAGE_L2_N,
    VOLTAGE_L3_N,
    CURRENT_L1,
    CURRENT_L2,
    CURRENT_L3,
    POWER_FACTOR,
    TOTAL_ACTIVE_ENERGY,
    FREQUENCY,
]

# Register address to definition mapping
REGISTER_MAP: dict[int, RegisterDefinition] = {reg.address: reg for reg in ALL_REGISTERS}

# Minimum and maximum register addresses
MIN_REGISTER_ADDRESS = min(reg.address for reg in ALL_REGISTERS)
MAX_REGISTER_ADDRESS = max(reg.address + reg.register_count - 1 for reg in ALL_REGISTERS)


def get_register_value(reading: MeterReading, register: RegisterDefinition) -> float:
    """
    Extract the value for a register from a meter reading.

    Args:
        reading: The meter reading containing all values.
        register: The register definition to extract.

    Returns:
        The float value for this register.

    Raises:
        ValueError: If register is not recognized.
    """
    readings = reading.readings

    value_map: dict[int, float] = {
        ACTIVE_POWER_L1.address: readings.active_power_l1_w,
        ACTIVE_POWER_L2.address: readings.active_power_l2_w,
        ACTIVE_POWER_L3.address: readings.active_power_l3_w,
        ACTIVE_POWER_TOTAL.address: (
            readings.active_power_l1_w + readings.active_power_l2_w + readings.active_power_l3_w
        ),
        VOLTAGE_L1_N.address: readings.voltage_l1_v,
        VOLTAGE_L2_N.address: readings.voltage_l2_v,
        VOLTAGE_L3_N.address: readings.voltage_l3_v,
        CURRENT_L1.address: readings.current_l1_a,
        CURRENT_L2.address: readings.current_l2_a,
        CURRENT_L3.address: readings.current_l3_a,
        POWER_FACTOR.address: readings.power_factor,
        TOTAL_ACTIVE_ENERGY.address: readings.total_energy_kwh,
        FREQUENCY.address: readings.frequency_hz,
    }

    if register.address not in value_map:
        raise ValueError(f"Unknown register address: {register.address}")

    return value_map[register.address] * register.scale


def get_all_register_values(reading: MeterReading) -> dict[int, float]:
    """
    Get all register values from a meter reading.

    Args:
        reading: The meter reading containing all values.

    Returns:
        Dictionary mapping register addresses to float values.
    """
    return {reg.address: get_register_value(reading, reg) for reg in ALL_REGISTERS}


# Type alias for value provider function
ValueProvider = Callable[[], MeterReading | None]
