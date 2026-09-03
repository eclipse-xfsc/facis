"""Small structured-output client for the local Ollama runtime."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Protocol


class ReasoningClient(Protocol):
    model: str

    def reason(
        self, stage: str, role: str, facts: dict[str, Any], fallback: str
    ) -> dict[str, str]: ...


class OllamaClient:
    """Use one local model for five role-specific agents with a failure circuit breaker."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        enabled: bool | None = None,
    ) -> None:
        self.base_url = (
            base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        ).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
        self.timeout = timeout or float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "12"))
        self.enabled = (
            enabled
            if enabled is not None
            else os.getenv("OLLAMA_ENABLED", "1").lower() not in {"0", "false", "no"}
        )
        self._disabled_reason: str | None = None

    def reason(
        self, stage: str, role: str, facts: dict[str, Any], fallback: str
    ) -> dict[str, str]:
        if not self.enabled:
            return {"text": fallback, "source": "deterministic_fallback:disabled"}
        if self._disabled_reason:
            return {
                "text": fallback,
                "source": f"deterministic_fallback:{self._disabled_reason}",
            }

        schema = {
            "type": "object",
            "properties": {
                "rationale": {"type": "string", "enum": [fallback]}
            },
            "required": ["rationale"],
            "additionalProperties": False,
        }
        body = {
            "model": self.model,
            "stream": False,
            "think": False,
            "keep_alive": "15m",
            "format": schema,
            "options": {"temperature": 0, "num_predict": 96},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are the safety-constrained {role} agent. Return the "
                        "approved conclusion exactly as supplied. Do not analyze, "
                        "expand, or alter it."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "stage": stage,
                            "approved_conclusion": fallback,
                            "tool_facts": facts,
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
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.load(response)
            content = json.loads(payload["message"]["content"])
            rationale = content["rationale"].strip()
            if rationale != fallback:
                raise ValueError("unapproved rationale")
            return {"text": rationale, "source": f"ollama:{self.model}"}
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._disabled_reason = type(exc).__name__
            return {
                "text": fallback,
                "source": f"deterministic_fallback:{self._disabled_reason}",
            }
