import json
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path


SUBMISSION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUBMISSION_ROOT))

from workflow import (  # noqa: E402
    DEFAULT_CASE_ID,
    degraded_response,
    parse_request_body,
    run_workflow,
)
from llm import OllamaClient  # noqa: E402
import observability  # noqa: E402


class RecordingSpan:
    def __init__(self, name):
        self.name = name
        self.attributes = {}

    def set_attribute(self, key, value):
        self.attributes[key] = value


class RecordingTracer:
    def __init__(self):
        self.spans = []

    @contextmanager
    def start_as_current_span(self, name):
        span = RecordingSpan(name)
        self.spans.append(span)
        yield span


class FakeLLM:
    model = "test-model"

    def __init__(self):
        self.calls = []

    def analyze(
        self, stage, role, facts, evidence_ids, recommendations, fallback
    ):
        self.calls.append(
            (stage, role, facts, evidence_ids, recommendations, fallback)
        )
        return {"data": fallback, "source": "test-llm", "validation": "passed"}


class DissentingLLM(FakeLLM):
    def analyze(
        self, stage, role, facts, evidence_ids, recommendations, fallback
    ):
        result = super().analyze(
            stage, role, facts, evidence_ids, recommendations, fallback
        )
        result["data"] = dict(fallback, recommendation=recommendations[-1])
        return result


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.llm = FakeLLM()

    def test_default_request_runs_all_five_stages(self):
        response = run_workflow(run_id="test-run", llm=self.llm)

        self.assertEqual(response["final_submission"]["case_id"], DEFAULT_CASE_ID)
        self.assertEqual(
            [stage["stage"] for stage in response["trace"]],
            [
                "diagnosis",
                "nff_assessment",
                "repair_plan",
                "execution",
                "outcome_learning",
            ],
        )
        self.assertTrue(all(stage["status"] == "complete" for stage in response["trace"]))
        self.assertEqual(len(self.llm.calls), 5)
        self.assertTrue(
            all(stage["output"]["reasoning_source"] == "test-llm" for stage in response["trace"])
        )
        self.assertTrue(all(stage["tool_calls"] for stage in response["trace"]))
        self.assertTrue(
            all(stage["output"]["retrieved_evidence"] for stage in response["trace"])
        )
        self.assertTrue(
            all(call[2]["retrieved_manual_chunks"] for call in self.llm.calls)
        )

    def test_reference_case_is_grounded_in_all_data_tools(self):
        result = run_workflow(run_id="test-run", llm=self.llm)["final_submission"]

        self.assertEqual(result["diagnosis"]["trend"]["vibration_phase_share"], 0.973)
        self.assertEqual(result["nff_assessment"]["history"], {"similar_cases": 19, "nff_cases": 9})
        self.assertEqual(result["repair_plan"]["flight_id_before"], "FD4018")
        self.assertEqual(result["repair_plan"]["station"], "FRA")
        self.assertEqual(result["outcome_learning"]["saving_eur"], 5029.17)

    def test_known_case_is_loaded_from_repository_data(self):
        response = run_workflow(
            {"case_id": "CASE-2026-0004"}, run_id="test-run", llm=self.llm
        )

        self.assertEqual(response["final_submission"]["seat_id"], "D-AXFD-4K")
        self.assertEqual(
            response["final_submission"]["diagnosis"]["fault_code"], "F-25-2166"
        )

    def test_all_seeded_faults_get_supported_decisions(self):
        expected = {
            "CASE-2026-0001": ("REPLACE_COMPONENT", "TASK-25-21-ACT-REPLACE"),
            "CASE-2026-0002": ("CONNECTOR_TASK", "TASK-25-21-CAN-RESEAT"),
            "CASE-2026-0003": ("DEFER_PER_MEL", "TSM-23-34-20"),
            "CASE-2026-0004": ("REPLACE_COMPONENT", "AWAIT-APPROVED-USB-PD-TASK"),
            "CASE-2026-0005": ("REPLACE_COMPONENT", "TSM-25-21-88"),
        }
        for case_id, (decision, task_id) in expected.items():
            with self.subTest(case_id=case_id):
                result = run_workflow(
                    {"case_id": case_id}, run_id="test-run", llm=FakeLLM()
                )["final_submission"]
                self.assertEqual(result["nff_assessment"]["decision"], decision)
                self.assertEqual(result["repair_plan"]["task_card_id"], task_id)

    def test_known_seat_without_open_case_is_monitored(self):
        response = run_workflow(
            {"case_id": DEFAULT_CASE_ID, "seat_id": "D-AXFB-1A"},
            run_id="test-run",
            llm=self.llm,
        )
        result = response["final_submission"]

        self.assertNotIn("degraded", response)
        self.assertEqual(result["nff_assessment"]["decision"], "MONITOR")
        self.assertEqual(result["repair_plan"]["task_card_id"], "NONE")
        self.assertEqual(result["execution"]["outcome"], "NO_ACTION")
        self.assertTrue(result["execution"]["functional_test_passed"])

    def test_unknown_case_returns_degraded_contract_response(self):
        response = run_workflow(
            {"case_id": "CASE-DOES-NOT-EXIST", "seat_id": "UNKNOWN-SEAT"},
            run_id="test-run",
            llm=self.llm,
        )

        self.assertTrue(response["degraded"])
        self.assertEqual(
            response["final_submission"]["case_id"], "CASE-DOES-NOT-EXIST"
        )
        self.assertEqual(len(response["trace"]), 5)

    def test_malformed_json_degrades_to_reference_case(self):
        payload, errors = parse_request_body(b"{bad json")
        response = run_workflow(
            payload, request_errors=errors, run_id="test-run", llm=self.llm
        )

        self.assertTrue(response["degraded"])
        self.assertEqual(response["final_submission"]["case_id"], DEFAULT_CASE_ID)

    def test_non_object_json_is_rejected_safely(self):
        payload, errors = parse_request_body(json.dumps([1, 2, 3]).encode())

        self.assertEqual(payload, {})
        self.assertTrue(errors)

    def test_last_resort_response_does_not_reenter_workflow(self):
        response = degraded_response(
            {"case_id": "CASE-BROKEN", "seat_id": "SEAT-BROKEN"},
            errors=["simulated failure"],
            run_id="degraded-test",
        )

        self.assertTrue(response["degraded"])
        self.assertEqual(response["final_submission"]["case_id"], "CASE-BROKEN")
        self.assertEqual(len(response["trace"]), 5)

    def test_exhausted_llm_budget_falls_back_without_network_call(self):
        client = OllamaClient(total_budget=0.01, enabled=True)

        fallback = {
            "analysis": "Approved fallback",
            "selected_evidence": ["data/test.json"],
            "recommendation": "MONITOR",
        }
        result = client.analyze(
            "diagnosis",
            "test role",
            {"fact": True},
            ["data/test.json"],
            ["MONITOR"],
            fallback,
        )

        self.assertEqual(result["data"], fallback)
        self.assertEqual(result["source"], "deterministic_fallback:budget")

    def test_policy_guard_overrides_dissenting_llm_recommendation(self):
        result = run_workflow(run_id="test-run", llm=DissentingLLM())[
            "final_submission"
        ]["nff_assessment"]

        self.assertEqual(result["decision"], "CONNECTOR_TASK")
        self.assertEqual(result["effective_recommendation"], "CONNECTOR_TASK")
        self.assertEqual(result["llm_recommendation"], "MONITOR")
        self.assertEqual(result["guardrail_status"], "recommendation_overridden")

    def test_semantic_guard_rejects_boolean_contradiction(self):
        facts = {"trend": {"monotonic_degradation": False}}

        self.assertTrue(
            OllamaClient._contradicts_facts(
                "The signal shows monotonic degradation.", facts
            )
        )
        self.assertFalse(
            OllamaClient._contradicts_facts(
                "The signal is non-monotonic.", facts
            )
        )

    def test_observability_records_request_agents_tools_and_llm(self):
        tracer = RecordingTracer()
        previous = (
            observability._tracer,
            observability._initialized,
            observability._initialization_error,
        )
        observability._tracer = tracer
        observability._initialized = True
        observability._initialization_error = None
        try:
            run_workflow(run_id="observable-run", llm=self.llm)
        finally:
            (
                observability._tracer,
                observability._initialized,
                observability._initialization_error,
            ) = previous

        names = [span.name for span in tracer.spans]
        self.assertEqual(names[0], "facis.workflow.request")
        self.assertEqual(sum(name.startswith("agent.") for name in names), 5)
        self.assertEqual(names.count("manual_retriever.search"), 5)
        self.assertEqual(names.count("ollama.analyze"), 5)
        self.assertEqual(names.count("policy_guard.validate"), 5)
        self.assertIn("telemetry.analyse_signal", names)
        self.assertTrue(
            all("openinference.span.kind" in span.attributes for span in tracer.spans)
        )


if __name__ == "__main__":
    unittest.main()
