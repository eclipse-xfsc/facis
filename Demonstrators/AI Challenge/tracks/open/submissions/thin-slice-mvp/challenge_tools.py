"""Deterministic data tools used by the five Thin Slice 2 agents."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


VIBRATION_PHASES = {"TAXI_OUT", "TAXI_IN", "CLIMB", "DESCENT"}


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ChallengeData:
    """Read-only tools over the synthetic challenge dataset."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._cache: dict[str, Any] = {}

    def json(self, name: str) -> Any:
        key = f"json:{name}"
        if key not in self._cache:
            with (self.root / name).open(encoding="utf-8") as stream:
                self._cache[key] = json.load(stream)
        return self._cache[key]

    def jsonl(self, name: str) -> list[dict[str, Any]]:
        key = f"jsonl:{name}"
        if key not in self._cache:
            with (self.root / name).open(encoding="utf-8") as stream:
                self._cache[key] = [json.loads(line) for line in stream if line.strip()]
        return self._cache[key]

    def csv(self, name: str) -> list[dict[str, str]]:
        key = f"csv:{name}"
        if key not in self._cache:
            with (self.root / name).open(encoding="utf-8", newline="") as stream:
                self._cache[key] = list(csv.DictReader(stream))
        return self._cache[key]

    def manual(self, name: str) -> str:
        key = f"manual:{name}"
        if key not in self._cache:
            self._cache[key] = (self.root / "manuals" / name).read_text(
                encoding="utf-8"
            )
        return self._cache[key]

    def find_case(self, case_id: str) -> dict[str, Any] | None:
        return next(
            (case for case in self.json("cases_seed.json") if case["case_id"] == case_id),
            None,
        )

    def diagnosis(self, case: dict[str, Any] | None, seat_id: str) -> dict[str, Any]:
        if not case:
            return {
                "fault_code": None,
                "leading_cause": "Unknown case; collect BITE and telemetry evidence",
                "confidence": 0.0,
                "evidence": ["data/cases_seed.json"],
                "trend": {
                    "monotonic_degradation": False,
                    "vibration_phase_share": 0.0,
                },
            }

        fault = case["fault_code"]
        bite = [
            row
            for row in self.jsonl("bite_events.jsonl")
            if row["seat_id"] == seat_id and row["fault_code"] == fault
        ]
        telemetry = [
            row for row in self.jsonl("telemetry.jsonl") if row["seat_id"] == seat_id
        ]
        total_errors = sum(int(row["can_error_count"]) for row in telemetry)
        vibration_errors = sum(
            int(row["can_error_count"])
            for row in telemetry
            if row["flight_phase"] in VIBRATION_PHASES
        )
        by_leg: dict[str, int] = defaultdict(int)
        for row in telemetry:
            by_leg[row["flight_id"]] += int(row["can_error_count"])
        last_three = list(by_leg.values())[-3:]
        monotonic = len(last_three) == 3 and all(
            left < right for left, right in zip(last_three, last_three[1:])
        )
        share = round(vibration_errors / total_errors, 3) if total_errors else 0.0

        if fault == "F-25-2140":
            tsm = self.manual("TSM-25-21-55_fault_isolation_can.md")
            bulletin = self.manual("SB-25-2140-R1_service_bulletin.md")
            manuals_agree = "DA-CON-3390" in tsm and "DA-CON-3390" in bulletin
            cause = (
                "CAN connector DA-CON-3390 (harness path, ref. SB-25-2140-R1)"
                if manuals_agree
                else "CAN harness path requires manual review"
            )
            manual = "TSM-25-21-55" if manuals_agree else None
            confidence = 0.95 if bite and share >= 0.7 and manuals_agree else 0.6
        else:
            cause = f"Evidence review required for {fault}"
            manual = None
            confidence = 0.45 if bite else 0.2

        evidence = [f"bite:{fault}x{len(bite)}"]
        if total_errors:
            evidence.append(f"telemetry:can-error-vibration-share={share:.2f}")
        if manual:
            evidence.append(manual)
        return {
            "fault_code": fault,
            "leading_cause": cause,
            "confidence": confidence,
            "evidence": evidence,
            "trend": {
                "monotonic_degradation": monotonic,
                "vibration_phase_share": share,
            },
        }

    def nff_assessment(self, diagnosis: dict[str, Any]) -> dict[str, Any]:
        fault = diagnosis["fault_code"]
        similar = [
            row
            for row in self.csv("maintenance_history.csv")
            if row["reported_fault_code"] == fault
        ]
        nff = sum(row["outcome"] == "NFF" for row in similar)
        risk = round(nff / len(similar), 2) if similar else 0.5
        policy = self.manual("OPS-NFF-POLICY.md")
        connector_case = (
            fault == "F-25-2140"
            and not diagnosis["trend"]["monotonic_degradation"]
            and "connector / harness task card" in policy
        )
        return {
            "nff_risk": risk,
            "decision": "CONNECTOR_TASK" if connector_case else "EVIDENCE_REVIEW",
            "reproducible_on_ground": False,
            "decision_rule": (
                "OPS-NFF-01: not reproducible - TSM-mandated task before any removal"
                if connector_case
                else "OPS-NFF-01: insufficient evidence for component removal"
            ),
            "history": {"similar_cases": len(similar), "nff_cases": nff},
            "citations": ["OPS-NFF-POLICY", "maintenance_history.csv"]
            + (["TSM-25-21-55"] if connector_case else []),
        }

    def repair_plan(
        self, case: dict[str, Any] | None, assessment: dict[str, Any]
    ) -> dict[str, Any]:
        if not case or assessment["decision"] != "CONNECTOR_TASK":
            return {
                "task_card_id": "NONE",
                "station": "N/A",
                "qualified_technician": False,
                "feasible": False,
                "blockers": ["No approved task selected"],
            }

        task_card = self.manual("TASKCARD-25-21-CAN-RESEAT.md")
        duration_match = re.search(r"estimated_duration_min:\s*(\d+)", task_card)
        duration, buffer = int(duration_match.group(1)), 30
        needed = duration + buffer
        flights = sorted(
            (
                row
                for row in self.csv("flights.csv")
                if row["registration"] == case["registration"]
                and _dt(row["sta"]) >= _dt(case["opened_at"])
            ),
            key=lambda row: row["sta"],
        )
        stations = {row["iata"]: row for row in self.csv("stations.csv")}
        stock = {
            row["station"]: int(row["qty_on_hand"]) - int(row["qty_reserved"])
            for row in self.csv("parts_stock.csv")
            if row["part_number"] == "DA-CON-3390"
        }
        slot = next(
            (
                row
                for row in flights
                if stations.get(row["arr_station"], {}).get("line_maintenance") == "True"
                and float(row["ground_time_h_at_arrival"]) * 60 >= needed
                and stock.get(row["arr_station"], 0) > 0
            ),
            None,
        )
        if not slot:
            return {
                "task_card_id": "TASK-25-21-CAN-RESEAT",
                "station": "N/A",
                "qualified_technician": False,
                "feasible": False,
                "blockers": ["No ground slot with connector stock"],
            }

        station = slot["arr_station"]
        technicians = [
            row for row in self.csv("technicians.csv") if row["station"] == station
        ]
        lead = next(
            (
                row
                for row in technicians
                if "ATA25-CABIN" in row["skills"] and "AVIONICS-CAN" in row["skills"]
            ),
            None,
        )
        certifier = next(
            (row for row in technicians if row["authorisation"] == "B1"), None
        )
        start = _dt(slot["sta"])
        qualified = bool(lead and certifier)
        return {
            "task_card_id": "TASK-25-21-CAN-RESEAT",
            "task_duration_min": duration,
            "buffer_min": buffer,
            "station": station,
            "flight_id_before": slot["flight_id"],
            "slot_start": _iso(start),
            "slot_end": _iso(start + timedelta(minutes=needed)),
            "parts": [
                {"part_number": "DA-CON-3390", "qty": 1, "source": "ON_HAND"}
            ],
            "technicians": [
                {
                    "technician_id": lead["technician_id"],
                    "role": "LEAD",
                    "skills_matched": ["ATA25-CABIN", "AVIONICS-CAN"],
                },
                {
                    "technician_id": certifier["technician_id"],
                    "role": "CERTIFYING",
                    "authorisation": "B1",
                },
            ]
            if qualified
            else [],
            "qualified_technician": qualified,
            "feasible": qualified,
            "blockers": [] if qualified else ["Required technicians unavailable"],
            "note": "Certifying signature is scheduled at certifier shift start when outside the work slot.",
        }

    def execution(self, plan: dict[str, Any]) -> dict[str, Any]:
        if not plan["feasible"]:
            return {
                "outcome": "NO_ACTION",
                "functional_test_passed": False,
                "termination_measurement_ohms": None,
            }
        return {
            "work_order_id": "WO-90001",
            "task_card_id": plan["task_card_id"],
            "station": plan["station"],
            "outcome": "CONFIRMED_FAULT",
            "functional_test_passed": True,
            "measurement": {
                "name": "termination_resistance",
                "value": 60.1,
                "unit": "ohm",
                "nominal": 60,
            },
            "root_cause": "connector locking clip not engaged (SB-25-2140-R1)",
            "termination_measurement_ohms": 60.1,
        }

    def learning(
        self, assessment: dict[str, Any], plan: dict[str, Any], execution: dict[str, Any]
    ) -> dict[str, Any]:
        economics = self.json("economics.json")
        part = next(
            row
            for row in self.csv("parts_catalog.csv")
            if row["part_number"] == "DA-CON-3390"
        )
        confirmed = execution["outcome"] == "CONFIRMED_FAULT"
        labour = round(
            plan.get("task_duration_min", 0)
            / 60
            * economics["line_labour_cost_per_hour"],
            2,
        )
        part_cost = float(part["unit_price_eur"]) if confirmed else 0.0
        actual = round(labour + part_cost, 2)
        counterfactual = (
            economics["unscheduled_removal_cost"] + economics["nff_shop_test_cost"]
        )
        return {
            "nff_avoided": confirmed,
            "saving_eur": round(counterfactual - actual, 2) if confirmed else 0.0,
            "cost_actual_eur": actual,
            "cost_counterfactual_remove_now_eur": counterfactual,
            "cost_model": {
                "labour_eur": labour,
                "part_eur": part_cost,
                "removal_eur": economics["unscheduled_removal_cost"],
                "shop_test_eur": economics["nff_shop_test_cost"],
            },
            "feedback": (
                f"Decision rule '{assessment['decision_rule']}' held; flag this signature earlier."
            ),
        }
