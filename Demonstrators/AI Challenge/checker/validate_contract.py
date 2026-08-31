#!/usr/bin/env python3
"""
Offline contract validator - The Airbus AI Challenge, powered by FACIS (contract v1.1).

    python3 validate_contract.py result.json [expected_case_id]
    python3 validate_contract.py https://.../api/airbus-challenge/<name>/run [case_id] [seat_id]

URL mode POSTs {"case_id": ..., "seat_id": ...} (or {} if omitted) to your endpoint.
Checks: five ordered stages, complete final_submission, non-empty grounded evidence_ids,
and - when a case is given - that final_submission.case_id echoes the requested case.
Exit code 0 = valid, 1 = violations found.
"""
import json, sys, urllib.request

ORDER = ["diagnosis","nff_assessment","repair_plan","execution","outcome_learning"]
ALIAS_STAGE, ALIAS_OUT = ("stage","agent","name"), ("output","result","payload")
MIN_FIELDS = {
    "diagnosis": ["fault_code","leading_cause"],
    "nff_assessment": ["nff_risk","decision"],
    "repair_plan": ["task_card_id","station"],
    "execution": ["outcome","functional_test_passed"],
    "outcome_learning": ["nff_avoided","saving_eur"],
}
def get(d, keys):
    for k in keys:
        if isinstance(d, dict) and k in d: return d[k]
    return None

def validate(doc, expected_case=None):
    errs = []
    if not isinstance(doc, dict): return ["response is not a JSON object"]
    for k in ("team_id","run_id"):
        if not doc.get(k): errs.append(f"missing {k}")
    trace = doc.get("trace")
    if not isinstance(trace, list) or len(trace) != 5:
        errs.append(f"trace must be a list of exactly 5 stages (got {len(trace) if isinstance(trace,list) else type(trace).__name__})")
        trace = trace if isinstance(trace, list) else []
    for i, item in enumerate(trace):
        want = ORDER[i] if i < 5 else "?"
        stage = get(item, ALIAS_STAGE)
        if isinstance(stage, int): stage = ORDER[stage-1] if 1 <= stage <= 5 else stage
        if stage != want: errs.append(f"trace[{i}]: stage '{stage}' != expected '{want}'")
        if item.get("status") != "complete": errs.append(f"trace[{i}]: status != complete")
        out = get(item, ALIAS_OUT)
        if not isinstance(out, dict) or not out: errs.append(f"trace[{i}]: empty or missing output")
    fs = doc.get("final_submission")
    if not isinstance(fs, dict):
        errs.append("missing final_submission"); fs = {}
    for sec, fields in MIN_FIELDS.items():
        block = fs.get(sec)
        if not isinstance(block, dict):
            errs.append(f"final_submission.{sec} missing"); continue
        for f in fields:
            if f not in block: errs.append(f"final_submission.{sec}.{f} missing")
    ev = fs.get("evidence_ids")
    if not isinstance(ev, list) or not ev or not all(isinstance(x, str) and x.strip() for x in ev):
        errs.append("final_submission.evidence_ids must be a NON-EMPTY list of artifact references (contract v1.1)")
    if not fs.get("case_id"):
        errs.append("final_submission.case_id missing (must echo the requested case)")
    elif expected_case and fs["case_id"] != expected_case:
        errs.append(f"case echo mismatch: answered '{fs['case_id']}' for requested '{expected_case}'")
    ints = fs.get("integrations")
    if not isinstance(ints, dict) or not all(isinstance(ints.get(k), bool) for k in ("ai_iot","dcm","partner_onboarding")):
        errs.append("final_submission.integrations must hold booleans ai_iot/dcm/partner_onboarding")
    return errs

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    src = sys.argv[1]; case = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        if src.startswith("http"):
            body = {}
            if case: body["case_id"] = case
            if len(sys.argv) > 3: body["seat_id"] = sys.argv[3]
            req = urllib.request.Request(src, data=json.dumps(body).encode(),
                                         headers={"Content-Type":"application/json"}, method="POST")
            import time as _t; t0 = _t.time()
            raw = urllib.request.urlopen(req, timeout=30).read()
            if _t.time() - t0 > 30:
                print("INVALID - endpoint took longer than 30 s (contract v1.1)"); sys.exit(1)
            doc = json.loads(raw)
        else:
            doc = json.load(open(src, encoding="utf8"))
    except json.JSONDecodeError:
        print("INVALID - response/file is not valid JSON (contract v1.1: always return valid JSON)"); sys.exit(1)
    except FileNotFoundError:
        print("INVALID - file not found:", src); sys.exit(1)
    except Exception as ex:
        print(f"INVALID - endpoint did not answer within 30 s or refused the connection ({type(ex).__name__}) - contract v1.1"); sys.exit(1)
    errs = validate(doc, expected_case=case)
    if errs:
        print("INVALID -", len(errs), "violation(s):")
        for e in errs: print("  -", e)
        sys.exit(1)
    print("VALID - 5 ordered stages, grounded evidence, case echoed. Ready for the runner.")
if __name__ == "__main__":
    main()
