# a2b — arifOS × AssetOpsBench Bridge

**ariffazil/a2b** is the canonical home for arifOS federation's integration
with the [AssetOpsBench](https://github.com/IBM/AssetOpsBench) benchmark
(IJCAI 2026 Industrial Automation Challenge).

[![License](https://img.shields.io/badge/License-Apache_2.0-green?style=for-the-badge)](LICENSE)
[![arifOS](https://img.shields.io/badge/arifOS-Federation-blue?style=for-the-badge)](https://github.com/ariffazil/arifOS)

## What is this?

A thin bridge layer between arifOS's constitutional governance kernel and the
AssetOpsBench evaluation framework. The bridge:
- Calls arifOS via JSON-RPC (`arif_init` → `arif_observe` → `arif_judge` → `arif_seal`)
- Returns canonical verdicts per scenario
- Produces VAULT999-sealed evidence for every run

## Why does it exist?

arifOS was built for industrial AI governance — the same domain AssetOpsBench
tests. This bridge lets us measure: does constitutional governance help or
hurt when scenarios get messy?

## Architecture

```
AssetOpsBench scenarios (FailureSensorIQ MCQ)
        ↓
  eval_harness.py (this repo)
        ↓
  TokenRouter → MiniMax-M3       arifOS MCP (:8088)
        ↓                              ↓
  LLM answer (A/B/C/D)         arif_judge → arif_seal → VAULT999
        ↓
  parse → compare → record
```

## Key Results (Disk-Verified, OBS Only)

| Run | Governance | Accuracy | Seals | HOLD | A-bias |
|-----|-----------|----------|-------|------|--------|
| smoke | ON | n/a | 0 | 2/2 ✅ | — |
| run001_gov | ON | 16/50 (32%) | 0 | 50/50 ✅ | 21/50 (42%) |
| run002_nogov | OFF | 18/50 (36%) | 0 | N/A | 19/50 (38%) |

**Key findings:**
- Governance held every scenario: 50/50 HOLD ✅
- Zero seals written: T1 identity not registered (airlock working as designed)
- A-bias confirmed: model defaults to "A" at 38–42% (expected 25%)
- Same model, same accuracy regardless of governance (32% vs 36% = noise)

**No aspirational claims.** All numbers disk-verified in `evals/` directory.

## Quick Start

```bash
# Clone
git clone https://github.com/ariffazil/a2b.git && cd a2b

# Run eval (governance enabled)
python3 harness/eval_harness.py \
  --scenarios data/failuresensoriq_standard/sample_50_questions.jsonl \
  --output-dir evals/run_latest \
  --limit 50

# Run baseline (no governance)
python3 harness/eval_harness.py \
  --scenarios data/failuresensoriq_standard/sample_50_questions.jsonl \
  --output-dir evals/run_nogov \
  --no-governance --limit 50
```

Requires: `TOKENROUTER_API_KEY` env var (or `/root/.secrets/vault.flat.env`).
arifOS kernel must be running at `localhost:8088` for governance runs.

## arifbench Agent (Constitutional Runner)

The `src/agent/arifbench/` directory contains the arifOS-governed agent runner
that wraps AssetOpsBench's opencode-agent with constitutional governance:

| File | Purpose |
|------|---------|
| `arif_os_client.py` | MCP client to arifOS kernel (init, judge, vault, seal) |
| `cli.py` | CLI entry: `uv run arifbench-agent "query"` |
| `constitutional_runner.py` | Intercepts tool calls → arifOS judge → SEAL before execute |

## Repo Structure

```
a2b/
├── README.md
├── LICENSE                          # Apache 2.0
├── harness/                         # Eval tooling
│   ├── eval_harness.py              # Main harness (642 lines)
│   └── runners/
│       └── direct_llm_agent.py     # Direct LLM runner
├── evals/                           # Canonical eval results (disk-verified)
│   ├── smoke/
│   ├── run001_gov/                  # Governance ON
│   └── run002_nogov/               # Governance OFF (baseline)
├── data/
│   └── failuresensoriq_standard/   # FailureSensorIQ MCQ scenarios
├── docs/
│   ├── ASSETOPSBENCH_BRIDGE.md     # Bridge architecture
│   └── CONSTITUTIONAL_ABSTRACTION_LAYER.md
├── reports/
│   └── EVAL_REPORT_v0.1.md        # Framing report
└── src/agent/arifbench/            # Constitutional runner agent
    ├── __init__.py
    ├── arif_os_client.py
    ├── cli.py
    └── constitutional_runner.py
```

## Eval Results Dataset

Structured eval results are also available as a HuggingFace dataset:
**[ariffazil/a2b-eval-results](https://huggingface.co/datasets/ariffazil/a2b-eval-results)**

## Related

- [arifOS Federation](https://github.com/ariffazil/arifOS) — Constitutional kernel
- [AAA Control Plane](https://github.com/ariffazil/AAA) — Agent registry + cockpit
- [AssetOpsBench (IBM Research)](https://github.com/IBM/AssetOpsBench) — Upstream benchmark

## License

Apache 2.0 — same as arifOS and AssetOpsBench.

---

*DITEMPA BUKAN DIBERI — Forged, Not Given.*
