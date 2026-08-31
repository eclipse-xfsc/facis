---
doc_id: TSM-25-21-55
doc_type: TSM
title: Fault Isolation - Intermittent CAN segment fault (F-25-2140)
ata: 25-21
revision: R6
effective: 2026-05-20
classification: SYNTHETIC TRAINING DOCUMENT
---

# Fault code F-25-2140 - CAN segment A error burst / node lost

## Symptom
Seat control panel unresponsive for seconds to minutes, then normal operation.
SCU logs error bursts on CAN segment A. The defect is very often NOT reproducible
during a static functional test on the ground.

## Why this is a no-fault-found trap
Error bursts on this segment correlate with airframe vibration. In service data,
more than 70 % of bursts occur in taxi, climb or descent, and fewer than 5 %
occur in stable cruise. A ground test without vibration input will therefore
usually pass, and a removed SCU will usually test serviceable in the shop.

Before removing any LRU on this fault code, complete the vibration-correlated
checks below.

## Fault isolation procedure
1. Download the BITE log and correlate error bursts with flight phase. If the
   bursts cluster in taxi / climb / descent, treat the fault as a wiring or
   connector defect, not as an SCU defect.
2. Inspect connector DA-CON-3390 at both ends of harness segment DA-HRN-7712.
   Look for backed-out pins, corrosion and missing locking clips.
3. Perform a wiggle test on the harness segment while monitoring the CAN error
   counter. An error rate increase during the wiggle test confirms the defect.
4. Measure the bus termination resistance. Nominal is 60 ohm across the segment.
5. Replace the connector kit DA-CON-3390 first. Replace the harness segment
   DA-HRN-7712 only if the wiggle test still produces errors.
6. Remove the SCU only after steps 2 to 5 have been completed and documented.

## Deferral
If the suite cannot be repaired before departure, see MEL-25-21-02.
