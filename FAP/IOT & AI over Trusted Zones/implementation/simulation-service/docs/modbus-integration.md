# Modbus Integration Guide

## Overview

The simulation service emulates a Janitza UMG 96RM energy meter via Modbus TCP on port 502.

## Connection

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('localhost', port=502)
client.connect()
```

## Register Map

| Register | Type | Parameter | Unit |
|----------|------|-----------|------|
| 19000-19001 | Float32 | Active Power L1 | W |
| 19002-19003 | Float32 | Active Power L2 | W |
| 19004-19005 | Float32 | Active Power L3 | W |
| 19006-19007 | Float32 | Active Power Total | W |
| 19020-19021 | Float32 | Voltage L1-N | V |
| 19022-19023 | Float32 | Voltage L2-N | V |
| 19024-19025 | Float32 | Voltage L3-N | V |
| 19040-19041 | Float32 | Current L1 | A |
| 19042-19043 | Float32 | Current L2 | A |
| 19044-19045 | Float32 | Current L3 | A |
| 19060-19061 | Float32 | Power Factor | - |
| 19062-19063 | Float32 | Total Active Energy | kWh |
| 19064-19065 | Float32 | Frequency | Hz |

## Reading Values

```python
import struct

# Read Active Power L1 (registers 19000-19001)
result = client.read_holding_registers(19000, 2)
value = struct.unpack('>f', struct.pack('>HH', *result.registers))[0]
print(f"Active Power L1: {value} W")
```
