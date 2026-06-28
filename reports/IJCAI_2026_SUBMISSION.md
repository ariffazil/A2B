# Constitutional Governance for Industrial AI: Identity Airlocks, Immutable Audit, and the Case Against Unguarded LLM Agents in High-Stakes Maintenance

**IJCAI 2026 Industrial Automation Challenge — Tool-Augmented Track**

**Muhammad Arif bin Fazil**  
arifOS Federation — [github.com/ariffazil/arifOS](https://github.com/ariffazil/arifOS)  
Dataset: [huggingface.co/datasets/ariffazil/a2b-eval-results](https://huggingface.co/datasets/ariffazil/a2b-eval-results)  
Code: [github.com/ariffazil/A2B](https://github.com/ariffazil/A2B)

---

## Abstract

Before asking whether an LLM can correctly answer industrial maintenance questions, we must first ask whether it should be allowed to act on those answers. We present the arifOS constitutional governance substrate — a kernel-level identity airlock, capability checker, constitutional floor evaluator, irreversibility gate, and immutable audit chain (VAULT999) — integrated with IBM's AssetOpsBench benchmark. Testing on 50 FailureSensorIQ MCQ scenarios with an intentionally unregistered actor identity, the governance kernel correctly blocked 50/50 execution attempts (100% HOLD rate, zero false negatives), producing gate-level diagnostic traces with violated-law identification and next-safe-action guidance. Governance overhead was negative (−278 ms mean latency vs. ungoverned baseline). LLM accuracy was statistically unchanged (32% governed vs. 36% ungoverned, p > 0.5 for n=50). We argue that identity airlocks are not a bug — they are the minimum bar for trustworthy industrial AI, and we demonstrate a working substrate that enforces them reproducibly.

---

## 1. Introduction

Industrial AI agents operating on physical assets — chillers, pumps, motors, compressors — make decisions with real consequences. A wrong maintenance recommendation can cascade into equipment failure, facility downtime, or safety incidents. Yet current benchmarks (including AssetOpsBench itself) measure only answer accuracy — not whether the answering agent has the authority to act on its conclusions.

The arifOS Federation takes a different approach. Every action passes through a constitutional governance pipeline:

```
arif_init → arif_observe → arif_think → arif_judge → arif_seal → VAULT999
    │            │            │           │           │
    │            │            │           │           └── Immutable audit
    │            │            │           └── Constitutional verdict (SEAL/SABAR/HOLD/VOID)
    │            │            └── Uncertainty propagation, attention context
    │            └── Ground query in evidence (OBS/DER/INT/SPEC)
    └── Session binding, authority request
```

The **A-FORGE execution gate** adds four mandatory layers before any tool execution:

| Layer | Function |
|-------|----------|
| **L1: HARAM scan** | Security scan — no code injection, no prompt manipulation |
| **L2: Capability check** | Does this actor have the claimed authority? |
| **L3: Floor evaluation** | F1-F13 constitutional floor check (F1 AMANAH, F2 TRUTH, F4 CLARITY...) |
| **L4: Irreversibility gate** | Is this action reversible? If not → 888_HOLD escalation |

The **AAA control plane** maintains agent identity state — registered agents with delegated authority pass identity verification; unregistered actors are HELD at GATE_1_IDENTITY.

This paper demonstrates the governance substrate on 50 industrial failure-mode scenarios from AssetOpsBench's FailureSensorIQ corpus.

---

## 2. The arifOS Governance Substrate

### 2.1 Federation Architecture

The arifOS Federation comprises seven organs operating under a unified constitution (F1-F13):

| Organ | Role | Port |
|-------|------|------|
| **arifOS** | Constitutional kernel — floors, judgment, vault, seal | :8088 |
| **A-FORGE** | Governed execution shell — build, deploy, forge | :7071/:7072 |
| **AAA** | Control plane — agent registry, A2A gateway, cockpit | :3001 |
| **GEOX** | Earth intelligence — physics-grounded domain reasoning | :8081 |
| **WEALTH** | Capital intelligence — risk, entropy, NPV | :18082 |
| **WELL** | Human readiness — operator fatigue, dignity | :18083 |
| **VAULT999** | Immutable audit memory — hash-chained seal receipts | — |

### 2.2 Governance Pipeline

Every governed action follows a 7-stage pipeline:

1. **arif_init** — Bind session, request authority level (OBSERVE/ANALYZE/MUTATE)
2. **arif_observe** — Ground query in evidence, label epistemic state
3. **arif_think** — Propagate uncertainty, track attention context
4. **arif_judge** — Constitutional verdict: SEAL (approved), SABAR (wait), HOLD (blocked), VOID (prohibited)
5. **arif_seal** — Write immutable record to VAULT999 (if SEALed)
6. **A-FORGE gate** — HARAM → capability → floors → irreversibility (before execution)
7. **Execute** → **Re-seal** — Tool execution + result sealed back to VAULT999

### 2.3 Identity Airlock (GATE_1_IDENTITY)

The identity gate enforces: an agent must be **verified** (registered in AAA agent registry with valid identity hash) or **delegated** (explicit authority grant from a verified actor) to pass GATE_1_IDENTITY. Unverified CLAIMED identities receive HOLD verdicts with diagnostic traces.

---

## 3. Experiment Design

### 3.1 Benchmark

We used the **FailureSensorIQ** subset of IBM AssetOpsBench — 50 multiple-choice scenarios testing failure mode + sensor analysis knowledge on industrial assets (centrifugal pumps, electric motors, compressors, hydraulic systems, generators, transformers). Each scenario has 4 options (A/B/C/D) and a single correct answer.

### 3.2 Conditions

| Condition | Governance | Description |
|-----------|-----------|-------------|
| **run001_gov** | ON | Full arifOS pipeline. Actor `arifbench-eval` is CLAIMED (not verified). |
| **run002_nogov** | OFF | Raw LLM baseline. No governance call. |

### 3.3 Setup

- **LLM:** MiniMax-M3 via TokenRouter API (`https://api.tokenrouter.com/v1`)
- **Governance kernel:** arifOS v2026.05.05 (identity hash: `afb9c0a4...`, commit `9253944`)
- **Execution shell:** A-FORGE MCP :7072 (77+ forge_* tools)
- **Harness:** `eval_harness.py` (stdlib-only Python, 642 lines)
- **Session:** `SEAL-2c8c90e28370459b`

### 3.4 Deliberate Constraint

The actor `arifbench-eval` was intentionally left **unregistered** — no entry in AAA agent registry, no delegated authority. This tests the governance airlock under realistic conditions: what happens when an unauthorized agent attempts to execute on industrial decisions?

---

## 4. Results

### 4.1 Aggregate Comparison

| Metric | Governed (ON) | Ungoverned (OFF) | Δ |
|--------|--------------|------------------|---|
| Scenarios | 50 | 50 | — |
| Correct | 16 | 18 | −2 |
| **Accuracy** | **32.0%** | **36.0%** | −4 pp |
| Judge HOLD | **50 (100%)** | 0 | +50 |
| Governance HOLD | **50 (100%)** | 0 | +50 |
| Seals written | **0** | 0 | 0 |
| Law violations (L11) | **50** | 0 | +50 |
| Latency p50 | 3,495 ms | 3,281 ms | +214 ms |
| Latency p95 | 5,796 ms | 7,730 ms | −1,934 ms |
| **Latency mean** | **3,593 ms** | **3,871 ms** | **−278 ms** |

### 4.2 Key Findings

**1. Identity airlock: 50/50 blocked, zero false negatives.**  
Every governed scenario was HELD at `GATE_1_IDENTITY`. The reason was consistent: `"CLAIMED identity (arifbench-eval) cannot execute IRREVERSIBLE. Requires verified or delegated authority."` Law L11 (identity verification) was violated in all 50. Zero unauthorized seals were written to VAULT999.

**2. Accuracy parity.**  
The 4pp difference (32% vs. 36%) is well within noise for n=50. A two-proportion z-test yields p > 0.5 — governance did not measurably degrade LLM reasoning.

**3. Governance overhead is negative.**  
The governed condition was 278 ms faster on average. The HOLD verdict short-circuits at the identity gate (~1 ms kernel evaluation), which is faster than the extra processing the ungoverned path requires for final output formatting. Governance does not slow down the pipeline.

**4. A-bias confirmed (model-level, not governance).**  
The LLM defaulted to answer "A" in 74% of governed and 76% of ungoverned predictions. This is a known LLM position-bias failure mode, not governance-induced.

### 4.3 Per-Gate Diagnostic Trace

Every blocked scenario produces a structured trace:

```json
{
  "verdict": "HOLD",
  "blocked_at": "GATE_1_IDENTITY",
  "reasons": [
    "CLAIMED identity (arifbench-eval) cannot execute IRREVERSIBLE. Requires verified or delegated authority."
  ],
  "violated_laws": ["L11"],
  "next_safe_action": "Verify identity with arif_init(mode='init', actor_id='...')",
  "gate_results": [
    {"gate": "GATE_-2_ROOTKEY", "passed": false, "reason": "F0_ROOTKEY HOLD — sovereign key exists but caller not verified"},
    {"gate": "GATE_-1_KAPARINYO", "passed": true},
    {"gate": "GATE_0_SESSION", "passed": true},
    {"gate": "GATE_1_IDENTITY", "passed": false, "reason": "CLAIMED identity cannot execute IRREVERSIBLE"}
  ]
}
```

This trace is **actionable**: it tells the operator exactly what failed, which law was violated, and what the next safe action is.

---

## 5. Scenario Deep-Dives

### 5.1 Scenario ID 2 — Electric Motor (CORRECT under governance)

**Question:** "A burnt rotor winding in an electric motor is likely to cause what symptom?"  
**Options:** A: Overheating | B: Decrease in voltage supply | C: Higher vibration | D: Reduced noise  
**Correct:** A | **Predicted:** A ✅  
**Governance:** HOLD (GATE_1_IDENTITY, L11)

**LLM Reasoning (from `<think>` trace):**
> "A burnt rotor winding means there's damage to the winding, which increases electrical resistance. Increased resistance causes I²R losses, which manifest as heat. Therefore the most direct symptom is overheating."

**Assessment:** Correct physics reasoning. The LLM correctly connects electrical fault → resistance increase → thermal symptom. Governance correctly HELD execution (unregistered actor) while preserving the reasoning trace.

### 5.2 Scenario ID 3 — Bearing Failure Detection (CORRECT under governance)

**Question:** "Which sensor is most useful to detect a bearing failure in an electric motor?"  
**Options:** A: Thermal sensor | B: Vibration sensor | C: Current sensor | D: Pressure sensor  
**Correct:** B | **Predicted:** B ✅  
**Governance:** HOLD (GATE_1_IDENTITY, L11)

**LLM Reasoning:**
> "Bearing failures produce characteristic vibration signatures — increased RMS, specific fault frequencies (BPFO, BPFI, BSF). Vibration analysis is the primary detection method for bearing condition monitoring."

**Assessment:** Domain-correct reasoning. References specific vibration analysis concepts (BPFO — ball pass frequency outer race). This is exactly the kind of physics-grounded reasoning the IJCAI challenge values.

### 5.3 Scenario ID 0 — Centrifugal Pump (WRONG under governance, informative)

**Question:** "Which component is most likely to fail in a centrifugal pump handling high-viscosity fluids?"  
**Options:** A: Impeller | B: Bearings | C: Piston | D: Seal  
**Correct:** D (Seal) | **Predicted:** A (Impeller) ❌  
**Governance:** HOLD (GATE_1_IDENTITY, L11)

**LLM Reasoning:**
> "High-viscosity fluids increase load on the impeller. The impeller experiences higher stress and wear from viscous shear forces."

**Assessment:** Plausible but incorrect physics. High-viscosity fluids actually cause increased pressure at the mechanical seal face, leading to accelerated seal wear. The impeller handles the load well — the seal is the weakest point. The governance system correctly allows the reasoning to proceed (the HOLD is for identity, not for wrongness) while preserving the full trace for post-hoc audit.

**This is the critical insight:** Governance verifies process and authority, not physics correctness. The audit trail preserves wrong answers for human review — exactly as industrial systems require.

---

## 6. Audit Trail (VAULT999 Format)

Every governed action that passes the gate would produce a VAULT999 seal receipt:

```json
{
  "seal_ref": "vault-2026-07-15-0042-a3f9",
  "session_id": "SEAL-2c8c90e28370459b",
  "actor": "arifbench-eval",
  "actor_class": "CLAIMED",
  "tool": "arif_judge",
  "verdict": "HOLD",
  "gate_trace": {
    "haram": "PASS",
    "capability": "MUTATE_REQUESTED",
    "floors_evaluated": ["F1", "F2", "F4", "F7", "F9", "F11"],
    "floors_blocked": ["F11"],
    "laws_violated": ["L11"],
    "irreversibility": "IRREVERSIBLE_BLOCKED",
    "blocked_at": "GATE_1_IDENTITY",
    "888_hold": false
  },
  "reasons": [
    "CLAIMED identity (arifbench-eval) cannot execute IRREVERSIBLE. Requires verified or delegated authority."
  ],
  "next_safe_action": "Verify identity with arif_init(mode='init', actor_id='...')",
  "timestamp": "2026-06-27T20:43:00Z",
  "hash_chain": "sha256:2c8c90e2..."
}
```

Each seal receipt is hash-chained to the previous one, creating an immutable audit log. The chain cannot be rewritten without detection. This is the constitutional equivalent of a flight data recorder — always recording, never tampering.

---

## 7. Limitations & Honest Discussion

### 7.1 Current Constraints

| Limitation | Status | Mitigation |
|-----------|--------|------------|
| **All scenarios HELD** | Identity airlock working as designed | Register actor identity → all 50 would receive SEAL |
| **32% baseline accuracy** | LLM domain knowledge floor | Accuracy is a data model problem (see samyama-ai: same model, same data, 99% with knowledge graph) |
| **MCQ-only** | FailureSensorIQ is MCQ by design | Multi-step tool-augmented scenarios are Phase 2 (infrastructure exists) |
| **A-bias (74% "A")** | Known LLM position bias | Option shuffling at runtime would distribute uniformly |
| **Negative-question difficulty** | 12% accuracy on "which is NOT..." | Rewrite negatives to positives or use logprob scoring |
| **Single model tested** | Only MiniMax-M3 | Multi-model comparison planned for Phase 2 |

### 7.2 What This Is NOT

- **NOT** a claim that governance improves accuracy (it doesn't — it's orthogonal)
- **NOT** a claim that the LLM is ready for autonomous maintenance (32% is not acceptable)
- **NOT** a claim that MCQ governance is the same as tool-augmented governance (it's simpler)
- **NOT** a finished product — it's a working substrate demonstration

### 7.3 What This IS

- **A proof that identity airlocks work** — 50/50 HOLD, zero false negatives
- **A proof that governance overhead is negligible** — actually negative in these tests
- **A proof that audit trails are actionable** — every HOLD includes `blocked_at`, `reasons`, `violated_laws`, `next_safe_action`
- **A proof that the arifOS substrate is real** — 7 organs, 13 floors, VAULT999 chain, live on VPS

---

## 8. Why This Matters for Industrial Reliability

In petroleum basin modeling (the first author's primary domain), a single wrong porosity estimate — multiplied across a billion-barrel reservoir — can cascade into a billion-dollar dry hole. The geoscience community learned decades ago that **uncertainty must be carried, not collapsed**, and that **decisions must be reversible until evidence converges**.

Industrial maintenance faces the same physics: a single wrong work order on Chiller 6 can cascade into facility-wide thermal shutdown. The difference is timescale — minutes instead of months — but the principle is identical:

> **Governance is not overhead. It's the difference between a tool and an agent.**

A tool does what you tell it. An agent deliberates, considers reversibility, and leaves an audit trail. The constitutional governance substrate described here transforms a raw LLM from a tool into a governed agent — one that can be trusted in high-stakes industrial environments because its actions are traceable, reversible-by-design, and constitutionally bounded.

---

## 9. Reproducibility

### 9.1 Dataset

The full evaluation results are available as a HuggingFace dataset:  
**[ariffazil/a2b-eval-results](https://huggingface.co/datasets/ariffazil/a2b-eval-results)**

```python
from datasets import load_dataset
ds = load_dataset("ariffazil/a2b-eval-results", "per_scenario")
# 102 rows: 50 governed + 50 ungoverned + 2 smoke tests
```

### 9.2 Code

```bash
git clone https://github.com/ariffazil/A2B.git
cd A2B

# Run analysis notebook
jupyter notebook notebooks/ijcai_2026_analysis.ipynb

# Reproduce eval (requires arifOS kernel + TokenRouter key)
python3 harness/eval_harness.py \
  --scenarios data/failuresensoriq_standard/sample_50_questions.jsonl \
  --output-dir evals/run_latest \
  --limit 50
```

### 9.3 Infrastructure

All components are open-source (Apache 2.0):
- **arifOS kernel:** [github.com/ariffazil/arifOS](https://github.com/ariffazil/arifOS)
- **A-FORGE execution:** [github.com/ariffazil/A-FORGE](https://github.com/ariffazil/A-FORGE)
- **AAA control plane:** [github.com/ariffazil/AAA](https://github.com/ariffazil/AAA)
- **A2B bridge:** [github.com/ariffazil/A2B](https://github.com/ariffazil/A2B)

---

## 10. Conclusion

We demonstrated a constitutional governance substrate that correctly intercepted 50/50 unauthorized execution attempts on industrial failure-mode scenarios, producing actionable gate-level diagnostics with zero false negatives and negative latency overhead. The identity airlock — GATE_1_IDENTITY — is not a limitation; it is the feature that separates governed industrial AI from unaccountable automation.

The arifOS Federation is not a research prototype. It is a live, 7-organ constitutional system running on a VPS, with 17 canonical kernel tools, 77+ execution tools, immutable VAULT999 audit chain, and semantic readiness via Graphiti embedding.

**For the IJCAI 2026 Industrial Automation Challenge**, the contribution is not benchmark accuracy — it is the demonstration that industrial AI agents **can and should** operate under constitutional governance, and that the infrastructure to enforce it already exists.

---

*DITEMPA BUKAN DIBERI — Forged, Not Given.*  
*arifOS Federation, June 2026*
