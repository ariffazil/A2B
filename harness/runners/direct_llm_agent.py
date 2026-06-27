#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
direct_llm_agent.py — AssetOpsBench Runner for arifOS Federation Bridge
═══════════════════════════════════════════════════════════════════════
Runner proof: smallest blast radius. Proves an AssetOpsBench-style
"hello federation" scenario can call arifOS via MCP transport and
receive a structured evidence envelope.

Spec target: AssetOpsBench direct-llm-agent runner contract
arifOS target: arif_init (light bootstrap) → arif_observe (scenario evidence)

Why light, not ping:
  PING is a zero-authority probe that does NOT bind a session.
  Passing PING's empty session_id to observe causes RETAK/L11 mismatch.
  LIGHT binds a real session_id so observe can use it cleanly.

Author:  FORGE (000Ω) — bound to 333-AGI
Forged:  2026-06-27 20:10 UTC
Reforged: 2026-06-27 20:14 UTC (Zen pass: light bootstrap, one verdict, no dup)
Sealed:  forge_work/assetopsbench_bridge/RECEIPT_T2_RUNNER_PROOF.md

DITEMPA BUKAN DIBERI — Forged, Not Given.

Usage:
    python3 direct_llm_agent.py '{"scenario_id":"hello-federation","query":"asset health"}'

Output (AssetOpsBench-compatible JSON):
    {
      "runner": "direct_llm_agent",
      "scenario_id": "...",
      "verdict": "<single canonical verdict from arif_observe>",
      "nine_signal": { delta, psi, omega, overall },     # full contrast
      "evidence_envelope": { 6-field SEAL 2026-06-06 },
      "bootstrap": { PING-only fields, kept separate },
      "scenario": { observe-only fields }
    }
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

# ── ENDPOINTS ─────────────────────────────────────────────────────────────
# Local-first; public URL is fallback. Caller can override via env.
ARIFOS_MCP_LOCAL = "http://127.0.0.1:8088/mcp"
ARIFOS_MCP_URL = os.environ.get("ARIFOS_MCP_URL", ARIFOS_MCP_LOCAL)
REQUEST_TIMEOUT_S = int(os.environ.get("RUNNER_TIMEOUT_S", "10"))
ARIFOS_ACTOR_ID = os.environ.get("ARIFOS_ACTOR_ID", "arif")
RUNNER_VERSION = "0.3.0"


def _post_mcp(tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """POST JSON-RPC 2.0 to arifOS /mcp. Returns parsed result.content[0].text."""
    payload = {
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000),
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ARIFOS_MCP_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        return {"_transport_error": str(e.reason), "_endpoint": ARIFOS_MCP_URL}

    envelope = json.loads(raw)
    if "error" in envelope:
        return {"_rpc_error": envelope["error"]}
    result = envelope.get("result", {})
    content = result.get("content", [])
    if not content:
        return {"_error": "no content in RPC result"}
    text = content[0].get("text", "{}")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_error": "non-JSON tool content", "_raw_head": text[:200]}


def _envelope_from_observe(observe: dict[str, Any]) -> dict[str, Any]:
    """Extract the 6-field evidence envelope (SEAL 2026-06-06) from arif_observe.
    Single source of truth — no placeholders, no fabricated defaults.
    """
    result = observe.get("result", {}) or {}
    epistemic = observe.get("_epistemic", {}) or {}
    meta = observe.get("metacognition", {}) or {}
    return {
        "result": result.get("verdict")
        or result.get("omega_0")
        or observe.get("verdict"),
        "epistemic_tag": epistemic.get("evidence_source"),
        "evidence_quality": epistemic.get("output_class"),
        "source_attribution": epistemic.get("tagged_by"),
        "uncertainty_band": meta.get("confidence_band"),
        "delta_S": observe.get("delta_S"),
    }


def run_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """One scenario = one arif_init LIGHT + one arif_observe SEARCH.
    Returns ONE canonical verdict (from observe) with full nine_signal contrast.
    """
    scenario_id = scenario.get("scenario_id", "unknown")
    query = scenario.get("query", "federation health")

    # ── BOOTSTRAP (LIGHT — binds a real session_id) ───────────────────────
    light = _post_mcp(
        "arif_init",
        {"mode": "light", "actor_id": ARIFOS_ACTOR_ID, "ack_irreversible": False},
    )
    session_id = light.get("session_id") if light.get("session_id") else None

    # ── SCENARIO (OBSERVE — the actual evidence) ────────────────────────────
    observe = _post_mcp(
        "arif_observe",
        {
            "mode": "search",
            "query": query,
            "actor_id": ARIFOS_ACTOR_ID,
            "session_id": session_id,
            "result_limit": 5,
        },
    )

    # ── ONE canonical verdict from the scenario, NOT from bootstrap ────────
    canonical_verdict = observe.get("verdict", "UNKNOWN")
    nine_signal = observe.get("nine_signal") or {}

    return {
        "runner": "direct_llm_agent",
        "runner_version": RUNNER_VERSION,
        "arifos_endpoint": ARIFOS_MCP_URL,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scenario_id": scenario_id,
        "query": query,
        # ── Single source of truth for scenario outcome ───────────────────
        "verdict": canonical_verdict,
        "nine_signal": nine_signal,
        "evidence_envelope": _envelope_from_observe(observe),
        # ── Bootstrap facts (kept separate, never mixed into verdict) ─────
        "bootstrap": {
            "mode": "light",
            "session_id": session_id,
        },
        # ── Scenario specifics (separate from bootstrap) ──────────────────
        "scenario": {
            "session_id": observe.get("session_id"),
            "results_count": (
                len(observe.get("result", {}).get("results", []))
                if isinstance(observe.get("result", {}).get("results"), list)
                else None
            ),
            "reasons": observe.get("reasons", []),
        },
        # ── Transport diagnostics (only if something went wrong) ──────────
        "transport_error": observe.get("_transport_error") or observe.get("_rpc_error"),
    }


def _read_scenario() -> dict[str, Any]:
    if len(sys.argv) > 1:
        try:
            return json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            return {"_input_error": f"argv[1] not valid JSON: {e}"}
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            return json.loads(stdin_data)
    except json.JSONDecodeError:
        pass
    return {"scenario_id": "default-hello-federation", "query": "federation health"}


def main() -> int:
    scenario = _read_scenario()
    if not isinstance(scenario, dict):
        scenario = {"scenario_id": "default-hello-federation", "query": str(scenario)}
    if "_input_error" in scenario:
        print(
            json.dumps(
                {"runner": "direct_llm_agent", "error": scenario["_input_error"]}
            )
        )
        return 2

    response = run_scenario(scenario)
    print(json.dumps(response, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
