# Track: Open (any platform)
Build the five-agent flow with whatever you like - Python + any LLM API, LangGraph, n8n, plain scripts, your own agent framework. Track support: Hossein Rafieekhah.

- Deliverable: a POST endpoint (preferred) or a runnable local demo printing the contract JSON (`contracts/`).
- You own your model access/keys. Keep secrets out of the repo.
- Starter: `starter/skeleton.py` already returns contract-valid JSON for any case - run it, then replace one agent at a time.
- Tip: get a five-stage skeleton that reads {case_id, seat_id} from the POST body and returns valid JSON in the first 30 minutes, then replace stages one by one with real logic over `data/`. Remember: at the showcase your endpoint is re-run on a case you didn't pick.
