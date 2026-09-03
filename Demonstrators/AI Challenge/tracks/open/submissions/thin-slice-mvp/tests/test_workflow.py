import json
import sys
import unittest
from pathlib import Path


SUBMISSION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUBMISSION_ROOT))

from workflow import DEFAULT_CASE_ID, parse_request_body, run_workflow  # noqa: E402


class FakeLLM:
    model = "test-model"

    def __init__(self):
        self.calls = []

    def reason(self, stage, role, facts, fallback):
        self.calls.append((stage, role, facts))
        return {"text": f"Grounded {stage} rationale", "source": "test-llm"}


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


if __name__ == "__main__":
    unittest.main()
