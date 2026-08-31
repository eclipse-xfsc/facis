---
doc_id: TSM-23-34-20
doc_type: TSM
title: Fault Isolation - Seat electronics box thermal shutdown (F-23-3401)
ata: 23-34
revision: R3
effective: 2026-01-10
classification: SYNTHETIC TRAINING DOCUMENT
---

# Fault code F-23-3401 - SEB thermal shutdown

## Symptom
In-flight entertainment at one suite switches off after several hours of cruise
and recovers after a cool-down period. SEB temperature exceeds 78 C before the
shutdown.

## Probable causes
1. Blocked cooling path of the seat electronics box DA-IFE-9002 (dust, pax items
   stored under the seat) - most common.
2. Failed cooling fan inside the SEB.
3. Elevated cabin floor temperature in that zone.

## Procedure
1. Inspect and clean the air inlet and outlet of the SEB. Confirm the required
   free space under the seat pan.
2. Run the SEB self-test with the cabin ground cooling active and record the
   temperature trend for 30 minutes.
3. If the temperature rises above 70 C at idle load, replace the SEB.
4. IFE unavailability at a single suite does not make the suite unsellable, but
   it is a passenger-experience item and must be entered in the cabin log.

## No-fault-found note
A bench test of a removed SEB at ambient temperature will usually pass. Always
attach the in-flight temperature trend to the removal tag.
