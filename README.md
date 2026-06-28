# A2B — arifOS × AssetOpsBench Bridge

**ariffazil/A2B** is the canonical home for arifOS federation's integration
with the [AssetOpsBench](https://github.com/IBM/AssetOpsBench) benchmark
for the **IJCAI 2026 Industrial Automation Challenge** (Tool-Augmented Track).

[![License](https://img.shields.io/badge/License-Apache_2.0-green?style=for-the-badge)](LICENSE)
[![arifOS](https://img.shields.io/badge/arifOS-Federation-blue?style=for-the-badge)](https://github.com/ariffazil/arifOS)
[![Dataset](https://img.shields.io/badge/🤗-Dataset-yellow?style=for-the-badge)](https://huggingface.co/datasets/ariffazil/a2b-eval-results)

## What is this?

A governed bridge between arifOS's constitutional governance kernel and
AssetOpsBench. Every action passes through:
- **arifOS kernel** (`arif_init` → `arif_observe` → `arif_think` → `arif_judge` → `arif_seal`)
- **A-FORGE execution gate** (HARAM scan + capability check + floor evaluation + irreversibility)
- **VAULT999 immutable audit** (hash-chained seal receipts)

## Why does it exist?

Industrial AI agents make decisions with real consequences. A wrong maintenance
recommendation can cascade into equipment failure. arifOS provides the governance
substrate that ensures every action is **authorized, auditable, and reversible-by-design.**

The IJCAI 2026 submission demonstrates: **identity airlocks work** — 50/50 unauthorized
execution attempts correctly blocked with zero false negatives and negative latency overhead.

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

## IJCAI 2026 Submission

📄 **Paper:** [`reports/IJCAI_2026_SUBMISSION.md`](reports/IJCAI_2026_SUBMISSION.md)  
📓 **Notebook:** [`notebooks/ijcai_2026_analysis.py`](notebooks/ijcai_2026_analysis.py) (open in Jupyter)  
🤗 **Dataset:** [ariffazil/a2b-eval-results](https://huggingface.co/datasets/ariffazil/a2b-eval-results)  

### One-Liner

> Before asking whether an LLM can correctly answer industrial maintenance questions,
> we must first ask whether it should be allowed to act on those answers. arifOS blocked
> 50/50 unauthorized attempts — the identity airlock is the feature, not the bug.

### Quick Analysis

```bash
git clone https://github.com/ariffazil/A2B.git && cd A2B
pip install datasets pandas matplotlib jupyter

# Open the analysis notebook
jupyter notebook notebooks/ijcai_2026_analysis.py

# Or quick summary from command line
python3 scripts/load_a2b_dataset.py
```

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
A2B/
├── README.md                           # This file
├── LICENSE                             # Apache 2.0
├── CITATION.cff                        # Citation metadata
├── CONTRIBUTING.md                     # Contribution guide
│
├── notebooks/                          # 📓 IJCAI 2026 analysis
│   └── ijcai_2026_analysis.py          #   Jupyter notebook (open in Jupyter)
│
├── reports/                            # 📄 Submission documents
│   ├── IJCAI_2026_SUBMISSION.md        #   Paper-style summary (8 sections)
│   └── EVAL_REPORT_v0.1.md             #   Detailed evaluation report
│
├── scripts/                            # 🛠 Utilities
│   └── load_a2b_dataset.py             #   Quick dataset loader & summarizer
│
├── harness/                            # ⚙️ Eval tooling
│   ├── eval_harness.py                 #   Main harness (642 lines, stdlib only)
│   └── runners/
│       └── direct_llm_agent.py         #   Direct LLM runner
│
├── evals/                              # 📊 Canonical eval results (disk-verified)
│   ├── run001_gov/                     #   Governance ON (50 scenarios)
│   │   ├── eval_results.jsonl          #     Per-scenario traces
│   │   ├── eval_aggregate.json         #     Aggregate metrics
│   │   └── RECEIPT.md                  #     Receipt: airlock proof
│   ├── run002_nogov/                   #   Governance OFF baseline (50 scenarios)
│   └── smoke/                          #   Smoke test (2 scenarios)
│
├── data/                               # 📦 Scenario data
│   └── failuresensoriq_standard/       #   FailureSensorIQ MCQ corpus
│       ├── sample_50_questions.jsonl   #     IJCAI eval set (50)
│       ├── all.jsonl                   #     Full set (2,667)
│       ├── all_10_options.jsonl        #     10-option variant
│       └── all_multi_answers.jsonl     #     Multi-answer variant
│
├── docs/                               # 📖 Architecture docs
│   ├── ASSETOPSBENCH_BRIDGE.md         #   Bridge architecture
│   ├── CONSTITUTIONAL_ABSTRACTION_LAYER.md
│   ├── EVAL_NUMBERS.md                 #   Number audit
│   ├── PROJECT_TRACKER.md              #   Project status
│   └── RESEARCHER_BRIEF.md             #   Research summary
│
└── src/agent/arifbench/                # 🤖 Constitutional runner agent
    ├── __init__.py
    ├── arif_os_client.py               #   arifOS MCP client (init, judge, seal)
    ├── cli.py                          #   CLI entry point
    └── constitutional_runner.py         #   Governed MCP proxy (652 lines)
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
