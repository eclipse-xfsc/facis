import json
import sys
import unittest
from pathlib import Path


SUBMISSION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUBMISSION_ROOT))

from workflow import DEFAULT_CASE_ID, parse_request_body, run_workflow  # noqa: E402


class WorkflowTests(unittest.TestCase):
    def test_default_request_runs_all_five_stages(self):
        response = run_workflow(run_id="test-run")

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

    def test_known_case_is_loaded_from_repository_data(self):
        response = run_workflow({"case_id": "CASE-2026-0004"}, run_id="test-run")

        self.assertEqual(response["final_submission"]["seat_id"], "D-AXFD-4K")
        self.assertEqual(
            response["final_submission"]["diagnosis"]["fault_code"], "F-25-2166"
        )

    def test_unknown_case_returns_degraded_contract_response(self):
        response = run_workflow(
            {"case_id": "CASE-DOES-NOT-EXIST", "seat_id": "UNKNOWN-SEAT"},
            run_id="test-run",
        )

        self.assertTrue(response["degraded"])
        self.assertEqual(
            response["final_submission"]["case_id"], "CASE-DOES-NOT-EXIST"
        )
        self.assertEqual(len(response["trace"]), 5)

    def test_malformed_json_degrades_to_reference_case(self):
        payload, errors = parse_request_body(b"{bad json")
        response = run_workflow(payload, request_errors=errors, run_id="test-run")

        self.assertTrue(response["degraded"])
        self.assertEqual(response["final_submission"]["case_id"], DEFAULT_CASE_ID)

    def test_non_object_json_is_rejected_safely(self):
        payload, errors = parse_request_body(json.dumps([1, 2, 3]).encode())

        self.assertEqual(payload, {})
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
