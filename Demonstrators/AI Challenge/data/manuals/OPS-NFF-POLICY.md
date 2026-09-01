---
doc_id: OPS-NFF-01
doc_type: POLICY
title: No-Fault-Found policy for cabin LRU removals (synthetic)
revision: R2
effective: 2026-05-01
classification: SYNTHETIC TRAINING DOCUMENT
---

# Purpose

Reduce unnecessary removals of cabin LRUs and the associated shop cost, without
dispatching an aircraft with an unresolved cabin-safety defect.

# Decision rules used in this exercise

1. A removal is justified when at least one of the following holds:
   a) the fault is reproducible in a functional test on the ground, or
   b) the trend data shows a monotonic degradation over at least three flight
      legs, or
   c) the fault is cabin-safety relevant (divider stow, seat lock) and cannot be
      cleared by the applicable task card.
2. If none of these hold, the defect is classified as NOT REPRODUCIBLE. The
   required action is the connector / harness task card plus continued monitoring
   for the next 10 flight legs, not an LRU removal.
3. Every removal request for a rotable LRU must carry an NFF risk score between
   0 and 1 with a written justification and the evidence used.
4. An NFF risk above 0.6 requires a second opinion from the component owner
   (manufacturer or MRO) before the removal is released. This is the external
   request path across the organisational boundary.
5. Cost anchors for the trade-off: a blocked first class suite costs the airline
   approximately EUR 10,000 per leg in lost revenue, an unscheduled removal
   approximately EUR 3,800, and a shop test that finds nothing approximately
   EUR 1,450. These are synthetic planning figures for the exercise.
