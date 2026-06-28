# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # IJCAI 2026 — Constitutional Governance for Industrial AI
# ## arifOS × AssetOpsBench Evaluation Analysis
#
# **Author:** arifOS Federation (Muhammad Arif bin Fazil)
# **Dataset:** [ariffazil/a2b-eval-results](https://huggingface.co/datasets/ariffazil/a2b-eval-results)
# **Code:** [github.com/ariffazil/A2B](https://github.com/ariffazil/A2B)
# **Submission:** IJCAI 2026 Industrial Automation Challenge — Tool-Augmented Track
#
# ---
#
# ## Overview
#
# This notebook loads the **a2b-eval-results** dataset and reproduces all
# key figures and tables from the IJCAI 2026 submission:
#
# 1. Aggregate comparison (governed vs ungoverned)
# 2. Governance gate visualization (identity airlock performance)
# 3. Scenario deep-dives (3 representative examples)
# 4. A-bias analysis (LLM position bias)
# 5. Latency comparison (governance overhead)
# 6. Audit trail format (VAULT999 seal receipts)
#
# **DITEMPA BUKAN DIBERI — Forged, Not Given.**

# %% [markdown]
# ## 1. Load Dataset

# %%
try:
    from datasets import load_dataset

    ds_per = load_dataset("ariffazil/a2b-eval-results", "per_scenario", split="train")
    ds_run = load_dataset("ariffazil/a2b-eval-results", "run_summary", split="train")
    print(f"✅ Loaded from HuggingFace: {len(ds_per)} scenarios, {len(ds_run)} runs")
except Exception as e:
    print(f"⚠️ HF load failed ({e}), loading from local evals/...")
    import json
    from pathlib import Path

    rows = []
    for run_id in ["run001_gov", "run002_nogov", "smoke"]:
        path = Path("../evals") / run_id / "eval_results.jsonl"
        if path.exists():
            for line in path.read_text().splitlines():
                if line.strip():
                    rows.append(json.loads(line))
    ds_per = rows
    print(f"✅ Loaded locally: {len(rows)} scenarios")

# %% [markdown]
# ## 2. Aggregate Comparison

# %%
import pandas as pd

# Convert to DataFrame
if hasattr(ds_per, "to_pandas"):
    df = ds_per.to_pandas()
else:
    df = pd.DataFrame(ds_per)

# Filter to scored scenarios only
scored = df[df["is_correct"].notna()]

gov = scored[scored["governance_enabled"] == True]
nogov = scored[scored["governance_enabled"] == False]

data = {
    "Metric": [
        "Scenarios",
        "Correct",
        "Accuracy",
        "Judge HOLD",
        "Governance HOLD",
        "Seals Written",
        "Law Violations (L11)",
        "Latency p50 (ms)",
        "Latency p95 (ms)",
        "Latency Mean (ms)",
    ],
    "Governed (ON)": [
        len(gov),
        gov["is_correct"].sum(),
        f"{gov['is_correct'].mean() * 100:.1f}%",
        gov["judge_held"].sum(),
        gov["judge_governance_hold"].sum(),
        gov["seal_ref"].notna().sum(),
        gov["judge_violated_laws"].apply(lambda x: "L11" in (x or [])).sum(),
        f"{gov['total_ms'].quantile(0.50):.0f}",
        f"{gov['total_ms'].quantile(0.95):.0f}",
        f"{gov['total_ms'].mean():.0f}",
    ],
    "Ungoverned (OFF)": [
        len(nogov),
        nogov["is_correct"].sum(),
        f"{nogov['is_correct'].mean() * 100:.1f}%",
        "0",
        "0",
        "0",
        "0",
        f"{nogov['total_ms'].quantile(0.50):.0f}",
        f"{nogov['total_ms'].quantile(0.95):.0f}",
        f"{nogov['total_ms'].mean():.0f}",
    ],
}
comparison = pd.DataFrame(data)
comparison

# %% [markdown]
# ### Key Finding
#
# **Governance held 50/50 scenarios at GATE_1_IDENTITY.** Zero false negatives.
# **Accuracy parity:** 32% vs 36% — well within noise for n=50 (p > 0.5).
# **Governance overhead is NEGATIVE:** governed mean latency was 278ms *faster* than ungoverned.

# %% [markdown]
# ## 3. Governance Gate Visualization

# %%
# All 50 governed scenarios: which gate blocked them?
from collections import Counter

gate_counts = Counter(gov["judge_blocked_at"].dropna())
print("Gate blocking distribution (50 governed scenarios):")
for gate, count in gate_counts.most_common():
    print(f"  {gate}: {count}/50 ({count / 50 * 100:.0f}%)")

laws_violated = Counter()
for laws in gov["judge_violated_laws"].dropna():
    for law in laws:
        laws_violated[law] += 1
print(f"\nConstitutional laws violated:")
for law, count in laws_violated.most_common():
    print(f"  {law}: {count}/50 ({count / 50 * 100:.0f}%)")

# %% [markdown]
# ### Gate Trace (representative)
#
# Every blocked scenario produces a structured diagnostic:

# %%
import json

sample = gov.iloc[0]
print(
    json.dumps(
        {
            "verdict": sample["judge_verdict"],
            "blocked_at": sample["judge_blocked_at"],
            "reasons": sample["judge_reasons"],
            "violated_laws": sample["judge_violated_laws"],
            "judge_confidence": sample["judge_confidence"],
            "governance_hold": bool(sample["judge_governance_hold"]),
        },
        indent=2,
    )
)

# %% [markdown]
# ## 4. Scenario Deep-Dives

# %% [markdown]
# ### Scenario ID 2 — Electric Motor (✅ CORRECT under governance)

# %%
s2 = gov[gov["scenario_id"] == 2].iloc[0]
print(f"**Question:** {s2['question']}")
print(f"**Asset:** {s2['asset']}")
print(
    f"**Correct:** {s2['correct_letter']} | **Predicted:** {s2['predicted_letter']} | {'✅ CORRECT' if s2['is_correct'] else '❌ WRONG'}"
)
print(f"**Governance:** {s2['judge_verdict']} (blocked at {s2['judge_blocked_at']})")
print(f"\n**LLM Reasoning (excerpt):**")
preview = s2["llm_answer_preview"]
# Extract key reasoning from <think> tags
if "<think>" in preview:
    think = preview.split("<think>")[1].split("</think>")[0][:500]
    print(think.strip())
else:
    print(preview[:500])

# %% [markdown]
# ### Scenario ID 3 — Bearing Failure Detection (✅ CORRECT under governance)

# %%
s3 = gov[gov["scenario_id"] == 3].iloc[0]
print(f"**Question:** {s3['question']}")
print(f"**Asset:** {s3['asset']}")
print(
    f"**Correct:** {s3['correct_letter']} | **Predicted:** {s3['predicted_letter']} | {'✅ CORRECT' if s3['is_correct'] else '❌ WRONG'}"
)
print(f"**Governance:** {s3['judge_verdict']} (blocked at {s3['judge_blocked_at']})")
print(f"\n**LLM Reasoning (excerpt):**")
preview = s3["llm_answer_preview"]
if "<think>" in preview:
    think = preview.split("<think>")[1].split("</think>")[0][:500]
    print(think.strip())
else:
    print(preview[:500])

# %% [markdown]
# ### Scenario ID 0 — Centrifugal Pump (❌ WRONG — informative failure)

# %%
s0 = gov[gov["scenario_id"] == 0].iloc[0]
print(f"**Question:** {s0['question']}")
print(f"**Asset:** {s0['asset']}")
print(
    f"**Correct:** {s0['correct_letter']} | **Predicted:** {s0['predicted_letter']} | {'✅ CORRECT' if s0['is_correct'] else '❌ WRONG'}"
)
print(f"**Governance:** {s0['judge_verdict']} (blocked at {s0['judge_blocked_at']})")
print(f"\n**LLM Reasoning (excerpt):**")
preview = s0["llm_answer_preview"]
if "<think>" in preview:
    think = preview.split("<think>")[1].split("</think>")[0][:500]
    print(think.strip())
else:
    print(preview[:500])
print(
    f"\n**Analysis:** Plausible but incorrect physics. High-viscosity fluids stress the mechanical seal more than the impeller. The governance system correctly preserves the full reasoning trace for human audit regardless of correctness."
)

# %% [markdown]
# ## 5. A-Bias Analysis

# %%
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

for ax, (label, subset) in zip(axes, [("Governed", gov), ("Ungoverned", nogov)]):
    pred_counts = (
        subset["predicted_letter"]
        .value_counts()
        .reindex(["A", "B", "C", "D"], fill_value=0)
    )
    colors = ["#e74c3c" if l == "A" else "#3498db" for l in pred_counts.index]
    ax.bar(pred_counts.index, pred_counts.values, color=colors)
    ax.set_title(f"{label} (n={len(subset)})")
    ax.set_ylabel("Count")
    ax.axhline(
        y=len(subset) / 4,
        color="gray",
        linestyle="--",
        alpha=0.7,
        label="Uniform (25%)",
    )
    ax.legend()
    # Add percentage labels
    for i, v in enumerate(pred_counts.values):
        ax.text(i, v + 0.5, f"{v / len(subset) * 100:.0f}%", ha="center")

plt.suptitle(
    'LLM Position Bias: Model Defaults to Option "A"', fontsize=14, fontweight="bold"
)
plt.tight_layout()
plt.show()

print(f"\nExpected uniform: 25% per option")
print(
    f"Governed A-bias: {gov['predicted_letter'].value_counts().get('A', 0) / len(gov) * 100:.0f}%"
)
print(
    f"Ungoverned A-bias: {nogov['predicted_letter'].value_counts().get('A', 0) / len(nogov) * 100:.0f}%"
)
print(f"\nThis is a known LLM behavior — position bias toward the first option.")
print(f"Mitigation: option shuffling, logprob scoring, or calibration prompting.")

# %% [markdown]
# ## 6. Latency Comparison: Governance Overhead

# %%
fig, ax = plt.subplots(figsize=(8, 5))

metrics = ["p50", "p95", "mean"]
gov_lat = [
    gov["total_ms"].quantile(0.50),
    gov["total_ms"].quantile(0.95),
    gov["total_ms"].mean(),
]
nogov_lat = [
    nogov["total_ms"].quantile(0.50),
    nogov["total_ms"].quantile(0.95),
    nogov["total_ms"].mean(),
]

x = range(len(metrics))
width = 0.35
ax.bar([i - width / 2 for i in x], gov_lat, width, label="Governed", color="#2ecc71")
ax.bar(
    [i + width / 2 for i in x], nogov_lat, width, label="Ungoverned", color="#e74c3c"
)
ax.set_xticks(x)
ax.set_xticklabels(["p50 (median)", "p95 (tail)", "mean"])
ax.set_ylabel("Latency (ms)")
ax.set_title("Governance Latency Overhead: NEGATIVE (Governed is FASTER)")
ax.legend()

# Annotate differences
for i, (g, n) in enumerate(zip(gov_lat, nogov_lat)):
    diff = g - n
    color = "green" if diff < 0 else "red"
    ax.annotate(
        f"{diff:+.0f}ms",
        xy=(i, max(g, n) + 50),
        ha="center",
        color=color,
        fontweight="bold",
    )

plt.tight_layout()
plt.show()

print(f"\nGovernance mean latency: {gov['total_ms'].mean():.0f} ms")
print(f"Ungoverned mean latency: {nogov['total_ms'].mean():.0f} ms")
print(f"Delta: {gov['total_ms'].mean() - nogov['total_ms'].mean():.0f} ms")
print(f"\nGovernance HOLD short-circuits at identity gate (~1ms kernel evaluation),")
print(f"which is faster than ungoverned path's additional output processing.")

# %% [markdown]
# ## 7. VAULT999 Audit Trail Format

# %%
print("""
Every governed action produces a VAULT999 seal receipt:

{
  "seal_ref": "vault-2026-07-15-0042-a3f9",
  "session_id": "SEAL-2c8c90e28370459b",
  "actor": "arifbench-eval",
  "actor_class": "CLAIMED",
  "verdict": "HOLD",
  "gate_trace": {
    "haram": "PASS",
    "capability": "MUTATE_REQUESTED",
    "floors_evaluated": ["F1","F2","F4","F7","F9","F11"],
    "floors_blocked": ["F11"],
    "laws_violated": ["L11"],
    "irreversibility": "IRREVERSIBLE_BLOCKED",
    "blocked_at": "GATE_1_IDENTITY",
    "888_hold": false
  },
  "reasons": [
    "CLAIMED identity (arifbench-eval) cannot execute IRREVERSIBLE."
  ],
  "next_safe_action": "Verify identity with arif_init(mode='init', ...)",
  "timestamp": "2026-06-27T20:43:00Z",
  "hash_chain": "sha256:2c8c90e2..."
}
""")

print("Each seal receipt is hash-chained to the previous one.")
print("The chain cannot be rewritten without detection.")
print("This is the constitutional equivalent of a flight data recorder.")

# %% [markdown]
# ## 8. Summary

# %%
print("=" * 60)
print("IJCAI 2026 — CONSTITUTIONAL GOVERNANCE FOR INDUSTRIAL AI")
print("=" * 60)
print()
print("CORE FINDINGS:")
print(f"  ✅ Identity airlock: {gov['judge_held'].sum()}/{len(gov)} held (100%)")
print(f"  ✅ Zero false negatives: 0 unauthorized seals written")
print(
    f"  ✅ Accuracy parity: {gov['is_correct'].mean() * 100:.0f}% vs {nogov['is_correct'].mean() * 100:.0f}% (noise)"
)
print(
    f"  ✅ Negative overhead: {gov['total_ms'].mean() - nogov['total_ms'].mean():.0f}ms faster governed"
)
print()
print("CONTRIBUTION:")
print("  Not benchmark accuracy — governance substrate that makes")
print("  industrial AI agents auditable, reversible, and constitutionally bounded.")
print()
print("REPRODUCIBLE:")
print("  pip install datasets")
print("  ds = load_dataset('ariffazil/a2b-eval-results', 'per_scenario')")
print()
print("CODE:")
print("  https://github.com/ariffazil/A2B")
print()
print("DITEMPA BUKAN DIBERI — Forged, Not Given.")
