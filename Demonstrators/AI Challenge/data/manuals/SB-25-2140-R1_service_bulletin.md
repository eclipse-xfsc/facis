---
doc_id: SB-25-2140-R1
doc_type: SB
title: Service Bulletin - improved locking clip for connector DA-CON-3390
ata: 25-21
revision: R1
effective: 2026-07-01
classification: SYNTHETIC TRAINING DOCUMENT
---

# Reason

Operators reported intermittent CAN segment A faults (F-25-2140) on suites with
harness segment DA-HRN-7712 installed before serial batch 4400. The root cause
was identified as insufficient retention of the connector locking clip under
vibration.

# Effectivity

All suites with SCU firmware 3.4.x and harness batches below 4400. Firmware 3.5.0
adds error-burst counters per flight phase, which makes the defect detectable
from the health data before the cabin crew reports it.

# Action

Install the improved locking clip kit at the next base maintenance visit.
Expected effect: reduction of F-25-2140 no-fault-found removals by approximately
half, based on the manufacturer fleet sample. This figure is a synthetic
assumption for the exercise.
