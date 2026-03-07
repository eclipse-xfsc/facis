# Modbus TCP Register Reference

**Project:** FACIS FAP — IoT & AI Demonstrator
**Protocol:** Modbus TCP
**Default Port:** 5020 (configurable)
**Meter Emulation:** Janitza UMG 96RM

---

## Connection

| Parameter | Value |
|---|---|
| Protocol | Modbus TCP |
| Default Port | 5020 |
| Unit ID | 1 |
| Supported Functions | FC 03 (Read Holding Registers), FC 04 (Read Input Registers) |
| Max Concurrent Clients | 10+ |

## Register Map

All registers use IEEE 754 single-precision (Float32) encoding across 2 consecutive 16-bit registers (Big-Endian byte order).

| Register | Type | Parameter | Unit | Range |
|---|---|---|---|---|
| 19000–19001 | Float32 | Active Power L1 | W | 0–50,000 |
| 19002–19003 | Float32 | Active Power L2 | W | 0–50,000 |
| 19004–19005 | Float32 | Active Power L3 | W | 0–50,000 |
| 19006–19007 | Float32 | Active Power Total | W | 0–150,000 |
| 19020–19021 | Float32 | Voltage L1-N | V | 220–240 |
| 19022–19023 | Float32 | Voltage L2-N | V | 220–240 |
| 19024–19025 | Float32 | Voltage L3-N | V | 220–240 |
| 19040–19041 | Float32 | Current L1 | A | 0–100 |
| 19042–19043 | Float32 | Current L2 | A | 0–100 |
| 19044–19045 | Float32 | Current L3 | A | 0–100 |
| 19060–19061 | Float32 | Power Factor | — | 0.0–1.0 |
| 19062–19063 | Float32 | Total Active Energy | kWh | Monotonically increasing |
| 19064–19065 | Float32 | Frequency | Hz | 49.9–50.1 |

## Data Characteristics

- Values are physically correlated: P = V × I × PF
- Voltage fluctuates realistically around 230V nominal
- Energy counters increment monotonically (never reset during simulation)
- Three-phase readings include realistic phase imbalance (±5%)
- Load curves follow weekday/weekend industrial patterns

## Client Example (Python)

```python
from pymodbus.client import ModbusTcpClient
import struct

client = ModbusTcpClient("localhost", port=5020)
client.connect()

# Read Active Power L1 (registers 19000-19001)
result = client.read_holding_registers(19000, 2, slave=1)
raw = struct.pack(">HH", result.registers[0], result.registers[1])
power_l1 = struct.unpack(">f", raw)[0]
print(f"Active Power L1: {power_l1:.1f} W")

client.close()
```

## Exception Handling

| Exception Code | Meaning |
|---|---|
| 0x01 | Illegal Function |
| 0x02 | Illegal Data Address (invalid register) |
| 0x03 | Illegal Data Value |

---

© ATLAS IoT Lab GmbH — Licensed under Apache License 2.0
