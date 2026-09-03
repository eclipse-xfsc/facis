#!/usr/bin/env python3
"""Contract-valid Thin Slice 1 workflow for the Airbus AI Challenge.

The five classes are deliberately simple walking-skeleton agents. Their stable
``run(state)`` interface lets us replace each implementation with an LLM-backed
LangGraph node in later slices without changing the HTTP contract.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Protocol, TypedDict


TEAM_ID = "TEAM-THIN-SLICE-MVP"
DEFAULT_CASE_ID = "CASE-2026-0002"
DEFAULT_SEAT_ID = "D-AXFB-1K"
CHALLENGE_ROOT = Path(__file__).resolve().parents[4]
CASES_PATH = CHALLENGE_ROOT / "data" / "cases_seed.json"


class WorkflowState(TypedDict, total=False):
    case_id: str
    seat_id: str
    case_record: dict[str, Any] | None
    degraded: bool
    errors: list[str]
    trace: list[dict[str, Any]]
    diagnosis: dict[str, Any]
    nff_assessment: dict[str, Any]
    repair_plan: dict[str, Any]
    execution: dict[str, Any]
    outcome_learning: dict[str, Any]


class Agent(Protocol):
    stage: str
    number: int

    def run(self, state: WorkflowState) -> None: ...


def _append_stage(state: WorkflowState, agent: Agent, output: dict[str, Any]) -> None:
    state[agent.stage] = output
    state["trace"].append(
        {
            "stage": agent.stage,
            "agent": agent.number,
            "status": "complete",
            "output": output,
        }
    )


class CaseRepository:
    """First real data tool: retrieve a seeded case by its identifier."""

    def __init__(self, cases_path: Path = CASES_PATH) -> None:
        self.cases_path = cases_path

    def find(self, case_id: str) -> dict[str, Any] | None:
        with self.cases_path.open(encoding="utf-8") as stream:
            cases = json.load(stream)
        return next((case for case in cases if case["case_id"] == case_id), None)


class DiagnosisAgent:
    stage, number = "diagnosis", 1

    def run(self, state: WorkflowState) -> None:
        case = state["case_record"]
        fault_code = case.get("fault_code") if case else None
        cause = (
            f"Thin Slice 1 placeholder: investigate evidence for {fault_code}"
            if fault_code
            else "No seeded case found; diagnosis requires additional evidence"
        )
        _append_stage(
            state,
            self,
            {
                "fault_code": fault_code,
                "leading_cause": cause,
                "confidence": 0.0,
                "evidence": ["data/cases_seed.json"],
            },
        )


class NffAssessmentAgent:
    stage, number = "nff_assessment", 2

    def run(self, state: WorkflowState) -> None:
        _append_stage(
            state,
            self,
            {
                "nff_risk": 0.5,
                "decision": "MONITOR",
                "decision_rule": "Thin Slice 1 safe placeholder pending evidence analysis",
                "citations": ["OPS-NFF-01"],
            },
        )


class RepairPlanningAgent:
    stage, number = "repair_plan", 3

    def run(self, state: WorkflowState) -> None:
        _append_stage(
            state,
            self,
            {
                "task_card_id": "NONE",
                "station": "N/A",
                "feasible": True,
                "blockers": [],
            },
        )


class ExecutionAgent:
    stage, number = "execution", 4

    def run(self, state: WorkflowState) -> None:
        _append_stage(
            state,
            self,
            {
                "outcome": "NO_ACTION",
                "functional_test_passed": True,
                "measurement": None,
            },
        )


class LearningAgent:
    stage, number = "outcome_learning", 5

    def run(self, state: WorkflowState) -> None:
        _append_stage(
            state,
            self,
            {
                "nff_avoided": False,
                "saving_eur": 0.0,
                "feedback": "Thin Slice 1 completed; replace placeholders with grounded reasoning",
            },
        )


AGENTS: tuple[Agent, ...] = (
    DiagnosisAgent(),
    NffAssessmentAgent(),
    RepairPlanningAgent(),
    ExecutionAgent(),
    LearningAgent(),
)


def parse_request_body(raw: bytes) -> tuple[dict[str, Any], list[str]]:
    """Parse input while preserving the contract's graceful-degradation rule."""
    if not raw.strip():
        return {}, []
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}, ["Request body was not valid JSON; using the reference case"]
    if not isinstance(payload, dict):
        return {}, ["Request JSON was not an object; using the reference case"]
    return payload, []


def run_workflow(
    payload: dict[str, Any] | None = None,
    *,
    request_errors: list[str] | None = None,
    repository: CaseRepository | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    payload = payload or {}
    errors = list(request_errors or [])

    case_id = payload.get("case_id", DEFAULT_CASE_ID)
    if not isinstance(case_id, str) or not case_id.strip():
        errors.append("case_id must be a non-empty string; using the reference case")
        case_id = DEFAULT_CASE_ID

    repository = repository or CaseRepository()
    case = repository.find(case_id)
    if case is None:
        errors.append(f"Unknown case_id: {case_id}")

    default_seat = case.get("seat_id") if case else "UNKNOWN"
    seat_id = payload.get("seat_id", default_seat)
    if not isinstance(seat_id, str) or not seat_id.strip():
        errors.append("seat_id must be a non-empty string; using the case default")
        seat_id = default_seat
    if case and seat_id != case["seat_id"]:
        errors.append(f"seat_id {seat_id} does not match {case_id}")

    state: WorkflowState = {
        "case_id": case_id,
        "seat_id": seat_id,
        "case_record": case,
        "degraded": bool(errors),
        "errors": errors,
        "trace": [],
    }
    for agent in AGENTS:
        agent.run(state)

    final_submission = {
        "team_id": TEAM_ID,
        "case_id": case_id,
        "seat_id": seat_id,
        "diagnosis": state["diagnosis"],
        "nff_assessment": state["nff_assessment"],
        "evidence_ids": ["data/cases_seed.json", "OPS-NFF-01"],
        "repair_plan": state["repair_plan"],
        "execution": state["execution"],
        "outcome_learning": state["outcome_learning"],
        "integrations": {
            "ai_iot": False,
            "dcm": False,
            "partner_onboarding": False,
        },
    }
    response = {
        "team_id": TEAM_ID,
        "run_id": run_id or f"mvp-{int(time.time())}-{uuid.uuid4().hex[:8]}",
        "trace": state["trace"],
        "final_submission": final_submission,
    }
    if errors:
        response["degraded"] = True
        response["errors"] = errors
    return response


if __name__ == "__main__":
    print(json.dumps(run_workflow(run_id="mvp-local-preview"), indent=2))
