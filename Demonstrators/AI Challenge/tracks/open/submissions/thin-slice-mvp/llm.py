"""Structured local-Ollama client with validation and a total time budget."""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from typing import Any, Protocol


IDENTIFIER = re.compile(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)+\b")


class ReasoningClient(Protocol):
    model: str

    def analyze(
        self,
        stage: str,
        role: str,
        facts: dict[str, Any],
        evidence_ids: list[str],
        recommendations: list[str],
        fallback: dict[str, Any],
    ) -> dict[str, Any]: ...


class OllamaClient:
    """Generate agent analysis while keeping identifiers and choices constrained."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        total_budget: float | None = None,
        enabled: bool | None = None,
    ) -> None:
        self.base_url = (
            base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        ).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
        self.timeout = timeout or float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "8"))
        self.total_budget = total_budget or float(
            os.getenv("OLLAMA_TOTAL_BUDGET_SECONDS", "25")
        )
        self.enabled = (
            enabled
            if enabled is not None
            else os.getenv("OLLAMA_ENABLED", "1").lower() not in {"0", "false", "no"}
        )
        self._disabled_reason: str | None = None
        self._started_at = time.monotonic()

    def _fallback(self, data: dict[str, Any], reason: str) -> dict[str, Any]:
        return {
            "data": data,
            "source": f"deterministic_fallback:{reason}",
            "validation": "fallback",
        }

    @staticmethod
    def _contradicts_facts(analysis: str, facts: dict[str, Any]) -> bool:
        text = analysis.lower()
        trend = facts.get("trend", {})
        if trend.get("monotonic_degradation") is False:
            claims_monotonic = "monotonic degradation" in text
            negates_monotonic = "not monotonic" in text or "non-monotonic" in text
            if claims_monotonic and not negates_monotonic:
                return True
        if trend.get("threshold_exceeded") is False:
            if "exceeds the threshold" in text or "threshold exceeded" in text:
                return True
        return False

    def analyze(
        self,
        stage: str,
        role: str,
        facts: dict[str, Any],
        evidence_ids: list[str],
        recommendations: list[str],
        fallback: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.enabled:
            return self._fallback(fallback, "disabled")
        if self._disabled_reason:
            return self._fallback(fallback, self._disabled_reason)
        remaining = self.total_budget - (time.monotonic() - self._started_at)
        if remaining <= 0.25:
            return self._fallback(fallback, "budget")

        schema = {
            "type": "object",
            "properties": {
                "analysis": {"type": "string", "minLength": 1, "maxLength": 200},
                "selected_evidence": {
                    "type": "array",
                    "items": {"type": "string", "enum": evidence_ids},
                    "minItems": 1,
                    "maxItems": min(3, len(evidence_ids)),
                },
                "recommendation": {
                    "type": "string",
                    "enum": recommendations,
                },
            },
            "required": ["analysis", "selected_evidence", "recommendation"],
            "additionalProperties": False,
        }
        body = {
            "model": self.model,
            "stream": False,
            "think": False,
            "keep_alive": "15m",
            "format": schema,
            "options": {"temperature": 0, "num_predict": 160, "num_ctx": 4096},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are the {role}. Output JSON immediately. In analysis, write one "
                        "factual sentence of at most 25 words using only supplied facts. Preserve "
                        "boolean meanings exactly. Select evidence and a recommendation only "
                        "from the allowed lists. Do not explain your process."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "stage": stage,
                            "facts": facts,
                            "allowed_evidence": evidence_ids,
                            "allowed_recommendations": recommendations,
                        }
                    ),
                },
            ],
        }
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=min(self.timeout, remaining)
            ) as response:
                payload = json.load(response)
            data = json.loads(payload["message"]["content"])
            analysis = data["analysis"].strip()
            selected = data["selected_evidence"]
            recommendation = data["recommendation"]
            if not analysis or len(analysis) > 200:
                raise ValueError("invalid analysis")
            if not selected or any(item not in evidence_ids for item in selected):
                raise ValueError("invalid evidence selection")
            if recommendation not in recommendations:
                raise ValueError("invalid recommendation")
            known_text = json.dumps(facts) + " " + " ".join(recommendations)
            if any(identifier not in known_text for identifier in IDENTIFIER.findall(analysis)):
                raise ValueError("invented identifier")
            if self._contradicts_facts(analysis, facts):
                raise ValueError("analysis contradicts facts")
            return {
                "data": {
                    "analysis": analysis,
                    "selected_evidence": selected,
                    "recommendation": recommendation,
                },
                "source": f"ollama:{self.model}",
                "validation": "passed",
            }
        except OSError as exc:
            self._disabled_reason = type(exc).__name__
            return self._fallback(fallback, self._disabled_reason)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return self._fallback(fallback, type(exc).__name__)
