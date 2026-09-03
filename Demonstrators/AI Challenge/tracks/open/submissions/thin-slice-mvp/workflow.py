#!/usr/bin/env python3
"""Thin Slice 2: LangGraph orchestration with five local-LLM agents."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from challenge_tools import ChallengeData
from llm import OllamaClient, ReasoningClient


TEAM_ID = "TEAM-THIN-SLICE-MVP"
DEFAULT_CASE_ID = "CASE-2026-0002"
CHALLENGE_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = CHALLENGE_ROOT / "data"


class WorkflowState(TypedDict, total=False):
    case_id: str
    seat_id: str
    case_record: Optional[dict[str, Any]]
    degraded: bool
    errors: list[str]
    trace: list[dict[str, Any]]
    data: ChallengeData
    llm: ReasoningClient
    diagnosis: dict[str, Any]
    nff_assessment: dict[str, Any]
    repair_plan: dict[str, Any]
    execution: dict[str, Any]
    outcome_learning: dict[str, Any]


class BaseAgent:
    stage = ""
    number = 0
    role = ""
    fallback = "Grounded tool output accepted."

    def build(self, state: WorkflowState) -> dict[str, Any]:
        raise NotImplementedError

    def __call__(self, state: WorkflowState) -> dict[str, Any]:
        output = self.build(state)
        reasoning = state["llm"].reason(
            self.stage, self.role, self._compact_facts(output), self.fallback
        )
        output["agent_rationale"] = reasoning["text"]
        output["reasoning_source"] = reasoning["source"]
        stage_trace = {
            "stage": self.stage,
            "agent": self.number,
            "status": "complete",
            "output": output,
        }
        return {self.stage: output, "trace": state["trace"] + [stage_trace]}

    @staticmethod
    def _compact_facts(output: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in output.items()
            if key not in {"agent_rationale", "reasoning_source"}
        }


class DiagnosisAgent(BaseAgent):
    stage, number, role = "diagnosis", 1, "diagnostic evidence analyst"
    fallback = "BITE and flight-phase telemetry support the tool-calculated leading cause."

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].diagnosis(state["case_record"], state["seat_id"])


class NffAssessmentAgent(BaseAgent):
    stage, number, role = "nff_assessment", 2, "NFF policy assessor"
    fallback = "Historical NFF rate and OPS-NFF-01 support the calculated decision."

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].nff_assessment(state["diagnosis"])


class RepairPlanningAgent(BaseAgent):
    stage, number, role = "repair_plan", 3, "maintenance resource planner"
    fallback = "The selected ground slot has sufficient time, stock, skills, and certification."

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].repair_plan(
            state["case_record"], state["nff_assessment"]
        )


class ExecutionAgent(BaseAgent):
    stage, number, role = "execution", 4, "task-card execution supervisor"
    fallback = "The simulated task result records an accepted measurement and functional test."

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].execution(state["repair_plan"])


class LearningAgent(BaseAgent):
    stage, number, role = "outcome_learning", 5, "maintenance outcome analyst"
    fallback = "The configured cost model shows the avoided NFF removal cost."

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].learning(
            state["nff_assessment"], state["repair_plan"], state["execution"]
        )


AGENTS = (
    DiagnosisAgent(),
    NffAssessmentAgent(),
    RepairPlanningAgent(),
    ExecutionAgent(),
    LearningAgent(),
)


def build_graph():
    builder = StateGraph(WorkflowState)
    for agent in AGENTS:
        builder.add_node(agent.stage, agent)
    builder.add_edge(START, AGENTS[0].stage)
    for current, following in zip(AGENTS, AGENTS[1:]):
        builder.add_edge(current.stage, following.stage)
    builder.add_edge(AGENTS[-1].stage, END)
    return builder.compile()


GRAPH = build_graph()


def parse_request_body(raw: bytes) -> tuple[dict[str, Any], list[str]]:
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
    data: ChallengeData | None = None,
    llm: ReasoningClient | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    payload = payload or {}
    errors = list(request_errors or [])
    data = data or ChallengeData(DATA_ROOT)

    case_id = payload.get("case_id", DEFAULT_CASE_ID)
    if not isinstance(case_id, str) or not case_id.strip():
        errors.append("case_id must be a non-empty string; using the reference case")
        case_id = DEFAULT_CASE_ID
    case = data.find_case(case_id)
    if case is None:
        errors.append(f"Unknown case_id: {case_id}")

    default_seat = case.get("seat_id") if case else "UNKNOWN"
    seat_id = payload.get("seat_id", default_seat)
    if not isinstance(seat_id, str) or not seat_id.strip():
        errors.append("seat_id must be a non-empty string; using the case default")
        seat_id = default_seat
    if case and seat_id != case["seat_id"]:
        errors.append(f"seat_id {seat_id} does not match {case_id}")

    state = GRAPH.invoke(
        {
            "case_id": case_id,
            "seat_id": seat_id,
            "case_record": case,
            "degraded": bool(errors),
            "errors": errors,
            "trace": [],
            "data": data,
            "llm": llm or OllamaClient(),
        }
    )
    diagnosis = state["diagnosis"]
    nff = state["nff_assessment"]
    plan = state["repair_plan"]
    execution = state["execution"]
    learning = state["outcome_learning"]
    evidence_ids = list(dict.fromkeys(diagnosis["evidence"] + nff["citations"]))
    response = {
        "team_id": TEAM_ID,
        "run_id": run_id or f"mvp-{int(time.time())}-{uuid.uuid4().hex[:8]}",
        "trace": state["trace"],
        "final_submission": {
            "team_id": TEAM_ID,
            "case_id": case_id,
            "seat_id": seat_id,
            "diagnosis": diagnosis,
            "nff_assessment": nff,
            "evidence_ids": evidence_ids,
            "repair_plan": plan,
            "execution": execution,
            "outcome_learning": learning,
            "integrations": {
                "ai_iot": False,
                "dcm": False,
                "partner_onboarding": False,
            },
        },
    }
    if errors:
        response["degraded"] = True
        response["errors"] = errors
    return response


if __name__ == "__main__":
    print(json.dumps(run_workflow(run_id="mvp-local-preview"), indent=2))
