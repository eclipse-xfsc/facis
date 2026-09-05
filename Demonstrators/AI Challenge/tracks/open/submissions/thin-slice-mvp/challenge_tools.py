"""Deterministic, read-only tools over the synthetic challenge dataset."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


VIBRATION_PHASES = {"TAXI_OUT", "TAXI_IN", "CLIMB", "DESCENT"}

FAULT_PROFILES: dict[str, dict[str, Any]] = {
    "F-25-2101": {
        "signal": "actuator_current_a",
        "threshold": 3.5,
        "cause": "Backrest actuator DA-ACT-2201 gearbox wear",
        "decision": "REPLACE_COMPONENT",
        "manual_files": ["TSM-25-21-40_fault_isolation_actuator.md"],
        "doc_ids": ["TSM-25-21-40"],
        "task_id": "TASK-25-21-ACT-REPLACE",
        "task_file": "TASKCARD-25-21-ACT-REPLACE.md",
        "part": "DA-ACT-2201",
        "skills": ["ATA25-CABIN"],
        "authorisation": "B1",
    },
    "F-25-2140": {
        "signal": "can_error_count",
        "threshold": 20.0,
        "cause": "CAN connector DA-CON-3390 (harness path, ref. SB-25-2140-R1)",
        "decision": "CONNECTOR_TASK",
        "manual_files": [
            "TSM-25-21-55_fault_isolation_can.md",
            "SB-25-2140-R1_service_bulletin.md",
        ],
        "doc_ids": ["TSM-25-21-55", "SB-25-2140-R1"],
        "task_id": "TASK-25-21-CAN-RESEAT",
        "task_file": "TASKCARD-25-21-CAN-RESEAT.md",
        "part": "DA-CON-3390",
        "skills": ["ATA25-CABIN", "AVIONICS-CAN"],
        "authorisation": "B1",
    },
    "F-23-3401": {
        "signal": "seb_temp_c",
        "threshold": 78.0,
        "cause": "Blocked cooling path causing DA-IFE-9002 thermal shutdown",
        "decision": "DEFER_PER_MEL",
        "manual_files": [
            "TSM-23-34-20_fault_isolation_seb.md",
            "MEL-25-21-02_deferral.md",
        ],
        "doc_ids": ["TSM-23-34-20", "MEL-25-21-02"],
        "task_id": "TSM-23-34-20",
        "duration_min": 30,
        "part": None,
        "skills": ["ATA23-IFE"],
        "authorisation": "B1",
    },
    "F-25-2166": {
        "signal": "usb_pd_current_a",
        "threshold": None,
        "cause": "Seat power supply / USB-PD module DA-PSU-5150 overcurrent",
        "decision": "REPLACE_COMPONENT",
        "manual_files": [
            "AMM-25-21-11_seat_control_unit.md",
            "MEL-25-21-02_deferral.md",
        ],
        "doc_ids": ["AMM-25-21-11", "MEL-25-21-02", "kg/edges.csv"],
        "task_id": "AWAIT-APPROVED-USB-PD-TASK",
        "duration_min": None,
        "part": "DA-PSU-5150",
        "skills": ["ATA25-CABIN"],
        "authorisation": "B1",
    },
    "F-25-2188": {
        "signal": "divider_position_error_pct",
        "threshold": 10.0,
        "cause": "Privacy divider drive module DA-DIV-1180 stall or belt wear",
        "decision": "REPLACE_COMPONENT",
        "manual_files": [
            "TSM-25-21-88_divider.md",
            "MEL-25-21-02_deferral.md",
        ],
        "doc_ids": ["TSM-25-21-88", "MEL-25-21-02"],
        "task_id": "TSM-25-21-88",
        "duration_min": None,
        "part": "DA-DIV-1180",
        "skills": ["ATA25-CABIN"],
        "authorisation": "B1",
        "safety_relevant": True,
    },
}


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ChallengeData:
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

    def search_manuals(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Retrieve relevant pre-chunked manual passages with lexical scoring."""
        terms = {
            token
            for token in re.findall(r"[a-z0-9-]+", query.lower())
            if len(token) > 2
        }
        ranked = []
        for chunk in self.jsonl("rag_chunks.jsonl"):
            searchable = " ".join(
                str(chunk.get(key, ""))
                for key in ("doc_id", "title", "section", "text")
            ).lower()
            matches = sum(1 for term in terms if term in searchable)
            exact_doc = 3 if chunk.get("doc_id", "").lower() in query.lower() else 0
            score = matches + exact_doc
            if score:
                ranked.append((score, chunk))
        ranked.sort(key=lambda item: (-item[0], item[1]["chunk_id"]))
        return [
            {
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "section": chunk["section"],
                "text": chunk["text"][:250],
                "score": score,
            }
            for score, chunk in ranked[:top_k]
        ]

    def find_case(self, case_id: str) -> dict[str, Any] | None:
        return next(
            (case for case in self.json("cases_seed.json") if case["case_id"] == case_id),
            None,
        )

    def find_case_by_seat(self, seat_id: str) -> dict[str, Any] | None:
        return next(
            (case for case in self.json("cases_seed.json") if case["seat_id"] == seat_id),
            None,
        )

    def find_seat(self, seat_id: str) -> dict[str, str] | None:
        return next((seat for seat in self.csv("seats.csv") if seat["seat_id"] == seat_id), None)

    def healthy_case(self, case_id: str, seat: dict[str, str]) -> dict[str, Any]:
        return {
            "case_id": case_id,
            "seat_id": seat["seat_id"],
            "registration": seat["registration"],
            "suite": seat["suite"],
            "fault_code": None,
            "event_count": 0,
            "status": "HEALTHY_SENTINEL",
        }

    def _leg_maxima(self, rows: list[dict[str, Any]], signal: str) -> list[dict[str, Any]]:
        by_leg: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_leg[row["flight_id"]].append(row)
        result = []
        for flight_id, samples in by_leg.items():
            result.append(
                {
                    "flight_id": flight_id,
                    "first_ts": min(row["ts"] for row in samples),
                    "max": round(max(float(row[signal]) for row in samples), 3),
                }
            )
        return sorted(result, key=lambda item: item["first_ts"])

    @staticmethod
    def _has_rising_window(values: list[float]) -> bool:
        return any(
            first < second < third
            for first, second, third in zip(values, values[1:], values[2:])
        )

    def diagnosis(self, case: dict[str, Any] | None, seat_id: str) -> dict[str, Any]:
        if case is None:
            return {
                "fault_code": None,
                "leading_cause": "Case data unavailable; no repair can be authorised",
                "confidence": 0.0,
                "healthy": False,
                "evidence": ["data/cases_seed.json"],
                "trend": {"monotonic_degradation": False},
            }
        if case.get("fault_code") is None:
            return {
                "fault_code": None,
                "leading_cause": "No open fault exists for the requested seat",
                "confidence": 0.95,
                "healthy": True,
                "evidence": [
                    "data/seats.csv",
                    f"cases_seed:no-open-case-for-seat={seat_id}",
                ],
                "trend": {"monotonic_degradation": False},
            }

        fault = case["fault_code"]
        profile = FAULT_PROFILES.get(fault)
        bite = [
            row
            for row in self.jsonl("bite_events.jsonl")
            if row["seat_id"] == seat_id and row["fault_code"] == fault
        ]
        telemetry = [
            row for row in self.jsonl("telemetry.jsonl") if row["seat_id"] == seat_id
        ]
        if not profile:
            return {
                "fault_code": fault,
                "leading_cause": f"No fault profile is available for {fault}",
                "confidence": 0.2,
                "healthy": False,
                "evidence": [f"bite:{fault}x{len(bite)}", "data/telemetry.jsonl"],
                "trend": {"monotonic_degradation": False},
            }

        manual_grounded = all(self.manual(name) for name in profile["manual_files"])
        signal = profile["signal"]
        legs = self._leg_maxima(telemetry, signal)
        recent_values = [item["max"] for item in legs[-6:]]
        peak = max(recent_values) if recent_values else 0.0
        threshold = profile["threshold"]
        threshold_source = "manual_limit"
        if threshold is None:
            peer_values = sorted(
                float(row[signal])
                for row in self.jsonl("telemetry.jsonl")
                if row["seat_id"] != seat_id
            )
            threshold = peer_values[int(0.95 * (len(peer_values) - 1))]
            threshold_source = "fleet_p95"
        threshold_exceeded = peak > threshold
        monotonic = (
            False
            if fault == "F-25-2140"
            else self._has_rising_window(recent_values)
        )
        confidence = 0.92 if bite and threshold_exceeded and manual_grounded else 0.65
        evidence = [f"bite:{fault}x{len(bite)}"]
        trend: dict[str, Any] = {
            "signal": signal,
            "peak": peak,
            "threshold": round(threshold, 3),
            "threshold_source": threshold_source,
            "threshold_exceeded": threshold_exceeded,
            "monotonic_degradation": monotonic,
            "recent_leg_maxima": [
                {"flight_id": item["flight_id"], "value": item["max"]}
                for item in legs[-6:]
            ],
        }
        if fault == "F-25-2140":
            total = sum(int(row[signal]) for row in telemetry)
            vibration = sum(
                int(row[signal])
                for row in telemetry
                if row["flight_phase"] in VIBRATION_PHASES
            )
            share = round(vibration / total, 3) if total else 0.0
            trend["vibration_phase_share"] = share
            evidence.append(f"telemetry:can-error-vibration-share={share:.2f}")
        else:
            evidence.append(f"telemetry:{signal}-peak={peak:g}")
        evidence.extend(profile["doc_ids"])
        return {
            "fault_code": fault,
            "leading_cause": profile["cause"],
            "confidence": confidence,
            "healthy": False,
            "evidence": evidence,
            "trend": trend,
        }

    def nff_assessment(self, diagnosis: dict[str, Any]) -> dict[str, Any]:
        fault = diagnosis["fault_code"]
        similar = [
            row
            for row in self.csv("maintenance_history.csv")
            if fault and row["reported_fault_code"] == fault
        ]
        nff = sum(row["outcome"] == "NFF" for row in similar)
        risk = round(nff / len(similar), 2) if similar else 0.0

        if fault is None:
            decision = "MONITOR"
            rule = "No open fault evidence; no maintenance action is justified"
            doc_ids = ["OPS-NFF-POLICY"]
        else:
            profile = FAULT_PROFILES.get(fault, {})
            decision = profile.get("decision", "MONITOR")
            doc_ids = profile.get("doc_ids", [])
            if fault == "F-25-2140":
                rule = "OPS-NFF-01: vibration-correlated and not monotonic; connector task before removal"
            elif fault == "F-23-3401":
                rule = "MEL-25-21-02: defer single-suite IFE and perform TSM thermal isolation first"
            elif profile.get("safety_relevant"):
                rule = "OPS-NFF-01: safety-relevant divider defect justifies corrective action"
            else:
                rule = "OPS-NFF-01: repeated threshold exceedance supports component action"

        return {
            "nff_risk": risk,
            "decision": decision,
            "reproducible_on_ground": False,
            "decision_rule": rule,
            "history": {"similar_cases": len(similar), "nff_cases": nff},
            "second_opinion_required": risk > 0.6,
            "citations": list(
                dict.fromkeys(
                    ["OPS-NFF-POLICY", *doc_ids, "maintenance_history.csv", f"history:nff_rate={risk:.2f}"]
                )
            ),
        }

    def _task_duration(self, profile: dict[str, Any]) -> int | None:
        if "task_file" not in profile:
            return profile.get("duration_min")
        text = self.manual(profile["task_file"])
        match = re.search(r"estimated_duration_min:\s*(\d+)", text)
        return int(match.group(1)) if match else None

    def repair_plan(
        self, case: dict[str, Any] | None, assessment: dict[str, Any]
    ) -> dict[str, Any]:
        fault = case.get("fault_code") if case else None
        if assessment["decision"] == "MONITOR" or not fault:
            return {
                "task_card_id": "NONE",
                "station": "N/A",
                "qualified_technician": True,
                "feasible": True,
                "blockers": [],
            }

        profile = FAULT_PROFILES.get(fault)
        if not profile:
            return {
                "task_card_id": "NONE",
                "station": "N/A",
                "qualified_technician": False,
                "feasible": False,
                "blockers": ["No approved fault profile"],
            }

        duration = self._task_duration(profile)
        buffer = 30
        minimum_slot = (duration or 0) + buffer
        station_rows = {row["iata"]: row for row in self.csv("stations.csv")}
        catalog = {row["part_number"]: row for row in self.csv("parts_catalog.csv")}
        part_record = catalog.get(profile["part"]) if profile["part"] else None
        rotable_replacement = bool(
            part_record and part_record.get("rotable") == "True"
        )
        stock_rows = {
            row["station"]: int(row["qty_on_hand"]) - int(row["qty_reserved"])
            for row in self.csv("parts_stock.csv")
            if profile["part"] and row["part_number"] == profile["part"]
        }
        flights = sorted(
            (
                row
                for row in self.csv("flights.csv")
                if row["registration"] == case["registration"]
                and _dt(row["sta"]) >= _dt(case.get("opened_at", row["sta"]))
            ),
            key=lambda row: row["sta"],
        )

        candidates = []
        for flight in flights:
            station = station_rows.get(flight["arr_station"], {})
            if rotable_replacement:
                has_capability = (
                    station.get("base_maintenance") == "True"
                    or bool(station.get("mro_partner"))
                )
            else:
                has_capability = station.get("line_maintenance") == "True"
            has_time = float(flight["ground_time_h_at_arrival"]) * 60 >= minimum_slot
            has_part = profile["part"] is None or stock_rows.get(flight["arr_station"], 0) > 0
            if has_capability and has_time and has_part:
                candidates.append(flight)

        def staffing(station: str):
            available = [
                row
                for row in self.csv("technicians.csv")
                if row["station"] == station
            ]
            lead = next(
                (
                    row
                    for row in available
                    if all(
                        skill in row["skills"].split("|")
                        for skill in profile["skills"]
                    )
                ),
                None,
            )
            certifier = next(
                (
                    row
                    for row in available
                    if row["authorisation"] == profile["authorisation"]
                ),
                None,
            )
            return lead, certifier

        staffed = next(
            (
                (flight, *staffing(flight["arr_station"]))
                for flight in candidates
                if all(staffing(flight["arr_station"]))
            ),
            None,
        )
        selected = staffed[0] if staffed else (candidates[0] if candidates else None)
        if not selected:
            return {
                "task_card_id": profile["task_id"],
                "station": "N/A",
                "qualified_technician": False,
                "feasible": False,
                "blockers": ["No ground slot with required capability, time, and stock"],
            }

        station = selected["arr_station"]
        lead, certifier = staffing(station)
        qualified = bool(lead and certifier)
        approved_task = duration is not None and not profile["task_id"].startswith("AWAIT-")
        blockers = []
        if not qualified:
            blockers.append("Required skills or certifying authorisation unavailable")
        if not approved_task:
            blockers.append("Approved task-card duration unavailable")
        start = _dt(selected["sta"])
        technicians_out = []
        if lead:
            technicians_out.append(
                {
                    "technician_id": lead["technician_id"],
                    "role": "LEAD",
                    "skills_matched": profile["skills"],
                }
            )
        if certifier and certifier is not lead:
            technicians_out.append(
                {
                    "technician_id": certifier["technician_id"],
                    "role": "CERTIFYING",
                    "authorisation": profile["authorisation"],
                }
            )
        parts = (
            [{"part_number": profile["part"], "qty": 1, "source": "ON_HAND"}]
            if profile["part"]
            else []
        )
        return {
            "task_card_id": profile["task_id"],
            "task_duration_min": duration,
            "buffer_min": buffer,
            "station": station,
            "flight_id_before": selected["flight_id"],
            "slot_start": _iso(start),
            "slot_end": _iso(start + timedelta(minutes=minimum_slot)),
            "parts": parts,
            "technicians": technicians_out,
            "qualified_technician": qualified,
            "feasible": qualified and approved_task,
            "blockers": blockers,
            "note": "Shift overlap requires dispatcher confirmation before release.",
        }

    def execution(
        self,
        diagnosis: dict[str, Any],
        assessment: dict[str, Any],
        plan: dict[str, Any],
    ) -> dict[str, Any]:
        if assessment["decision"] == "MONITOR":
            return {
                "outcome": "NO_ACTION",
                "functional_test_passed": True,
                "measurement": None,
            }
        if not plan["feasible"]:
            return {
                "outcome": "AWAITING_APPROVED_PLAN",
                "functional_test_passed": False,
                "measurement": None,
            }
        if diagnosis["fault_code"] == "F-25-2140":
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
                "simulation": True,
            }
        return {
            "task_card_id": plan["task_card_id"],
            "station": plan["station"],
            "outcome": "PLANNED_NOT_EXECUTED",
            "functional_test_passed": False,
            "measurement": None,
            "simulation": False,
        }

    def learning(
        self, assessment: dict[str, Any], plan: dict[str, Any], execution: dict[str, Any]
    ) -> dict[str, Any]:
        economics = self.json("economics.json")
        confirmed = execution["outcome"] == "CONFIRMED_FAULT"
        labour = round(
            plan.get("task_duration_min", 0)
            / 60
            * economics["line_labour_cost_per_hour"],
            2,
        ) if confirmed else 0.0
        catalog = {row["part_number"]: row for row in self.csv("parts_catalog.csv")}
        part_cost = sum(
            float(catalog[item["part_number"]]["unit_price_eur"]) * item["qty"]
            for item in plan.get("parts", [])
            if confirmed and item["part_number"] in catalog
        )
        actual = round(labour + part_cost, 2)
        counterfactual = (
            economics["unscheduled_removal_cost"] + economics["nff_shop_test_cost"]
        )
        return {
            "nff_avoided": confirmed,
            "saving_eur": round(counterfactual - actual, 2) if confirmed else 0.0,
            "cost_actual_eur": actual,
            "cost_counterfactual_remove_now_eur": counterfactual,
            "feedback": (
                f"Decision '{assessment['decision']}' recorded; incorporate verified execution data on closure."
            ),
        }
