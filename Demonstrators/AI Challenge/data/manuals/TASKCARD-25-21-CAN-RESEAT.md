---
doc_id: TASK-25-21-CAN-RESEAT
doc_type: TASKCARD
title: Task card - inspect and re-seat suite CAN connector
ata: 25-21
estimated_duration_min: 55
required_skill: ATA25-CABIN, AVIONICS-CAN
required_authorisation: B1
classification: SYNTHETIC TRAINING DOCUMENT
---

# Task card: CAN connector inspection and re-seat

Tools: torque screwdriver 0.4-2.0 Nm, contact cleaner, borescope, CAN test set.
Parts (as required): DA-CON-3390 connector kit.

## Steps
1. Safety: confirm cabin power to the suite is isolated. Attach the warning tag.
2. Remove the seat pan access panel. Four captive screws, 1.2 Nm on refit.
3. Locate connector DA-CON-3390 at the SCU port and at the harness junction.
4. Inspect both connectors with the borescope. Record any corrosion, bent or
   backed-out pins with a photograph.
5. Clean the contacts. Re-seat both connectors until the locking clip audibly
   engages.
6. Connect the CAN test set. Run the wiggle test for 3 minutes while monitoring
   the error counter. Acceptance: zero new errors during the wiggle test.
7. Measure the bus termination. Acceptance: 60 ohm plus/minus 6 ohm.
8. Refit the access panel. Torque 1.2 Nm.
9. Run the suite functional test: full recline cycle, divider stow cycle, IFE boot.
10. Clear the BITE fault. Record the work order, the measured values and the
    photographs.

## Sign-off
Certifying staff B1 signature required. Attach the CAN test set log to the work order.
