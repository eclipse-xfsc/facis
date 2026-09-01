---
doc_id: AMM-25-21-11
doc_type: AMM
title: Suite Control Unit (SCU) - Description and Operation
ata: 25-21
revision: R7
effective: 2026-04-01
applicability: A350-941 / A350-1041, first class suite DA-STE-1000
classification: SYNTHETIC TRAINING DOCUMENT - not a real maintenance manual
---

# 1. General

The Suite Control Unit (SCU, P/N DA-SCU-4410) is the seat-level controller for
one first class suite. It drives the backrest actuator (DA-ACT-2201), the legrest
actuator (DA-ACT-2205), the privacy divider drive module (DA-DIV-1180) and the
seat power supply unit (DA-PSU-5150).

The SCU communicates with the Cabin Services System over CAN segment A. Each
suite forms one node. Loss of a single node does not affect the other suites.

# 2. Operating limits

| Parameter | Nominal | Caution | Limit |
|---|---|---|---|
| Backrest actuator current | 2.2 - 2.8 A | > 3.5 A sustained 10 s | 4.5 A (thermal cutout) |
| Legrest actuator current | 1.6 - 2.2 A | > 3.0 A sustained 10 s | 3.8 A |
| Position error, any axis | < 2 % | > 5 % | 8 % (fault latched) |
| SCU internal temperature | 25 - 45 C | > 60 C | 72 C (derating) |
| CAN segment A error counter | 0 - 5 per hour | > 20 per hour | 100 per hour (bus off) |

# 3. Built-in test (BITE)

The SCU records a fault code, a timestamp, the flight phase and a sensor snapshot
for every latched fault. BITE memory holds the last 64 events and is downloaded
via the cabin maintenance terminal or streamed to the ground through the aircraft
health link.

A latched fault is cleared only by a successful functional test (see TSM-25-21-40)
or by a power cycle of the suite. A cleared fault that returns within 10 flight
hours must be treated as a repeat defect and must not be closed as no-fault-found.
