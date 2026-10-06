#!/usr/bin/env python3
"""Observable LangGraph orchestration with five local-LLM agents."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from challenge_tools import ChallengeData
from llm import OllamaClient, ReasoningClient
from observability import observed_span, set_span_attribute, set_span_output, trace_reference


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
    def build(self, state: WorkflowState) -> dict[str, Any]:
        raise NotImplementedError

    def fallback_analyses(self, output: dict[str, Any]) -> list[str]:
        return ["The grounded tool output supports this stage result."]

    def retrieval_query(self, output: dict[str, Any]) -> str:
        return f"{self.stage} aircraft maintenance"

    def expected_recommendation(self, output: dict[str, Any]) -> str:
        return "ACCEPT_TOOL_RESULT"

    def allowed_recommendations(self, output: dict[str, Any]) -> list[str]:
        return [self.expected_recommendation(output), "COLLECT_MORE_EVIDENCE"]

    def tool_calls(self, output: dict[str, Any]) -> list[dict[str, Any]]:
        return []

    def __call__(self, state: WorkflowState) -> dict[str, Any]:
        with observed_span(
            f"agent.{self.stage}",
            "AGENT",
            input_value={"case_id": state["case_id"], "seat_id": state["seat_id"]},
            attributes={"facis.agent.number": self.number, "facis.agent.role": self.role},
        ) as agent_span:
            result = self._process(state)
            set_span_output(agent_span, result[self.stage])
            return result

    def _process(self, state: WorkflowState) -> dict[str, Any]:
        output = self.build(state)
        tool_calls = self.tool_calls(output)
        for call in tool_calls:
            with observed_span(
                call["tool"],
                "TOOL",
                input_value=call.get("input", {"stage": self.stage}),
                attributes={"facis.stage": self.stage},
            ) as tool_span:
                set_span_output(tool_span, call.get("output"))

        query = self.retrieval_query(output)
        with observed_span(
            "manual_retriever.search",
            "RETRIEVER",
            input_value={"query": query, "top_k": 2},
            attributes={"facis.stage": self.stage},
        ) as retrieval_span:
            retrieved = state["data"].search_manuals(query, top_k=2)
            set_span_output(retrieval_span, retrieved)
        retrieved_ids = [item["chunk_id"] for item in retrieved]
        evidence_ids = list(
            dict.fromkeys(
                output.get("evidence", [])
                + output.get("citations", [])
                + retrieved_ids
            )
        )
        if not evidence_ids:
            evidence_ids = ["data/cases_seed.json"]
        facts = self._compact_facts(output)
        facts["retrieved_manual_chunks"] = retrieved
        expected = self.expected_recommendation(output)
        recommendations = self.allowed_recommendations(output)
        with observed_span(
            "ollama.analyze",
            "LLM",
            input_value={
                "stage": self.stage,
                "role": self.role,
                "facts": facts,
                "evidence_ids": evidence_ids,
                "recommendations": recommendations,
            },
            attributes={"llm.model_name": state["llm"].model, "facis.stage": self.stage},
        ) as llm_span:
            reasoning = state["llm"].analyze(
                self.stage,
                self.role,
                facts,
                evidence_ids,
                recommendations,
                {
                    "analysis": self.fallback_analyses(output)[0],
                    "selected_evidence": evidence_ids[:1],
                    "recommendation": expected,
                },
            )
            set_span_output(llm_span, reasoning)
        agent_data = reasoning["data"]
        output["agent_analysis"] = agent_data["analysis"]
        output["llm_recommendation"] = agent_data["recommendation"]
        output["effective_recommendation"] = expected
        output["selected_evidence"] = agent_data["selected_evidence"]
        output["retrieved_evidence"] = retrieved_ids
        output["reasoning_source"] = reasoning["source"]
        with observed_span(
            "policy_guard.validate",
            "GUARDRAIL",
            input_value={
                "llm_recommendation": agent_data["recommendation"],
                "expected_recommendation": expected,
            },
            attributes={"facis.stage": self.stage},
        ) as guard_span:
            output["guardrail_status"] = (
                reasoning["validation"]
                if agent_data["recommendation"] == expected
                else "recommendation_overridden"
            )
            set_span_attribute(
                guard_span, "facis.guardrail.status", output["guardrail_status"]
            )
            set_span_output(
                guard_span,
                {
                    "effective_recommendation": expected,
                    "status": output["guardrail_status"],
                },
            )
        stage_trace = {
            "stage": self.stage,
            "agent": self.number,
            "status": "complete",
            "tool_calls": tool_calls
            + [
                {
                    "tool": "manual_retriever.search",
                    "input": {"query": query, "top_k": 2},
                    "output": {"chunk_ids": retrieved_ids},
                }
            ],
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

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].diagnosis(state["case_record"], state["seat_id"])

    def fallback_analyses(self, output: dict[str, Any]) -> list[str]:
        if output["fault_code"] is None:
            return [
                f"{output['leading_cause']}; the safe diagnosis is no authorised repair.",
                "No active fault code is available for this seat.",
            ]
        return [
            f"{output['fault_code']} is most consistent with {output['leading_cause']}.",
            f"The diagnosis is backed by {len(output['evidence'])} grounded evidence references.",
        ]

    def retrieval_query(self, output: dict[str, Any]) -> str:
        trend = output.get("trend", {})
        return " ".join(
            str(value)
            for value in (
                output.get("fault_code", "healthy seat"),
                output["leading_cause"],
                trend.get("signal", "no fault monitoring"),
            )
        )

    def expected_recommendation(self, output: dict[str, Any]) -> str:
        return output["leading_cause"]

    def allowed_recommendations(self, output: dict[str, Any]) -> list[str]:
        return [output["leading_cause"], "COLLECT_MORE_EVIDENCE"]

    def tool_calls(self, output: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"tool": "case_repository.lookup", "output": {"fault_code": output["fault_code"]}},
            {"tool": "bite_events.lookup", "output": output["evidence"][:1]},
            {"tool": "telemetry.analyse_signal", "output": output["trend"]},
        ]


class NffAssessmentAgent(BaseAgent):
    stage, number, role = "nff_assessment", 2, "NFF policy assessor"

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].nff_assessment(state["diagnosis"])

    def fallback_analyses(self, output: dict[str, Any]) -> list[str]:
        history = output["history"]
        return [
            f"The {output['nff_risk']:.2f} NFF risk supports {output['decision']} under the cited policy.",
            f"History contains {history['nff_cases']} NFF outcomes among {history['similar_cases']} similar cases.",
        ]

    def retrieval_query(self, output: dict[str, Any]) -> str:
        return f"OPS-NFF-01 {output['decision']} {output['decision_rule']}"

    def expected_recommendation(self, output: dict[str, Any]) -> str:
        return output["decision"]

    def allowed_recommendations(self, output: dict[str, Any]) -> list[str]:
        return list(
            dict.fromkeys(
                [
                    output["decision"],
                    "CONNECTOR_TASK",
                    "REPLACE_COMPONENT",
                    "DEFER_PER_MEL",
                    "MONITOR",
                ]
            )
        )

    def tool_calls(self, output: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"tool": "maintenance_history.nff_rate", "output": output["history"]},
            {"tool": "nff_policy.apply", "output": {"decision": output["decision"]}},
        ]


class RepairPlanningAgent(BaseAgent):
    stage, number, role = "repair_plan", 3, "maintenance resource planner"

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].repair_plan(
            state["case_record"], state["nff_assessment"]
        )

    def fallback_analyses(self, output: dict[str, Any]) -> list[str]:
        if output["feasible"]:
            return [
                f"{output['task_card_id']} is feasible at {output['station']} with the selected resources.",
                f"The planned station is {output['station']} and no blockers remain.",
            ]
        return [
            f"{output['task_card_id']} is not yet feasible because {', '.join(output['blockers'])}.",
            "The plan remains blocked pending an approved and resourced maintenance task.",
        ]

    def retrieval_query(self, output: dict[str, Any]) -> str:
        task_id = output["task_card_id"].replace("TASK-", "TASKCARD-")
        return f"{task_id} ground time parts skills authorisation"

    def expected_recommendation(self, output: dict[str, Any]) -> str:
        return output["task_card_id"]

    def allowed_recommendations(self, output: dict[str, Any]) -> list[str]:
        return [output["task_card_id"], "DEFER_PER_MEL", "NO_ACTION"]

    def tool_calls(self, output: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"tool": "flight_schedule.find_ground_slot", "output": output.get("flight_id_before")},
            {"tool": "parts_stock.check", "output": output.get("parts", [])},
            {"tool": "technician_roster.match", "output": output.get("technicians", [])},
        ]


class ExecutionAgent(BaseAgent):
    stage, number, role = "execution", 4, "task-card execution supervisor"

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].execution(
            state["diagnosis"], state["nff_assessment"], state["repair_plan"]
        )

    def fallback_analyses(self, output: dict[str, Any]) -> list[str]:
        return [
            f"Execution outcome is {output['outcome']} and functional-test status is {output['functional_test_passed']}.",
            "Execution state reflects only the verified or explicitly simulated evidence available.",
        ]

    def retrieval_query(self, output: dict[str, Any]) -> str:
        task_id = output.get("task_card_id", "no action").replace(
            "TASK-", "TASKCARD-"
        )
        return f"{task_id} functional test acceptance"

    def expected_recommendation(self, output: dict[str, Any]) -> str:
        return output["outcome"]

    def allowed_recommendations(self, output: dict[str, Any]) -> list[str]:
        return [output["outcome"], "HOLD_FOR_VERIFICATION", "NO_ACTION"]

    def tool_calls(self, output: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"tool": "task_card.load", "output": output.get("task_card_id", "NONE")},
            {"tool": "execution_result.verify", "output": output.get("measurement")},
        ]


class LearningAgent(BaseAgent):
    stage, number, role = "outcome_learning", 5, "maintenance outcome analyst"

    def build(self, state: WorkflowState) -> dict[str, Any]:
        return state["data"].learning(
            state["nff_assessment"], state["repair_plan"], state["execution"]
        )

    def fallback_analyses(self, output: dict[str, Any]) -> list[str]:
        return [
            f"Recorded NFF saving is EUR {output['saving_eur']:.2f} from the configured cost model.",
            f"NFF avoidance is recorded as {output['nff_avoided']} until verified closure data is available.",
        ]

    def retrieval_query(self, output: dict[str, Any]) -> str:
        return "OPS-NFF-01 removal shop test cost learning"

    def expected_recommendation(self, output: dict[str, Any]) -> str:
        return "INCORPORATE_ON_CLOSURE"

    def allowed_recommendations(self, output: dict[str, Any]) -> list[str]:
        return ["INCORPORATE_ON_CLOSURE", "MONITOR_TREND"]

    def tool_calls(self, output: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "tool": "economics.calculate",
                "output": {
                    "nff_avoided": output["nff_avoided"],
                    "saving_eur": output["saving_eur"],
                },
            }
        ]


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


def degraded_response(
    payload: dict[str, Any] | None = None,
    *,
    errors: list[str] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Return a contract-valid response without touching data, LangGraph, or Ollama."""
    payload = payload if isinstance(payload, dict) else {}
    case_id = payload.get("case_id", DEFAULT_CASE_ID)
    if not isinstance(case_id, str) or not case_id.strip():
        case_id = DEFAULT_CASE_ID
    seat_id = payload.get("seat_id", "UNKNOWN")
    if not isinstance(seat_id, str) or not seat_id.strip():
        seat_id = "UNKNOWN"
    outputs = {
        "diagnosis": {
            "fault_code": None,
            "leading_cause": "Workflow unavailable; no diagnosis authorised",
        },
        "nff_assessment": {"nff_risk": 0.0, "decision": "MONITOR"},
        "repair_plan": {"task_card_id": "NONE", "station": "N/A"},
        "execution": {"outcome": "NO_ACTION", "functional_test_passed": True},
        "outcome_learning": {"nff_avoided": False, "saving_eur": 0.0},
    }
    trace = [
        {
            "stage": agent.stage,
            "agent": agent.number,
            "status": "complete",
            "output": outputs[agent.stage],
        }
        for agent in AGENTS
    ]
    return {
        "team_id": TEAM_ID,
        "run_id": run_id or f"degraded-{int(time.time())}-{uuid.uuid4().hex[:8]}",
        "trace": trace,
        "degraded": True,
        "errors": errors or ["Workflow unavailable"],
        "final_submission": {
            "team_id": TEAM_ID,
            "case_id": case_id,
            "seat_id": seat_id,
            **outputs,
            "evidence_ids": ["degraded:workflow-unavailable"],
            "integrations": {
                "ai_iot": False,
                "dcm": False,
                "partner_onboarding": False,
            },
        },
    }


def _execute_workflow(
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
    requested_case = data.find_case(case_id)
    if requested_case is None:
        errors.append(f"Unknown case_id: {case_id}")

    default_seat = requested_case.get("seat_id") if requested_case else "UNKNOWN"
    seat_id = payload.get("seat_id", default_seat)
    if not isinstance(seat_id, str) or not seat_id.strip():
        errors.append("seat_id must be a non-empty string; using the case default")
        seat_id = default_seat
    case = requested_case
    if requested_case and seat_id != requested_case["seat_id"]:
        seat = data.find_seat(seat_id)
        other_case = data.find_case_by_seat(seat_id)
        if seat and other_case is None:
            case = data.healthy_case(case_id, seat)
        else:
            errors.append(f"seat_id {seat_id} does not match {case_id}")
            case = None

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


def run_workflow(
    payload: dict[str, Any] | None = None,
    *,
    request_errors: list[str] | None = None,
    data: ChallengeData | None = None,
    llm: ReasoningClient | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    resolved_run_id = run_id or f"mvp-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    with observed_span(
        "facis.workflow.request",
        "CHAIN",
        input_value=payload or {},
        attributes={
            "facis.run_id": resolved_run_id,
            "facis.case_id": (payload or {}).get("case_id", DEFAULT_CASE_ID),
        },
    ) as workflow_span:
        response = _execute_workflow(
            payload,
            request_errors=request_errors,
            data=data,
            llm=llm,
            run_id=resolved_run_id,
        )
        reference = trace_reference(workflow_span)
        if reference:
            response["observability"] = reference
        set_span_attribute(
            workflow_span,
            "facis.degraded",
            response.get("degraded", False),
        )
        set_span_output(workflow_span, response)
        return response


if __name__ == "__main__":
    print(json.dumps(run_workflow(run_id="mvp-local-preview"), indent=2))
