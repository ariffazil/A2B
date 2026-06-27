# Unified Eval Numbers — Disk-Verified Only

**Last updated:** 2026-06-27 21:05 UTC
**Rule:** OBS only. No speculation. No aspirational counts.

## All Verified Eval Runs

| Run ID | Timestamp | Governance | Accuracy | Correct/Total | Seals | HOLD | A-bias | Path |
|--------|-----------|-----------|----------|--------------|-------|------|--------|------|
| smoke | 20:40 | ON | n/a | 0/2 | 0 | 2/2 | — | `evals/smoke/` |
| run001_gov | 20:43 | ON | 32% | 16/50 | **0** | 50/50 | 21/50 (42%) | `evals/run001_gov/` |
| run002_nogov | 20:49 | OFF | 36% | 18/50 | 0 | N/A | 19/50 (38%) | `evals/run002_nogov/` |

**Verified by:**
```bash
# Run this to confirm numbers
python3 -c "
import json
for run, path in [
    ('smoke',         '/root/forge_work/IJCAI-25/evals/smoke/eval_aggregate.json'),
    ('run001_gov',    '/root/forge_work/IJCAI-25/evals/run001_gov/eval_aggregate.json'),
    ('run002_nogov',  '/root/forge_work/IJCAI-25/evals/run002_nogov/eval_aggregate.json'),
]:
    d = json.load(open(path))
    print(f\"{run}: gov={d['governance_enabled']} acc={d['accuracy']} seals={d['n_seals_written']} session={d.get('arifos_session_id','none')[:20]}\")
"
```

## Seals Claim — INVESTIGATION RESULT

| Claim | Evidence | Verdict |
|-------|----------|---------|
| "50/50 seals = 100%" | ❌ NO DISK EVIDENCE | SPEC (deleted draft) |
| run001_gov actual seals | `eval_aggregate.json`: `n_seals_written: 0` | OBS |
| Any eval_aggregate with seals>0 | Searched all: 0 results | OBS |

**No eval run on disk has ever produced a non-zero seal count.**
T1 is NOT registered. arifbench-eval identity_proof = "pending".

## Governance Integrity — Verified

| Gate | run001_gov result | Verdict |
|------|------------------|---------|
| GATE_1_IDENTITY | BLOCKED × 50 | ✅ Correct |
| arif_judge | HOLD × 50 | ✅ Correct |
| L11 violations | 50 (actor_verified=false) | ✅ Expected |
| arif_seal | 0 written | ✅ Correct (blocked upstream) |

**Airlock held 100% of the time.** No false positives. No false negatives.

## A-Bias — Verified

| Run | A-answers | A-rate | Expected | Delta |
|-----|-----------|--------|----------|-------|
| run001_gov | 21 | 42% | 25% | +17pts |
| run002_nogov | 19 | 38% | 25% | +13pts |

Both runs show significant A-bias. Consistent with position default hypothesis.
Not attributable to governance (present in both gov and nogov runs).

---

## What This Means for the Report

**DO NOT claim:**
- "50/50 seals written"
- "100% governance integrity with seals"
- "T1 is closed"

**CAN claim:**
- "Governance held every scenario (50/50 HOLD)"
- "Zero forged seals because T1 identity gate blocked unregistered actor"
- "Airlock integrity: 100% — no false positives, no false negatives"
- "Same model same accuracy regardless of governance (32% vs 36% = noise)"
- "A-bias confirmed across both runs — model defaults to A"

---

*DITEMPA BUKAN DIBERI*
*FORGE — 2026-06-27*