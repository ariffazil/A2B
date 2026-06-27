# Eval Receipt — smoke

**Run ID:** smoke
**Date:** 2026-06-27 20:40 UTC
**Author:** FORGE (000Ω)
**Session:** SEAL-ff6a8d59ae3c4136

## Conditions

| Field | Value |
|-------|-------|
| Governance | ✅ ENABLED (arifOS MCP in loop) |
| arifOS init | ✅ Success |
| T1 identity | ❌ NOT registered (`arifbench-eval` not in `agent_identities.json`) |
| GATE_1_IDENTITY | ✅ BLOCKED (actor_verified=false) |
| arif_judge | HOLD for all scenarios |
| arif_seal | ❌ 0 written (correct — blocked at identity gate) |

## Results

| Metric | Value |
|--------|-------|
| n_scenarios | 2 (smoke — 2 only) |
| n_correct | 0 |
| accuracy | 0.0 (n/a — too small sample) |
| n_seals | 0 |
| latency_mean_ms | ~3,600 (estimated) |

## Purpose

Smoke test — confirmed:
1. arifOS MCP endpoint reachable
2. Identity gate correctly rejects `arifbench-eval`
3. eval_harness.py functional
4. No false positives at airlock

## Next Run

`run001_gov` — full 50-scenario run, same conditions.

---

*DITEMPA BUKAN DIBERI*
*FORGE — 2026-06-27*