---
doc_id: TSM-25-21-40
doc_type: TSM
title: Fault Isolation - Backrest actuator overcurrent (F-25-2101)
ata: 25-21
revision: R4
effective: 2026-02-15
classification: SYNTHETIC TRAINING DOCUMENT
---

# Fault code F-25-2101 - Recline actuator overcurrent / thermal cutout

## Symptom
Backrest moves slowly or stops before the commanded position. SCU logs current
above 3.5 A and position error above 5 %. Cabin crew typically report "seat does
not go flat".

## Probable causes, in order of likelihood
1. Mechanical obstruction in the backrest kinematics (foreign object, seat belt,
   pax personal item) - approx. 45 % of confirmed cases.
2. Gearbox wear in actuator DA-ACT-2201 - approx. 35 %.
3. Degraded connector at the SCU actuator port - approx. 15 %.
4. SCU driver stage failure - approx. 5 %.

## Fault isolation procedure
1. Visually inspect the kinematics envelope. Remove any obstruction. Repeat a
   full range-of-motion test.
2. Record the actuator current trend over 5 full cycles. A rising trend across
   cycles with no obstruction indicates gearbox wear.
3. Disconnect and inspect the actuator connector for corrosion and bent pins.
   Re-seat and lock. Repeat the test.
4. If the current stays above 3.5 A, replace the actuator DA-ACT-2201.
   Do not replace the SCU first: the historical no-fault-found rate for SCU
   removals on this symptom is high.

## Notes on trend data
An actuator whose mean current per cycle has increased by more than 0.8 A over
the last 200 actuation cycles is a wear candidate even when the current is still
inside limits. Plan the replacement at the next base maintenance opportunity
rather than as an unscheduled removal.
