# Constitutional Abstraction Layer (CAL)

**Forged:** 2026-06-27 20:26 UTC
**Author:** FORGE (000Ω) → 333-AGI
**Lane:** A-FORGE (engineering)
**Version:** 0.1.0

> The CAL is the theory behind the bridge. It explains why arifOS organs
> expose the surface they do, why envelopes have the fields they have,
> why the runner consumes one verdict per scenario, and why every action
> must declare its floor binding.

DITEMPA BUKAN DIBERI — Forged, Not Given.

---

## 1. Definition

The Constitutional Abstraction Layer is the **set of invariants** that
constrain how arifOS organs present themselves to the outside world
(MCP clients, AssetOpsBench, peer agents, federated operators).

CAL is not a library, not a service, not a config file. It is the
**shape of correct exposure**.

The bridge (AssetOpsBench integration) is one expression of CAL.
Future bridges (other benchmarks, peer federations, A2A agents) will
inherit the same shape.

---

## 2. The 7 Layers

arifOS presents itself in 7 nested layers. Each layer is a level of
abstraction with its own invariants.

```
L7  Audit Memory       VAULT999 hash chain, append-only
L6  Verdict            arif_judge → arif_seal → arif_act
L5  Evidence Envelope  6 fields SEALED 2026-06-06
L4  Tool Surface       7 canonical tools (F13-hidden 10 internal)
L3  Organ              arifos / geox / wealth / well / aforge / aaa
L2  Federation         7 organs + arifOS kernel, one constitution
L1  Identity           F13 SOVEREIGN — Arif, final veto
```

**Rule:** A consumer at layer N may reference layers above (N+1..7)
but never below (1..N-1). For example, an L4 tool call may surface
L5 evidence but not L3 organ internals.

### L1 — Identity
- F13 SOVEREIGN: Arif, final veto.
- The federation exists to serve a human. Every other layer is reversible
  to serve the human's judgment.
- Identity is sovereign-anchored, not server-anchored.

### L2 — Federation
- 7 organs + constitutional kernel = one federation.
- One doctrine, multiple surfaces.
- Cross-organ handoff requires explicit lease (A-FORGE) + seal (arifOS).

### L3 — Organ
- Each organ has a bounded function (evidence, execution, control plane).
- An organ never judges constitution (that's arifOS only).
- An organ never executes irreversibly without arifOS seal (that's arifOS only).

### L4 — Tool Surface
- 7 canonical tools exposed via MCP (arif_init, arif_observe, arif_think,
  arif_route, arif_judge, arif_seal, arif_act).
- 10 internal tools (F13-ratified hidden): arif_bridge_connect,
  arif_compose, arif_critique, arif_fetch, arif_forge,
  arif_judge_deliberate, arif_kernel_intercept, arif_measure,
  arif_memory, arif_triage.
- Tool count semantics: `tools_exposed_via_mcp=7`, `canonical_tools_loaded=17`.

### L5 — Evidence Envelope (SEALED 2026-06-06)
6 fields, sealed contract:
1. `result`             — canonical outcome
2. `epistemic_tag`      — OBSERVED | DERIVED | INTERPRETED | HYPOTHESIS
3. `evidence_quality`   — graded quality of evidence
4. `source_attribution` — where the evidence came from
5. `uncertainty_band`   — explicit bounds
6. `delta_S`            — entropy delta (informative = negative)

**F4 CLARITY rule:** One source of truth per field. The runner enforces
this via the `_envelope_from_observe()` helper.

### L6 — Verdict
- `arif_judge` deliberates intent → verdict (SEAL | HOLD | VOID | SABAR).
- `arif_seal` writes verdict to VAULT999 chain (irreversible).
- `arif_act` executes approved action (gated by prior seal).

**Authority ladder (never skip):**
PROVENANCE → EVIDENCE → REASONING → AUTHORITY → RISK → ACTION

### L7 — Audit Memory
- VAULT999 is hash-chained, append-only.
- 60 historical gaps pre-May-2026 (SOVEREIGN RULING 2026-06-05: non-issue).
- Post-migration: zero gaps expected.

---

## 3. The Epistemic Ladder

Every claim must declare its rung:

```
OBSERVED         direct observation, sensor data, model output
   ↓
DERIVED          transformation of observations (math, formula)
   ↓
INTERPRETED      human/AI judgment on derived evidence
   ↓
HYPOTHESIS       unverified claim, awaiting test
```

**F2 TRUTH:** Claims without a label are FALSE by default. The ladder is
explicit; ascent is earned by evidence.

**TokenRouter policy enforcement:** Each organ declares its epistemic
state in capabilities and provenance. Cross-organ handoffs may not skip
rungs without explicit A-FORGE lease + arifOS seal.

---

## 4. Authority Ceilings

Per-organ authority is a deliberate asymmetry. CAL codifies it:

| Ceiling | Organs | Allows | Holds On |
|---------|--------|--------|----------|
| FULL | arifos | all capabilities | irreversible without seal |
| LIMITED_MUTATE | aforge | read + write within scope | cross-organ mutation, irreversible |
| EVIDENCE_ONLY | geox, wealth, well | read + compute | any state mutation |

**F13 SOVEREIGN:** Authority is granted by Arif. The TokenRouter
policies (/root/tokenrouter/policies/*.yaml) encode Arif's grants.

---

## 5. Cross-Organ Handoff Rules

When organ A needs organ B's capabilities:

```
A.request()  →  arifos.arif_route(intent)  →  B.execute()
                       │
                       └── if IRREVERSIBLE: arifos.arif_judge → arifos.arif_seal
```

**Concrete examples:**
- `geox.claim_seal` → routed via `arifos.arif_seal` (claims need seal)
- `aforge.vault_write` → routed via `arifos.arif_seal` (vault is arifOS lane)
- `wealth.trade_execution` → HOLD (capital allocation is Arif-only)
- `well.diagnosis_request` → HOLD + recommend professional care (F6)

The TokenRouter policies encode these as `fallback` blocks.

---

## 6. Why the Bridge is Thin

The AssetOpsBench bridge consumes CAL at exactly one layer: L5 (evidence
envelope) and L6 (verdict). It does not mutate L4 (tools), L3 (organs),
L2 (federation), or L1 (identity).

This thinness is the point. The bridge proves the constitutional lane
works end-to-end without asking arifOS to change.

**F1 AMANAH:** The bridge is fully reversible. Delete
`/root/forge_work/assetopsbench_bridge/` + `/root/tokenrouter/` +
`/root/geox/geox_timeseries/` + the cascade fix drop-in, and arifOS
returns to its pre-bridge state.

---

## 7. The 5 Invariants of CAL

These invariants are the contract between arifOS and any external
consumer (runner, benchmark, peer agent):

1. **One canonical verdict per scenario.**
   `verdict === nine_signal.overall === evidence_envelope.result`.
   No contradiction; no averaging; no synthesis.

2. **Bootstrap facts are separate from scenario outcome.**
   Session IDs, actor IDs, and tool versions are transport metadata,
   not evidence. They are reported alongside, never mixed into, the verdict.

3. **Every claim declares its epistemic ladder rung.**
   OBSERVED → DERIVED → INTERPRETED → HYPOTHESIS. No unlabelled claims.

4. **Reversibility is the default.**
   Every bridge artifact is a file, not a state mutation. VAULT999 seals
   are the only irreversible acts, and they require actor_verified=true.

5. **Floor binding is explicit.**
   Every component (runner, policy, backend, fix) declares which F1-F13
   floors it satisfies. No silent guarantees.

---

## 8. How CAL Maps to the Bridge

| CAL Layer | Bridge Component | File |
|-----------|------------------|------|
| L5/L6 — Verdict + Envelope | Runner reads `nine_signal`, `evidence_envelope.result` | `/root/forge_work/assetopsbench_bridge/runners/direct_llm_agent.py` |
| L4 — Tool Surface | arif_init (LIGHT) → arif_observe (search) | (in runner) |
| L3 — Organ | arifOS as canonical kernel | `/health` |
| L2 — Federation | TokenRouter gates cross-organ calls | `/root/tokenrouter/policies/*.yaml` |
| L1 — Identity | actor_id propagated; verification deferred to T1 | (in runner; needs crypto) |
| L7 — Audit Memory | VAULT999 seal (when T1 done) | `/var/lib/arifos/vault/telemetry/` (redirected) |
| Epistemic ladder | ForecastResult.epistemic | `/root/geox/geox_timeseries/backends/base.py` |

---

## 9. Known Limitations of CAL

| Limitation | Why | Workaround |
|------------|-----|------------|
| actor_verified=false (T1) | Ed25519 signature path not yet wired | Env binding carries identity; bridge work proceeds at 90% confidence |
| runtime_drift=true | Container image not rebuilt after commit 0abe104 | Rebuild container; not blocking CAL |
| Challenge mode unreachable | Multi-layer rejection (whitelist, sovereign map, in-memory) | Direct identity via env; defer to T1 |
| VAULT999 historical gaps | 60 gaps pre-May-2026 (Sovereign ruling: non-issue) | Documented; not blocking |

---

## 10. Conclusion

CAL is what makes arifOS governance-able from the outside. Without it,
the federation would be a black box; with it, the federation is auditable
end-to-end without losing its constitution.

The AssetOpsBench bridge is CAL applied to one specific integration.
Future bridges inherit the same shape because the shape is not
negotiable — it is the constitution, abstracted to one page.

---

*Forged 2026-06-27. DITEMPA BUKAN DIBERI.*