"""arifbench — arifOS-governed AssetOpsBench agent runner.

This module wraps the opencode-agent runner with arifOS constitutional governance:
every tool call is intercepted and routed through arifOS judge/vault/seal pipeline
BEFORE the tool executes.  Reversible reads → vault log.  State mutations →
888_JUDGE adjudication → SEAL required before execution.

Produces AssetOpsBench-compatible AgentResult / Trajectory so the full
evaluation pipeline (evaluate --scorer llm_judge) runs unchanged.
"""

from __future__ import annotations

from .cli import main

__all__ = ["main"]
