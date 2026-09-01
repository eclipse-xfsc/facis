#!/usr/bin/env python3
"""Open-track starter: a contract-valid five-stage skeleton (stdlib only).
Run:  python3 skeleton.py   ->  POST http://localhost:8080/api/airbus-challenge/starter/run
It answers ANY case with placeholder logic - replace each agent_N() with real work over ../../data/.
"""
import json, time
from http.server import BaseHTTPRequestHandler, HTTPServer

def agent1(case, seat): return {"fault_code": None, "leading_cause": "TODO: derive from BITE + telemetry", "confidence": 0.5, "evidence": ["data/bite_events.jsonl"]}
def agent2(a1):        return {"nff_risk": 0.5, "decision": "MONITOR"}
def agent3(a2):        return {"task_card_id": "NONE", "station": "N/A", "feasible": True}
def agent4(a3):        return {"outcome": "NO_ACTION", "functional_test_passed": True}
def agent5(a4):        return {"nff_avoided": True, "saving_eur": 0.0, "feedback": "TODO"}

def run(case, seat):
    a1,a2 = agent1(case,seat), None
    a2,a3 = agent2(a1), None
    a3 = agent3(a2); a4 = agent4(a3); a5 = agent5(a4)
    stages = [("diagnosis",a1),("nff_assessment",a2),("repair_plan",a3),("execution",a4),("outcome_learning",a5)]
    return {"team_id":"TEAM-STARTER","run_id":f"starter-{int(time.time())}",
            "trace":[{"stage":n,"agent":i+1,"status":"complete","output":o} for i,(n,o) in enumerate(stages)],
            "final_submission":{"team_id":"TEAM-STARTER","case_id":case,"seat_id":seat,
              "diagnosis":a1,"nff_assessment":a2,"evidence_ids":a1["evidence"],
              "repair_plan":a3,"execution":a4,"outcome_learning":a5,
              "integrations":{"ai_iot":False,"dcm":False,"partner_onboarding":False}}}

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        n=int(self.headers.get("Content-Length") or 0); raw=self.rfile.read(n) if n else b""
        try: body=json.loads(raw) if raw.strip() else {}
        except Exception: body={}
        doc=run(body.get("case_id") or "CASE-2026-0002", body.get("seat_id") or "D-AXFB-1K")
        b=json.dumps(doc,indent=1).encode()
        self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self,*a): pass

if __name__=="__main__":
    print("starter on :8080"); HTTPServer(("0.0.0.0",8080),H).serve_forever()
