#!/usr/bin/env python3
"""Quick loader for the a2b-eval-results HuggingFace dataset.

Usage:
    python3 scripts/load_a2b_dataset.py              # load and summarize
    python3 scripts/load_a2b_dataset.py --local       # load from local evals/ JSONL
    python3 scripts/load_a2b_dataset.py --export-csv   # export to CSV
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_from_hf():
    """Load from HuggingFace datasets library."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("ERROR: pip install datasets")
        sys.exit(1)

    ds_per = load_dataset("ariffazil/a2b-eval-results", "per_scenario", split="train")
    ds_run = load_dataset("ariffazil/a2b-eval-results", "run_summary", split="train")
    return ds_per, ds_run


def load_from_local(repo_root: Path | None = None):
    """Load from local evals/ JSONL files."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[1]

    rows = []
    for run_id in ["run001_gov", "run002_nogov", "smoke"]:
        path = repo_root / "evals" / run_id / "eval_results.jsonl"
        if path.exists():
            for line in path.read_text().splitlines():
                if line.strip():
                    rows.append(json.loads(line))

    # Build run_summary from aggregate files
    summaries = []
    for run_id in ["run001_gov", "run002_nogov", "smoke"]:
        path = repo_root / "evals" / run_id / "eval_aggregate.json"
        if path.exists():
            summaries.append(json.loads(path.read_text()))

    return rows, summaries


def summarize(rows):
    """Print summary statistics."""
    gov = [r for r in rows if r.get("governance_enabled")]
    nogov = [
        r
        for r in rows
        if not r.get("governance_enabled") and r.get("is_correct") is not None
    ]

    print(f"Total scenarios: {len(rows)}")
    print(f"Governed: {len(gov)}, Ungoverned: {len(nogov)}")
    print()

    if gov:
        gov_correct = sum(1 for r in gov if r.get("is_correct"))
        gov_held = sum(1 for r in gov if r.get("judge_held"))
        print(f"=== GOVERNED (n={len(gov)}) ===")
        print(
            f"  Accuracy: {gov_correct}/{len(gov)} = {gov_correct / len(gov) * 100:.1f}%"
        )
        print(f"  Judge HOLD: {gov_held}/{len(gov)}")
        print(f"  Seals written: {sum(1 for r in gov if r.get('seal_ref'))}")
        blocked = {}
        for r in gov:
            gate = r.get("judge_blocked_at", "none")
            blocked[gate] = blocked.get(gate, 0) + 1
        print(f"  Blocked at: {blocked}")
        laws = {}
        for r in gov:
            for law in r.get("judge_violated_laws") or []:
                laws[law] = laws.get(law, 0) + 1
        print(f"  Laws violated: {laws}")
        print()

    if nogov:
        nogov_correct = sum(1 for r in nogov if r.get("is_correct"))
        print(f"=== UNGOVERNED (n={len(nogov)}) ===")
        print(
            f"  Accuracy: {nogov_correct}/{len(nogov)} = {nogov_correct / len(nogov) * 100:.1f}%"
        )
        print()

    # A-bias analysis
    from collections import Counter

    for label, subset in [("Governed", gov), ("Ungoverned", nogov)]:
        if not subset:
            continue
        preds = Counter(r.get("predicted_letter", "?") for r in subset)
        print(f"=== A-BIAS ({label}) ===")
        for letter in sorted(preds.keys()):
            print(
                f"  {letter}: {preds[letter]:2d} ({preds[letter] / len(subset) * 100:.0f}%)"
            )
        print()


def main():
    args = sys.argv[1:]

    if "--local" in args:
        rows, summaries = load_from_local()
        summarize(rows)
    elif "--export-csv" in args:
        try:
            ds_per, _ = load_from_hf()
        except Exception:
            rows, _ = load_from_local()
            import csv, io

            out = io.StringIO()
            if rows:
                writer = csv.DictWriter(out, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
                path = Path("a2b_eval_results.csv")
                path.write_text(out.getvalue())
                print(f"Exported {len(rows)} rows to {path}")
        else:
            ds_per.to_csv("a2b_eval_results.csv")
            print(f"Exported {len(ds_per)} rows to a2b_eval_results.csv")
    else:
        try:
            ds_per, ds_run = load_from_hf()
            print(
                f"Loaded from HF: {len(ds_per)} per_scenario rows, {len(ds_run)} run_summary rows"
            )
            # Convert to list of dicts for summarize
            rows = [dict(r) for r in ds_per]
            summarize(rows)
        except Exception as e:
            print(f"HF load failed ({e}), falling back to local...")
            rows, summaries = load_from_local()
            summarize(rows)


if __name__ == "__main__":
    main()
