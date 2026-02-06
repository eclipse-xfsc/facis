"""
IEEE 754 float encoding utilities.

Converts between Python floats and Modbus register pairs.
Janitza meters use big-endian byte order for Float32 values.
"""

import struct


def float32_to_registers(value: float) -> tuple[int, int]:
    """
    Convert a float to two 16-bit Modbus registers (big-endian).

    IEEE 754 single-precision float is 32 bits (4 bytes).
    Modbus registers are 16 bits each, so we need 2 registers.

    Big-endian byte order means:
    - Register 1 (high): Most significant 16 bits
    - Register 2 (low): Least significant 16 bits

    Args:
        value: The float value to convert.

    Returns:
        Tuple of (high_register, low_register).

    Example:
        >>> float32_to_registers(230.5)
        (17142, 32768)  # 0x4366, 0x8000
    """
    # Pack float as big-endian 32-bit float
    packed = struct.pack(">f", value)
    # Unpack as two big-endian 16-bit unsigned integers
    high, low = struct.unpack(">HH", packed)
    return high, low


def registers_to_float32(high: int, low: int) -> float:
    """
    Convert two 16-bit Modbus registers to a float (big-endian).

    Args:
        high: High register (most significant 16 bits).
        low: Low register (least significant 16 bits).

    Returns:
        The decoded float value.

    Example:
        >>> registers_to_float32(17142, 32768)
        230.5
    """
    # Pack as two big-endian 16-bit unsigned integers
    packed = struct.pack(">HH", high, low)
    # Unpack as big-endian 32-bit float
    (value,) = struct.unpack(">f", packed)
    return value


def encode_float32_to_register_list(values: list[float]) -> list[int]:
    """
    Encode multiple float values to a flat list of registers.

    This is useful for populating Modbus data blocks where
    consecutive register pairs represent float values.

    Args:
        values: List of float values to encode.

    Returns:
        Flat list of 16-bit register values (2 registers per float).

    Example:
        >>> encode_float32_to_register_list([230.5, 50.0])
        [17142, 32768, 16968, 0]  # 4 registers for 2 floats
    """
    registers: list[int] = []
    for value in values:
        high, low = float32_to_registers(value)
        registers.extend([high, low])
    return registers


def decode_register_list_to_float32(registers: list[int]) -> list[float]:
    """
    Decode a flat list of registers to float values.

    Args:
        registers: List of 16-bit register values (must be even length).

    Returns:
        List of decoded float values.

    Raises:
        ValueError: If register list has odd length.

    Example:
        >>> decode_register_list_to_float32([17142, 32768, 16968, 0])
        [230.5, 50.0]
    """
    if len(registers) % 2 != 0:
        raise ValueError(f"Register list must have even length, got {len(registers)}")

    values: list[float] = []
    for i in range(0, len(registers), 2):
        value = registers_to_float32(registers[i], registers[i + 1])
        values.append(value)
    return values
