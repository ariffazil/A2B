# IJCAI-25 / AssetOpsBench Sprint Tracker

**Sprint Start:** 2026-06-27
**Deadline:** 2026-08-01 (35 days)
**Remaining:** 34 days
**Status:** 🟡 PRE-SPRINT — scaffolding a2b repos for next session

---

## MISSION

Enter AssetOpsBench quietly from the edges. Demonstrate that a governed
federation of specialized AI organs (arifOS) handles real-world industrial
asset operations with constitutional grounding — without claiming victory,
just offering evidence.

**Not the goal:** Win the benchmark. The goal is to learn what "constitutional
AI governance in industrial operations" actually means when tested against
real scenarios, and to open a relationship with a researcher who understands
this domain.

---

## WHY THIS MATTERS (plain English for when he replies)

arifOS is a system I built because I watched a great institution slowly forget
what it was built for. I'm a geologist, not a coder — I found my way to AI
through the problem of governance, not through CS.

Most AI systems optimize for task completion. arifOS optimizes for *correct*
task completion under constraint — where "correct" is defined by constitutional
floors (F1-F13), not just output quality.

AssetOpsBench is interesting because it tests something harder than "can the
AI do the task" — it tests whether the AI knows when it *shouldn't* do the task,
when to escalate, and how to handle ambiguity.

---

## PHASE BREAKDOWN

### PHASE 0 — Contact & Setup (Jun 27 — Jul 3) [7 days remaining]
**Goal:** Researcher replies. Repo access confirmed. Dev environment stable.

| Task | Owner | Status | Evidence |
|------|-------|--------|----------|
| Send cold email to researcher | Arif | ✅ Done | Email sent 2026-06-27 |
| Organize project files (chaos → canonical) | FORGE | ✅ Done | `/root/forge_work/IJCAI-25/` |
| Archive 35 stale memory entries (>30d) | FORGE | ✅ Done | `memory/archive/2026-06-27/` |
| Write plain-English researcher brief | FORGE | ✅ Done | `IJCAI-25/RESEARCHER_BRIEF.md` |
| Run eval harness smoke test | FORGE | ✅ Done | `evals/smoke/` |
| Run governance eval (50 scenarios) | FORGE | ✅ Done | `evals/run001_gov/` |
| Run no-governance baseline (50 scenarios) | FORGE | ✅ Done | `evals/run002_nogov/` |
| Await reply (48h window) | — | ⏳ Waiting | — |
| Confirm AssetOpsBench repo access | Arif | 🔲 Pending | — |

**Exit criteria:** Researcher replied. Repo access granted or clear path.

---

### PHASE 0 RESULTS — Eval Runs Complete

Three eval runs completed 2026-06-27:

| Run | Gov | Accuracy | Seals | HOLD | A-bias | Path |
|-----|-----|----------|-------|------|--------|------|
| smoke | ON | n/a | 0 | 2/2 | — | `evals/smoke/` |
| run001_gov | ON | 16/50 (32%) | **0** | 50/50 | 21/50 (42%) | `evals/run001_gov/` |
| run002_nogov | OFF | 18/50 (36%) | 0 | N/A | 19/50 (38%) | `evals/run002_nogov/` |

**Key findings (verified, OBS):**
- Governance held every scenario: 50/50 HOLD ✅
- Zero seals written: T1 identity not registered ❌
- A-bias confirmed: model defaults to "A" answer at 38–42% (expected 25%)
- Governance latency: slightly faster mean (3.6s vs 3.9s) with tighter p95
- LLM accuracy is a domain knowledge floor, not a governance result

**No aspirational claims.** All numbers are disk-verified in `evals/*/eval_aggregate.json`.
Full analysis: `EVAL_NUMBERS.md`

---

### PHASE 1 — Bridge Core (Jul 3 — Jul 17) [14 days]
**Goal:** Functional bridge between arifOS and AssetOpsBench, running clean.

| Task | Owner | Status | Evidence |
|------|-------|--------|----------|
| Runner v1.0 — scenario execution loop | FORGE | 🔲 Pending | — |
| Envelope → AssetOpsBench format adapter | FORGE | 🔲 Pending | — |
| arifOS MCP endpoint health wrapper | FORGE | 🔲 Pending | — |
| 3-run SYUBHAH consistency test (baseline) | FORGE | 🔲 Pending | — |
| VAULT999 seal path for benchmark results | FORGE | 🔲 Pending | — |
| Document constitutional constraints in CAL | FORGE | 🔲 Pending | — |

**Exit criteria:** Runner executes 3 scenarios without crash. Verdict
consistency confirmed. Sealed receipt generated.

---

### PHASE 2 — Benchmark Submission (Jul 17 — Jul 31) [14 days]
**Goal:** Submit results. Receive feedback. Document findings.

| Task | Owner | Status | Evidence |
|------|-------|--------|----------|
| Run full AssetOpsBench scenario set | FORGE | 🔲 Pending | — |
| Generate benchmark report with evidence | FORGE | 🔲 Pending | — |
| arifOS constitutional layer audit (floors) | AUDITOR | 🔲 Pending | — |
| Submit results per competition format | Arif | 🔲 Pending | — |
| Post-submission debrief to researcher | Arif | 🔲 Pending | — |
| Document lessons learned | FORGE | 🔲 Pending | — |

**Exit criteria:** Results submitted. Researcher's feedback received or
acknowledged. Findings sealed to VAULT999.

---

## CURRENT STATE

### Organs (7/7 alive ✅)
```
arifOS :8088   ✅ Constitutional kernel
A-FORGE :7071  ✅ Execution shell
AAA :3001      ✅ Control plane
GEOX :8081     ✅ Earth intelligence
WEALTH :18082  ✅ Capital intelligence
WELL :18083    ✅ Human readiness
```

### Repos (synced ✅)
```
arifOS  ✅ clean
A-FORGE ✅ clean (f5f6d3e + dad4c7e)
AAA     ✅ clean (36ea07df)
GEOX    ✅ clean
WEALTH  ✅ clean
WELL    ✅ clean
```

### Project Structure (canonical ✅)
```
/root/forge_work/IJCAI-25/          ← ALL project work lives here
├── README.md                        ← structure + run registry
├── PROJECT_TRACKER.md               ← sprint management
├── RESEARCHER_BRIEF.md             ← plain-English brief
├── EVAL_NUMBERS.md                 ← verified numbers only
├── data/                           ← scenario data
├── harness/                        ← eval tooling
├── evals/                          ← ALL eval run results
│   ├── smoke/
│   ├── run001_gov/
│   └── run002_nogov/
└── reports/
    └── EVAL_REPORT_v0.1.md        ← Arif's framing (do not overwrite)
```

### Dirty State
- A-FORGE + AAA: ✅ resolved
- Stale eval paths: marked in README, not deleted (may have other artifacts)

---

## OPEN RISKS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Researcher doesn't reply | Medium | Low | 48h window. Follow-up at 72h if silent. |
| Repo access denied | Low | Medium | Work with public AssetOpsBench only |
| arifOS MCP instability during benchmark | Low | High | Fix cascade first (TELEMETRY_PATH ✅ done) |
| Constitutional floor false positives | Medium | Medium | Run floor benchmark before submission |
| 34 days insufficient | Medium | High | Phase 1 + 2 are parallelizable by task type |

---

## PLAIN-ENGLISH BRIEF (for researcher reply)

When he asks "what is arifOS" — answer without vocabulary:

> **What it is:** A federation of AI agents where each agent has a clear role
> (geoscience, capital, health, execution) and a set of hard constraints
> it cannot violate — things like "don't be irreversible without human approval"
> or "don't claim certainty you don't have."
>
> **What problem it solves:** Most AI systems optimize for "did I complete the task."
> arifOS also optimizes for "did I complete the task *correctly* under the
> institution's actual constraints" — which matters in oil & gas, where a wrong
> decision costs lives and money.
>
> **What makes it different from LangGraph/AutoGen:** Those are orchestration
> frameworks — they manage flow. arifOS manages *authority*. It has a
> constitutional kernel that says no to certain things, not just a workflow
> that sequences them. Think of it as the difference between a traffic light
> (orchestration) and traffic law (constitutional).
>
> **The benchmark question:** AssetOpsBench tests real-world industrial
> operations. arifOS was built for exactly that domain. I want to know:
> does constitutional governance help or hurt when the scenario gets messy?

---

## COMMUNICATION LOG

| Date | Event | Detail |
|------|-------|--------|
| 2026-06-27 | Cold email sent | Researcher contacted re: AssetOpsBench + arifOS |
| 2026-06-27 | FORGE cleanup | A-FORGE + AAA committed, 0 dirty repos |

---

## REFERENCES

| Document | Path |
|----------|------|
| Bridge blueprint | `/root/AAA/docs/architecture/ASSETOPSBENCH_BRIDGE.md` |
| Constitutional Abstraction Layer | `/root/AAA/docs/architecture/CONSTITUTIONAL_ABSTRACTION_LAYER.md` |
| Runner v0.3.0 | `/root/forge_work/assetopsbench_bridge/runners/direct_llm_agent.py` |
| This tracker | `/root/forge_work/IJCAI-25/PROJECT_TRACKER.md` |

---

*DITEMPA BUKAN DIBERI — Jalan terus.*
*FORGE — 2026-06-27*