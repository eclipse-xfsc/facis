# Energy Meter Simulator

from src.simulators.energy_meter.ieee754 import (
    decode_register_list_to_float32,
    encode_float32_to_register_list,
    float32_to_registers,
    registers_to_float32,
)
from src.simulators.energy_meter.load_curves import (
    WEEKDAY_LOAD_CURVE,
    WEEKEND_LOAD_CURVE,
    DayType,
    calculate_power_from_load_factor,
    distribute_power_across_phases,
    get_day_type,
    get_load_factor,
    get_load_factor_with_noise,
)
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
from src.simulators.energy_meter.simulator import EnergyMeterSimulator, EnergyState

__all__ = [
    # Simulator
    "EnergyMeterSimulator",
    "EnergyState",
    # Load curves
    "DayType",
    "get_day_type",
    "get_load_factor",
    "get_load_factor_with_noise",
    "calculate_power_from_load_factor",
    "distribute_power_across_phases",
    "WEEKDAY_LOAD_CURVE",
    "WEEKEND_LOAD_CURVE",
    # IEEE 754 encoding
    "float32_to_registers",
    "registers_to_float32",
    "encode_float32_to_register_list",
    "decode_register_list_to_float32",
    # Register map
    "RegisterType",
    "RegisterDefinition",
    "ACTIVE_POWER_L1",
    "ACTIVE_POWER_L2",
    "ACTIVE_POWER_L3",
    "ACTIVE_POWER_TOTAL",
    "VOLTAGE_L1_N",
    "VOLTAGE_L2_N",
    "VOLTAGE_L3_N",
    "CURRENT_L1",
    "CURRENT_L2",
    "CURRENT_L3",
    "POWER_FACTOR",
    "TOTAL_ACTIVE_ENERGY",
    "FREQUENCY",
    "ALL_REGISTERS",
    "REGISTER_MAP",
    "MIN_REGISTER_ADDRESS",
    "MAX_REGISTER_ADDRESS",
    "get_register_value",
    "get_all_register_values",
]
