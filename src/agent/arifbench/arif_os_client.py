"""arifOS MCP client for arifbench.

Wraps the arifOS constitutional kernel tools via the MCP protocol:
  - arif_init    : bind a governed session
  - arif_judge   : adjudicate irreversible tool calls
  - arif_seal    : write immutable vault record
  - arif_observe : ground queries in evidence

All tools accessed via MCP JSON-RPC over HTTP to the arifOS kernel at :8088/mcp.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from typing import Any
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

_log = logging.getLogger(__name__)

ARIFOS_URL = os.environ.get("ARIFOS_URL", "http://localhost:8088")
ARIFOS_MCP_URL = f"{ARIFOS_URL}/mcp"
ARIFOS_SESSION_ID = os.environ.get("ARIFOS_SESSION_ID", "")
ARIFOS_ACTOR_ID = os.environ.get("ARIFOS_ACTOR_ID", "arifbench")

# ── Tool Classification ───────────────────────────────────────────────────────

# AssetOpsBench tools that are READ-ONLY (no F1 AMANAH risk)
_READ_ONLY_TOOLS = {
    # IoT
    "assets", "sensors", "sensor_history", "get_asset", "asset_sensors",
    "registry_assets",
    # Utilities
    "get_unit", "list_units", "get_weather", "get_electricity_price",
    # FMSR
    "get_failure_modes", "get_failure_mode_sensor_mapping",
    # TSFM (forecasting / inference — no state write)
    "get_ai_tasks", "get_tsfm_models", "run_tsfm_forecasting",
    "run_tsad", "run_integrated_tsad",
    # Vibration
    "compute_fft", "envelope_spectrum", "assess_iso10816", "classify_faults",
    "detect_anomalies",
    # Generic
    "ping", "health",
}

# AssetOpsBench tools that MUTATE state (F1 AMANAH → requires 888_JUDGE)
_MUTATE_TOOLS = {
    # WorkOrder lifecycle
    "create_work_order", "approve_work_order", "assign_work_order",
    "close_work_order", "cancel_work_order",
    # TSFM (finetuning writes model state)
    "run_tsfm_finetuning",
}


def classify_tool(tool_name: str) -> str:
    """Classify a tool call by action class for ART adjudication."""
    if tool_name in _READ_ONLY_TOOLS:
        return "OBSERVE"
    if tool_name in _MUTATE_TOOLS:
        return "MUTATE"
    return "ANALYZE"


def is_irreversible(tool_name: str) -> bool:
    """Return True if this tool is classified as irreversible."""
    return tool_name in _MUTATE_TOOLS


# ── MCP JSON-RPC helpers ─────────────────────────────────────────────────────

def _mcp_post(
    method: str,
    params: dict[str, Any],
    session_id: str = "",
    timeout: float = 30.0,
) -> tuple[dict[str, Any], str]:
    """Send an MCP JSON-RPC request and return (json_rpc_response_dict, mcp_session_id_from_headers)."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = Request(ARIFOS_MCP_URL, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=timeout) as resp:
            response = json.loads(resp.read().decode("utf-8"))
            # Extract MCP session ID from response headers
            mcp_sid = resp.headers.get("Mcp-Session-Id", session_id)
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"arifOS MCP HTTP {e.code}: {body}") from e
    except URLError as e:
        raise RuntimeError(f"arifOS MCP unreachable: {e.reason}") from e

    if "error" in response:
        raise RuntimeError(f"arifOS MCP error: {response['error']}")
    return response, mcp_sid


# ── Session ──────────────────────────────────────────────────────────────────

@dataclass
class ArifOSClient:
    """Minimal arifOS MCP client for arifbench."""
    session_id: str = field(default="")
    actor_id: str = ARIFOS_ACTOR_ID
    _mcp_session_id: str = field(default="", repr=False)
    _initialized: bool = field(default=False, repr=False)

    def init_session(self, intent: str = "assetopsbench_governed") -> str:
        """Initialize an MCP session with arifOS kernel. Returns arifOS session_id."""
        if not self.session_id:
            self.session_id = f"bench-{uuid.uuid4().hex[:12]}"

        # Step 1: MCP handshake to get an MCP session ID (returned as HTTP header)
        try:
            response, mcp_sid = _mcp_post(
                "initialize",
                {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "arifbench", "version": "0.1"},
                },
                timeout=10.0,
            )
            self._mcp_session_id = mcp_sid
        except Exception as e:
            _log.warning("arifOS MCP initialize failed: %s", e)
            self._mcp_session_id = ""

        # Step 2: arif_init to bind the governed session
        try:
            response, _ = _mcp_post(
                "tools/call",
                {
                    "name": "arif_init",
                    "arguments": {
                        "mode": "init",
                        "session_id": self.session_id,
                        "actor_id": self.actor_id,
                        "intent": intent,
                        "requested_authority": "MUTATE",
                        "context": {
                            "benchmark": "AssetOpsBench",
                            "governed": True,
                            "purpose": "IJCAI 2026 governed agent benchmark",
                        },
                    },
                },
                session_id=self._mcp_session_id,
            )
            result = response.get("result", response)
            # Extract session_id from result
            content = result.get("content", [{}])
            if content and isinstance(content[0], dict):
                text = content[0].get("text", "{}")
                try:
                    parsed = json.loads(text)
                    self.session_id = parsed.get("session_id", self.session_id)
                except (json.JSONDecodeError, TypeError):
                    pass
            self._initialized = True
            _log.info("arifOS session initialized: %s (mcp_session=%s)", self.session_id, self._mcp_session_id)
            return self.session_id
        except Exception as e:
            _log.warning("arifOS session init failed (continuing ungoverned): %s", e)
            self._initialized = False
            return self.session_id

    def judge(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        blast_radius: str = "LOW",
    ) -> dict[str, Any]:
        """Adjudicate a tool call through arifOS 888_JUDGE.

        Returns dict with keys: verdict (SEAL|SABAR|HOLD|VOID),
        reasoning, seal_verdict_id (if SEAL).
        """
        action_class = classify_tool(tool_name)
        reversible = "FULL" if tool_name in _READ_ONLY_TOOLS else "PARTIAL"
        domain = "iot_operations" if tool_name in _READ_ONLY_TOOLS else "workorder_mutation"

        if not self._initialized:
            # Fail open for reads, fail closed for mutations
            if tool_name in _MUTATE_TOOLS:
                return {"verdict": "HOLD", "reasoning": "arifOS not initialized"}
            return {"verdict": "SEAL", "reasoning": "Governed fallback: no session"}

        try:
            response, _ = _mcp_post(
                "tools/call",
                {
                    "name": "arif_judge",
                    "arguments": {
                        "actor": self.actor_id,
                        "intent": f"Tool call: {tool_name}",
                        "requested_capability": tool_name,
                        "domain": domain,
                        "reversibility_level": reversible,
                        "blast_radius": blast_radius,
                        "epistemic_state": "OBSERVED",
                        "session_id": self.session_id,
                        "actor_id": self.actor_id,
                    },
                },
                session_id=self._mcp_session_id,
            )
            result = response.get("result", response)
            # Parse verdict from MCP result
            content = result.get("content", [{}])
            if content and isinstance(content[0], dict):
                text = content[0].get("text", "{}")
                try:
                    parsed = json.loads(text)
                    return {
                        "verdict": parsed.get("verdict", "HOLD"),
                        "reasoning": parsed.get("reasoning", ""),
                        "seal_verdict_id": parsed.get("seal_verdict_id"),
                    }
                except (json.JSONDecodeError, TypeError):
                    pass
            return {"verdict": "SEAL", "reasoning": "MCP OK"}
        except Exception as e:
            _log.warning("arifOS judge unavailable, allowing tool (unguarded): %s", e)
            if tool_name in _MUTATE_TOOLS:
                return {"verdict": "HOLD", "reasoning": str(e)}
            return {"verdict": "SEAL", "reasoning": "Governed fallback"}

    def seal(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_output: Any,
        verdict: str,
        session_id: str = "",
    ) -> str | None:
        """Seal a tool call result to VAULT999. Returns seal_ref or None."""
        if not self._initialized:
            return None

        try:
            response, _ = _mcp_post(
                "tools/call",
                {
                    "name": "arif_seal",
                    "arguments": {
                        "mode": "seal",
                        "payload": json.dumps({
                            "tool": tool_name,
                            "input": tool_input,
                            "output": str(tool_output)[:500] if tool_output else None,
                            "verdict": verdict,
                            "actor": self.actor_id,
                            "benchmark": "AssetOpsBench",
                        }),
                        "session_id": session_id or self.session_id,
                        "actor_id": self.actor_id,
                        "ack_irreversible": verdict in ("SEAL",),
                    },
                },
                session_id=self._mcp_session_id,
            )
            result = response.get("result", response)
            content = result.get("content", [{}])
            if content and isinstance(content[0], dict):
                text = content[0].get("text", "{}")
                try:
                    parsed = json.loads(text)
                    return parsed.get("seal_ref") or parsed.get("id")
                except (json.JSONDecodeError, TypeError):
                    pass
            return None
        except Exception as e:
            _log.warning("arifOS seal failed (non-critical): %s", e)
            return None

    def health_check(self) -> bool:
        """Return True if arifOS kernel is reachable."""
        if not self._mcp_session_id:
            try:
                _mcp_json_request(
                    "initialize",
                    {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "arifbench", "version": "0.1"}},
                    timeout=5.0,
                )
                return True
            except Exception:
                return False
        return True
