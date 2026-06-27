# ASSETOPSBENCH Bridge — Constitutional Integration Blueprint

**Forged:** 2026-06-27 20:26 UTC
**Author:** FORGE (000Ω) → 333-AGI
**Lane:** A-FORGE (engineering)
**Version:** 0.1.0

> The bridge makes arifOS federation organs AssetOpsBench-aware without
> mutating constitution, organs, or envelope. It is a thin layer, by design.

DITEMPA BUKAN DIBERI — Forged, Not Given.

---

## 1. Why a Bridge?

AssetOpsBench is an external benchmark / evaluation framework that probes
LLM agents on real-world tasks. arifOS is a governed AI federation with
7 organs, 13 floors, 7 canonical tools, and a hash-chained VAULT999.

The two must interact without:

| Concern | Bridge Approach |
|---------|-----------------|
| Mutating arifOS constitution | ZERO mutation; bridge is opt-in, flag-gated |
| Mutating organ envelopes | Runner reads envelopes, doesn't rewrite them |
| Mutating VAULT999 chain | Seal goes through arifos.arif_seal; runner never seals |
| Breaking F1-F13 | Every component declares its floor binding |
| Pollution of evidence | All bridge artifacts go to `/root/forge_work/assetopsbench_bridge/` |

The bridge is a **read-side mirror** that produces evidence-bound proofs
that arifOS organs work as documented, on a runtime that's actually live.

---

## 2. Components

### 2.1 Runner — `direct_llm_agent.py`

**Location:** `/root/forge_work/assetopsbench_bridge/runners/direct_llm_agent.py`

**Purpose:** Smallest-blast-radius AssetOpsBench-style runner. Calls arifOS via
JSON-RPC, receives canonical envelopes, returns single-verdict-per-scenario.

**Why LIGHT bootstrap (not PING):**
- PING returns no `session_id` → arif_observe rejects with RETAK/L11 mismatch.
- LIGHT binds a real session_id → observe uses it cleanly.

**Output envelope (single canonical verdict):**
```json
{
  "runner": "direct_llm_agent",
  "runner_version": "0.3.0",
  "arifos_endpoint": "http://127.0.0.1:8088/mcp",
  "timestamp_utc": "2026-06-27T20:20:40Z",
  "scenario_id": "run1-hello",
  "query": "federation health",
  "verdict": "SYUBHAH",
  "nine_signal": { "overall": {"state": "SYUBHAH"} },
  "evidence_envelope": { "result": "SYUBHAH" },
  "bootstrap": { "mode": "light", "session_id": "SEAL-ec59b4db611c4410" },
  "scenario": { "results_count": 5, "reasons": [] }
}
```

**F2 TRUTH invariant:** `verdict === nine_signal.overall === envelope.result`.
The runner enforces this via the `_envelope_from_observe()` helper.

### 2.2 TokenRouter Policies — `/root/tokenrouter/policies/`

**Five YAML files** declare per-organ authority ceilings, model preferences,
hold triggers, F1-F13 binding, and audit rules. TokenRouter loads these on
gateway boot.

| Organ | Authority | Rationale |
|-------|-----------|-----------|
| arifos | FULL | Constitutional kernel; sovereign-anchored |
| aforge | LIMITED_MUTATE | Execution shell; writes within declared scope |
| geox | EVIDENCE_ONLY | Earth intelligence; read + compute, no writes |
| wealth | EVIDENCE_ONLY | Capital intelligence; compute only, never trades |
| well | EVIDENCE_ONLY | Vitality mirror; reflect only, never diagnose |

### 2.3 Time-Series Backends — `/root/geox/geox_timeseries/`

Pluggable backends for forecasting. Statistical baseline is always-on;
TTM (IBM Granite Tiny Time Mixer) is flag-gated.

**Why flag-gated?** TTM requires loading a transformer model (~50MB+).
The flag-gate pattern lets us prove the constitutional lane works
(statistical) before paying the ML cost (TTM).

**Activation:**
```bash
export GEOX_TIMESERIES_BACKBONE=ibm/granite-ttm
export GEOX_TIMESERIES_TTM_ENABLED=1
```

**When gated off (default):** `ttm.forecast()` raises `RuntimeError` immediately.
F2 TRUTH: fail loud, fail early. No silent fallback to statistical when
TTM is explicitly requested.

### 2.4 Cascade Fix — `telemetry-path.conf`

**Location:** `/etc/systemd/system/arifos.service.d/telemetry-path.conf`

**Purpose:** Resolved latent permission bug where `/app/telemetry/` was
root-owned but systemd ran arifos as `User=arifos`. Budget violations
failed to write, triggering cascade shutdown.

**Fix:** Redirect `TELEMETRY_PATH` env var to `/var/lib/arifos/vault/telemetry/`
(arifos-owned, writable). Zero source mutation.

---

## 3. Constitutional Flow

```
┌─────────────────────────┐
│   AssetOpsBench Runner  │  (stdlib-only JSON-RPC client)
│   direct_llm_agent.py   │
└───────────┬─────────────┘
            │ JSON-RPC POST /mcp
            │ tools/call { name: "arif_init" | "arif_observe" }
            ▼
┌─────────────────────────┐
│   arifOS :8088          │  (canonical kernel)
│   arif_init → session   │
│   arif_observe → evidence │
└───────────┬─────────────┘
            │ 7-tool canonical surface
            │ 17 internal tools (F13-hidden)
            ▼
┌─────────────────────────┐
│   Federated organs      │
│   GEOX · WEALTH · WELL  │  (read-only bridge)
│   AAA · A-FORGE         │
└───────────┬─────────────┘
            │ backends/ · registry.py
            │ statistical (default) · ttm (gated)
            ▼
┌─────────────────────────┐
│   Time-series output    │  (epistemic ladder)
│   OBSERVED → DERIVED    │
│   → INTERPRETED → HYPOTHESIS │
└─────────────────────────┘
```

---

## 4. F1-F13 Binding (per component)

| Component | F1 | F2 | F4 | F7 | F11 | F13 |
|-----------|----|----|----|----|-----|-----|
| Runner | reversible (no writes) | OBS/DER/INT/SPEC | one verdict field | n/a (LLM-bound) | forge_work/ log | actor_id propagated |
| TokenRouter policies | reversible YAML | explicit ceilings | one source per field | cap 0.90 | per-organ log path | HOLD on irreversible |
| TTM backend | no writes | INTERPRETED label | deterministic w/ seed | cap 0.90 | provenance dict | gated activation |
| Cascade fix | drop-in reversible | OBS-labeled | minimal env mutation | n/a | journalctl + receipt | Arif approved "fix c" |

---

## 5. Run the Bridge

### 5.1 Verify arifOS is alive
```bash
curl -s http://127.0.0.1:8088/health | jq '.status, .identity_hash.b3_prefix, .thermodynamic.verdict'
# Expected: "healthy", "afb9c0a4adcabc6d", "SEAL"
```

### 5.2 Run the runner
```bash
echo '{"scenario_id":"my-test","query":"federation organs"}' | \
  python3 /root/forge_work/assetopsbench_bridge/runners/direct_llm_agent.py | \
  jq '{verdict, nine_signal_overall: .nine_signal.overall.state, session_id: .bootstrap.session_id}'
```

### 5.3 List available backbones
```bash
cd /root/geox && python3 -c "
from geox_timeseries import list_backends
for b in list_backends():
    print(f'{b[\"name\"]:20s} enabled={b[\"enabled\"]}  gate={b[\"gate_reason\"]}')
"
```

### 5.4 Activate TTM (opt-in)
```bash
export GEOX_TIMESERIES_BACKBONE=ibm/granite-ttm
export GEOX_TIMESERIES_TTM_ENABLED=1
# Now TTM backend is available; .forecast() delegates to statistical until
# real inference is wired (see backends/ttm.py docstring).
```

---

## 6. Receipts and Audit Trail

| Receipt | Path | Purpose |
|---------|------|---------|
| T2 Runner Proof | `/root/forge_work/PATH-B3-FIX-CASCADE-2026-06-27.md` | 3-run consistency check, cascade forensics |
| TokenRouter Key | `/root/forge_work/hf_organization/99_RECEIPTS/RECEIPT-2026-06-26-tokenrouter-key-provisioned.md` | API key provisioning, model census |
| Bridge Blueprint | (this file) | Integration SOT |

**VAULT999 seal:** Blocked at GATE_1_IDENTITY (actor_verified=false). T1 deferred
to a separate session where Ed25519 signature completes the identity loop.

---

## 7. Known Gaps (Deferred)

| Gap | Impact | Blocker |
|-----|--------|---------|
| actor_verified=false | arif_judge + arif_seal HOLD on every call | T1 (crypto identity) |
| runtime_drift=true | build_commit ≠ live_commit | Container rebuild |
| WAJIB-4 challenge mode | unreachable at runtime | Multi-layer rejection (whitelist, sovereign map, in-memory state) |
| TTM real inference | delegates to statistical | Wire ibm/granite-ttm model |

---

## 8. Reversal Recipe

To undo all bridge work:
```bash
# Drop-in
sudo rm /etc/systemd/system/arifos.service.d/telemetry-path.conf
sudo systemctl daemon-reload && sudo systemctl restart arifos

# Runner
rm /root/forge_work/assetopsbench_bridge/

# TokenRouter policies
rm -rf /root/tokenrouter/

# Time-series backends
rm -rf /root/geox/geox_timeseries/

# Bridge docs
rm /root/AAA/docs/architecture/ASSETOPSBENCH_BRIDGE.md
rm /root/AAA/docs/architecture/CONSTITUTIONAL_ABSTRACTION_LAYER.md
```

**All bridge artifacts are self-contained. arifOS core untouched.**

---

## 9. Future Work (Roadmap)

1. **T1 — actor_verified=true** — Ed25519 signature completes identity loop.
   Then VAULT999 seal becomes passable.
2. **Wire TTM real inference** — load ibm/granite-ttm-r1, replace stub
   delegation with encoder forward pass + MC-dropout quantiles.
3. **AssetOpsBench full integration** — register arifOS in AssetOpsBench
   registry; expose runner as a benchmark target.
4. **WEALTH collapse scanner integration** — wire geox evidence into
   wealth.collapse_signature_scan for institutional diagnostics.
5. **WELL metabolism adapter** — connect well.compute_metabolic_flux to
   A-FORGE execution intensity.

---

## 10. Cross-References

- AGENTS.md: `/root/AGENTS.md` — federation constitution, heptalogy
- INVARIANTS.md: `/root/AAA/docs/philosophy/INVARIANTS.md`
- TokenRouter policy schema: `/root/tokenrouter/policies/README.md`
- Runner source: `/root/forge_work/assetopsbench_bridge/runners/direct_llm_agent.py`
- T2 proof: `/root/forge_work/PATH-B3-FIX-CASCADE-2026-06-27.md`
- Cascade fix drop-in: `/etc/systemd/system/arifos.service.d/telemetry-path.conf`

---

*Forged 2026-06-27. DITEMPA BUKAN DIBERI.*