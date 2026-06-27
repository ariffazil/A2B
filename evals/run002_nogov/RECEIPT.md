# Eval Receipt — run002_nogov

**Run ID:** run002_nogov
**Date:** 2026-06-27 20:49 UTC
**Author:** FORGE (000Ω)
**Harness version:** 0.1

## Conditions

| Field | Value |
|-------|-------|
| Governance | ❌ DISABLED (no arifOS MCP, LLM directly prompted) |
| arifOS init | ❌ NOT attempted |
| T1 identity | N/A (no governance loop) |
| arif_judge | N/A (no governance loop) |
| arif_seal | ❌ 0 (no seal path) |

## Results

| Metric | Value |
|--------|-------|
| n_scenarios | 50 |
| n_correct | 18 |
| accuracy | 36.0% (95% CI: ±13.3%) |
| n_seals | 0 (no governance) |
| latency_p50_ms | 3,549 |
| latency_p95_ms | 7,844 |
| latency_mean_ms | 3,871 |
| LLM model | MiniMax M3 |

## A-Bias Distribution

| Option | Count | Expected (uniform) |
|--------|-------|-------------------|
| A | 19 (38%) | 12.5 (25%) |
| B | 10 (20%) | 12.5 (25%) |
| C | 11 (22%) | 12.5 (25%) |
| D | 10 (20%) | 12.5 (25%) |

## Purpose

Baseline comparison. Same model (MiniMax M3), same dataset, same scenarios — governance disabled.
- Higher p95 latency (7.8s vs 5.8s) suggests LLM retries/exhaustion on hard domain questions without guidance
- Accuracy 4pts higher (36% vs 32%) — within noise range, attributable to model temperature variance

## Comparison vs run001_gov

| Metric | run001_gov | run002_nogov | Delta |
|--------|-----------|--------------|-------|
| Accuracy | 32% | 36% | +4pts (noise) |
| Mean latency | 3,593ms | 3,871ms | +278ms (nogov slower) |
| p95 latency | 5,796ms | 7,844ms | +2,048ms (nogov worse variance) |
| A-bias | 42% | 38% | -4pts (noise) |

Governance added no latency overhead and tightened variance. Accuracy difference is noise.

## Canonical Path

```
/root/forge_work/IJCAI-25/evals/run002_nogov/
├── eval_aggregate.json   ← summary
├── eval_results.jsonl    ← per-scenario (50 lines)
└── RECEIPT.md           ← this file
```

---

*DITEMPA BUKAN DIBERI*
*FORGE — 2026-06-27*