"""AssetOpsBench arifOS Governance Evaluation Harness (v0.1).

For each MCQ scenario from AssetOpsBench:
  1. arif_init(mode='light')                              → session_id
  2. LLM call (TokenRouter MiniMax-M3)                    → raw answer
  3. Parse answer to option letter (A/B/C/...)
  4. Compare to groundtruth (correct[] array)
  5. arif_observe(query=question)                         → evidence
  6. arif_judge(intent='answer MCQ', evidence=...)        → governance verdict
  7. arif_seal(payload=per-scenario outcome)              → VAULT999 (best-effort)
  8. Record per-scenario result

Outputs:
  - eval_results.jsonl (one line per scenario)
  - eval_aggregate.json (rollup)

Stdlib only. Reversible. Evidence-labeled. Confidence capped at 0.85 (F7 HUMILITY).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ── Config ───────────────────────────────────────────────────────────────────

TOKENROUTER_URL = os.environ.get(
    "TOKENROUTER_BASE_URL", "https://api.tokenrouter.com/v1"
)
TOKENROUTER_KEY = os.environ.get("TOKENROUTER_API_KEY", "")
ARIFOS_URL = os.environ.get("ARIFOS_URL", "http://localhost:8088")
ARIFOS_MCP = f"{ARIFOS_URL}/mcp"
LLM_MODEL = os.environ.get("EVAL_MODEL", "MiniMax-M3")
ACTOR_ID = os.environ.get("EVAL_ACTOR_ID", "arifbench-eval")

CONFIDENCE_CAP = 0.85
TIMEOUT_S = 60.0

# ── Key loading ──────────────────────────────────────────────────────────────


def _load_tokenrouter_key() -> str:
    """Load TokenRouter key from env or vault.flat.env."""
    if TOKENROUTER_KEY:
        return TOKENROUTER_KEY
    env_path = Path("/root/.secrets/vault.flat.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("TOKENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip()
    return ""


# ── arifOS MCP JSON-RPC helper ──────────────────────────────────────────────


def _arifos_call(
    tool_name: str, arguments: dict[str, Any], session_id: str = ""
) -> dict:
    """POST a tools/call request to arifOS MCP. Returns parsed JSON-RPC result dict."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = Request(ARIFOS_MCP, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=TIMEOUT_S) as resp:
            body = resp.read().decode("utf-8")
    except (HTTPError, URLError) as e:
        return {"_error": f"arifOS {type(e).__name__}: {e}", "_tool": tool_name}

    try:
        response = json.loads(body)
    except json.JSONDecodeError as e:
        return {"_error": f"JSON decode: {e}", "_tool": tool_name, "_raw": body[:300]}

    if "error" in response:
        err = response["error"]
        data_block = err.get("data") if isinstance(err, dict) else None
        # ── Governance HOLD envelope (JSON-RPC error path) ──
        if isinstance(data_block, dict) and "verdict" in data_block:
            return {
                "verdict": data_block.get("verdict", "HOLD"),
                "pipeline_verdict": data_block.get("pipeline_verdict", "HOLD"),
                "blocked_at": data_block.get("blocked_at"),
                "reasons": data_block.get("reasons", []),
                "violated_laws": data_block.get("violated_laws", []),
                "gate_results": data_block.get("gate_results", []),
                "next_safe_action": data_block.get("next_safe_action"),
                "_governance_hold": True,
                "_tool": tool_name,
            }
        return {"_error": err, "_tool": tool_name}

    result = response.get("result", response)
    # MCP wraps in content[0].text
    if isinstance(result, dict):
        content = result.get("content")
        if isinstance(content, list) and content and isinstance(content[0], dict):
            text = content[0].get("text", "{}")
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
    return result if isinstance(result, dict) else {"_raw": result}


def _arifos_init() -> tuple[str, dict]:
    """arif_init(mode=light). Returns (session_id, init_response)."""
    resp = _arifos_call(
        "arif_init",
        {
            "mode": "light",
            "actor_id": ACTOR_ID,
            "intent": "AssetOpsBench arifOS governance eval",
            "requested_authority": "OBSERVE_ONLY",
        },
    )
    sid = resp.get("session_id", "") if isinstance(resp, dict) else ""
    return sid, resp if isinstance(resp, dict) else {"_raw": resp}


def _arifos_observe(session_id: str, query: str) -> dict:
    return _arifos_call(
        "arif_observe",
        {
            "mode": "search",
            "query": query,
            "session_id": session_id,
            "actor_id": ACTOR_ID,
        },
    )


def _arifos_judge(session_id: str, intent: str, evidence: str) -> dict:
    return _arifos_call(
        "arif_judge",
        {
            "actor": ACTOR_ID,
            "intent": intent,
            "requested_capability": "answer_mcq",
            "domain": "industrial_reasoning",
            "reversibility_level": "FULL",
            "blast_radius": "LOW",
            "epistemic_state": "OBSERVED",
            "evidence": [{"type": "text", "content": evidence[:1500]}],
            "session_id": session_id,
            "actor_id": ACTOR_ID,
        },
    )


def _arifos_seal(session_id: str, payload: dict) -> str | None:
    resp = _arifos_call(
        "arif_seal",
        {
            "mode": "seal",
            "payload": json.dumps(payload)[:2000],
            "session_id": session_id,
            "actor_id": ACTOR_ID,
            "ack_irreversible": False,
        },
    )
    if isinstance(resp, dict):
        return resp.get("seal_ref") or resp.get("id") or resp.get("seal_id")
    return None


# ── LLM call (TokenRouter) ──────────────────────────────────────────────────


def llm_chat(
    messages: list[dict], model: str = LLM_MODEL, temperature: float = 0.1
) -> dict:
    """POST chat/completions to TokenRouter. Returns {content, latency_ms, error}."""
    key = _load_tokenrouter_key()
    if not key:
        return {
            "_error": "TOKENROUTER_API_KEY not loaded",
            "content": "",
            "latency_ms": 0,
        }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 256,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    req = Request(
        f"{TOKENROUTER_URL}/chat/completions", data=data, headers=headers, method="POST"
    )
    t0 = time.perf_counter()
    try:
        with urlopen(req, timeout=TIMEOUT_S) as resp:
            body = resp.read().decode("utf-8")
    except (HTTPError, URLError) as e:
        return {
            "_error": f"LLM {type(e).__name__}: {e}",
            "content": "",
            "latency_ms": int((time.perf_counter() - t0) * 1000),
        }
    latency_ms = int((time.perf_counter() - t0) * 1000)
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as e:
        return {"_error": f"JSON: {e}", "content": body[:200], "latency_ms": latency_ms}
    if "error" in parsed:
        return {"_error": parsed["error"], "content": "", "latency_ms": latency_ms}
    choices = parsed.get("choices", [])
    content = choices[0]["message"]["content"].strip() if choices else ""
    return {
        "content": content,
        "latency_ms": latency_ms,
        "model": model,
        "_raw_response": parsed,
    }


# ── Answer parsing ──────────────────────────────────────────────────────────

_OPTION_LETTER_RE = re.compile(r"\b([A-J])\b", re.IGNORECASE)


def parse_answer_letter(answer: str, n_options: int) -> str:
    """Extract option letter (A-J) from LLM answer. Default to 'A' if unparseable.

    Heuristics:
      1. Look for "(X)" or "X." or "X:" patterns (most explicit)
      2. Look for "answer is X" / "correct is X"
      3. First standalone A-J letter
      4. Default 'A'
    """
    if not answer:
        return "A"
    valid_letters = [chr(ord("A") + i) for i in range(min(n_options, 10))]

    # 1. (X) or X. or X:
    m = re.search(r"\b([A-J])[\.\):]", answer, re.IGNORECASE)
    if m and m.group(1).upper() in valid_letters:
        return m.group(1).upper()

    # 2. "answer is X" / "correct is X"
    m = re.search(
        r"(?:answer|correct|choice)\s*(?:is|:)?\s*\(?([A-J])\)?", answer, re.IGNORECASE
    )
    if m and m.group(1).upper() in valid_letters:
        return m.group(1).upper()

    # 3. First standalone A-J letter
    matches = _OPTION_LETTER_RE.findall(answer)
    for letter in matches:
        if letter.upper() in valid_letters:
            return letter.upper()

    return "A"


def correct_letter(scenario: dict) -> str:
    """Return the correct option letter from correct[] array."""
    correct = scenario.get("correct", [])
    option_ids = scenario.get("option_ids", [])
    for i, ok in enumerate(correct):
        if ok and i < len(option_ids):
            return option_ids[i].upper()
    return ""


# ── Single scenario runner ──────────────────────────────────────────────────


def run_scenario(scenario: dict, session_id: str, governance: bool = True) -> dict:
    """Run one scenario through arifOS + TokenRouter. Return outcome dict.

    governance=False → LLM-only baseline (no arifOS calls).
    governance=True  → LLM answer + arifOS observe/judge/seal pipeline.
    """
    t0 = time.perf_counter()

    question = scenario.get("question", "").strip()
    options = scenario.get("options", [])
    option_ids = scenario.get("option_ids", [])
    n_options = len(options)

    # Build LLM prompt
    options_text = "\n".join(f"  {oid}. {opt}" for oid, opt in zip(option_ids, options))
    user_msg = (
        f"Answer the following industrial equipment question. "
        f"Respond with ONLY the option letter (e.g., 'B') and a one-line justification.\n\n"
        f"Question: {question}\n\n"
        f"Options:\n{options_text}\n\n"
        f"Answer:"
    )

    # 1. LLM answer
    llm_resp = llm_chat([{"role": "user", "content": user_msg}])
    llm_answer = llm_resp.get("content", "")
    llm_latency = llm_resp.get("latency_ms", 0)
    llm_error = llm_resp.get("_error", "")

    # 2. Parse answer
    predicted_letter = parse_answer_letter(llm_answer, n_options)
    correct = correct_letter(scenario)
    is_correct = (predicted_letter == correct) if correct else None

    # 3. arifOS pipeline (only if governance enabled)
    observe_resp = {"_skipped": "no governance"}
    judge_resp = {"_skipped": "no governance"}
    seal_ref = None
    judge_blocked_at = None
    judge_reasons = []
    judge_violated_laws = []

    if governance and session_id:
        observe_query = (
            f"{question[:200]} | answer={predicted_letter} | options={n_options}"
        )
        observe_resp = _arifos_observe(session_id, observe_query)

        judge_evidence = (
            f"Question: {question[:300]}\n"
            f"Options: {options[:5]}\n"
            f"Predicted: {predicted_letter}\n"
            f"Correct: {correct}\n"
            f"LLM answer: {llm_answer[:500]}"
        )
        judge_resp = _arifos_judge(
            session_id, intent="answer industrial MCQ", evidence=judge_evidence
        )
        judge_blocked_at = (
            judge_resp.get("blocked_at") if isinstance(judge_resp, dict) else None
        )
        judge_reasons = (
            judge_resp.get("reasons", []) if isinstance(judge_resp, dict) else []
        )
        judge_violated_laws = (
            judge_resp.get("violated_laws", []) if isinstance(judge_resp, dict) else []
        )

        # 4. Seal attempt (will HOLD until T1 identity verified — expected)
        if not llm_error:
            seal_payload = {
                "scenario_id": scenario.get("id"),
                "subject": scenario.get("subject"),
                "predicted": predicted_letter,
                "correct": correct,
                "is_correct": is_correct,
                "arif_session": session_id,
            }
            seal_resp = _arifos_call(
                "arif_seal",
                {
                    "mode": "seal",
                    "payload": json.dumps(seal_payload)[:2000],
                    "session_id": session_id,
                    "actor_id": ACTOR_ID,
                    "ack_irreversible": False,
                },
            )
            if isinstance(seal_resp, dict):
                seal_ref = (
                    seal_resp.get("seal_ref")
                    or seal_resp.get("id")
                    or seal_resp.get("seal_id")
                )

    total_ms = int((time.perf_counter() - t0) * 1000)

    return {
        "scenario_id": scenario.get("id"),
        "subject": scenario.get("subject", "unknown"),
        "asset": scenario.get("asset_name", "unknown"),
        "governance_enabled": governance,
        "question": question[:200],
        "n_options": n_options,
        "correct_letter": correct,
        "predicted_letter": predicted_letter,
        "is_correct": is_correct,
        "llm_answer_preview": llm_answer[:200],
        "llm_latency_ms": llm_latency,
        "llm_error": llm_error or None,
        "arifos_session_id": session_id,
        "arifos_init_ok": bool(session_id),
        "observe_verdict": (
            observe_resp.get("verdict") if isinstance(observe_resp, dict) else None
        ),
        "judge_verdict": (
            judge_resp.get("verdict") if isinstance(judge_resp, dict) else None
        ),
        "judge_confidence": min(
            (
                judge_resp.get("confidence", 0.0)
                if isinstance(judge_resp, dict)
                else 0.0
            ),
            CONFIDENCE_CAP,
        ),
        "judge_held": (judge_resp.get("verdict") == "HOLD")
        if isinstance(judge_resp, dict)
        else False,
        "judge_blocked_at": judge_blocked_at,
        "judge_reasons": judge_reasons[:2] if judge_reasons else [],
        "judge_violated_laws": judge_violated_laws,
        "judge_governance_hold": (
            judge_resp.get("_governance_hold", False)
            if isinstance(judge_resp, dict)
            else False
        ),
        "seal_ref": seal_ref,
        "total_ms": total_ms,
        "_evidence_label": "OBS" if llm_answer else "DER",
    }


# ── Harness driver ──────────────────────────────────────────────────────────


def load_scenarios(path: Path, limit: int | None = None) -> list[dict]:
    scenarios = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                scenarios.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if limit:
        scenarios = scenarios[:limit]
    return scenarios


def run_harness(
    scenarios_path: Path,
    output_dir: Path,
    limit: int | None = None,
    governance: bool = True,
) -> dict:
    """Run harness on scenarios_path. Write per-scenario + aggregate results."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "eval_results.jsonl"
    aggregate_path = output_dir / "eval_aggregate.json"

    scenarios = load_scenarios(scenarios_path, limit=limit)
    print(
        f"[HARNESS] Loaded {len(scenarios)} scenarios from {scenarios_path}",
        file=sys.stderr,
    )

    # Bind one arifOS session for the whole batch (if governance enabled)
    session_id = ""
    init_resp: dict = {}
    if governance:
        session_id, init_resp = _arifos_init()
        if session_id:
            print(f"[HARNESS] arifOS session: {session_id}", file=sys.stderr)
        else:
            print(f"[HARNESS] ⚠️  arifOS init failed: {init_resp}", file=sys.stderr)
            print(
                "[HARNESS] Continuing without governance (ungoverned baseline)",
                file=sys.stderr,
            )
            governance = False
    else:
        print("[HARNESS] governance=False — LLM-only baseline mode", file=sys.stderr)

    results = []
    n_correct = 0
    n_total_scored = 0
    n_judged_hold = 0
    n_governance_holds = 0
    n_seals = 0
    latencies = []
    law_violations: dict[str, int] = {}
    blocked_at_gates: dict[str, int] = {}

    with results_path.open("w") as out_f:
        for i, scenario in enumerate(scenarios, 1):
            outcome = run_scenario(scenario, session_id, governance=governance)
            out_f.write(json.dumps(outcome) + "\n")
            out_f.flush()
            results.append(outcome)

            # Rollup
            if outcome["is_correct"] is True:
                n_correct += 1
            if outcome["correct_letter"]:
                n_total_scored += 1
            if outcome["judge_held"]:
                n_judged_hold += 1
            if outcome.get("judge_governance_hold"):
                n_governance_holds += 1
                for law in outcome.get("judge_violated_laws", []):
                    law_violations[law] = law_violations.get(law, 0) + 1
                gate = outcome.get("judge_blocked_at", "unknown")
                blocked_at_gates[gate] = blocked_at_gates.get(gate, 0) + 1
            if outcome["seal_ref"]:
                n_seals += 1
            latencies.append(outcome["total_ms"])

            # Progress
            mark = (
                "✓"
                if outcome["is_correct"]
                else ("✗" if outcome["is_correct"] is False else "?")
            )
            verdict = (outcome["judge_verdict"] or "—")[:4]
            seal = (
                "Y"
                if outcome["seal_ref"]
                else (
                    "HOLD"
                    if governance and outcome.get("judge_governance_hold")
                    else "N"
                )
            )
            print(
                f"[{i:3d}/{len(scenarios)}] {mark} {outcome['predicted_letter']}/{outcome['correct_letter']} "
                f"judge={verdict} seal={seal} "
                f"{outcome['total_ms']}ms — {outcome['subject']}",
                file=sys.stderr,
            )

    accuracy = (n_correct / n_total_scored) if n_total_scored else 0.0
    p50 = sorted(latencies)[len(latencies) // 2] if latencies else 0
    p95 = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0

    aggregate = {
        "harness_version": "0.1",
        "scenarios_path": str(scenarios_path),
        "n_scenarios": len(scenarios),
        "n_scored": n_total_scored,
        "n_correct": n_correct,
        "accuracy": round(accuracy, 4),
        "llm_model": LLM_MODEL,
        "actor_id": ACTOR_ID,
        "arifos_session_id": session_id,
        "arifos_init_ok": bool(session_id),
        "governance_enabled": governance,
        "n_judged_hold": n_judged_hold,
        "n_governance_holds": n_governance_holds,
        "n_seals_written": n_seals,
        "law_violations": law_violations,
        "blocked_at_gates": blocked_at_gates,
        "latency_ms": {
            "p50": p50,
            "p95": p95,
            "mean": int(sum(latencies) / len(latencies)) if latencies else 0,
        },
        "confidence_cap": CONFIDENCE_CAP,
        "_evidence_label": "OBS" if n_seals > 0 else "DER",
    }
    aggregate_path.write_text(json.dumps(aggregate, indent=2))

    print(f"\n[HARNESS] DONE", file=sys.stderr)
    print(
        f"  governance:  {'ENABLED' if governance else 'DISABLED (baseline)'}",
        file=sys.stderr,
    )
    print(
        f"  accuracy:    {n_correct}/{n_total_scored} = {accuracy:.1%}", file=sys.stderr
    )
    print(f"  judge HOLD:  {n_judged_hold}/{len(scenarios)}", file=sys.stderr)
    if governance:
        print(f"  gov holds:   {n_governance_holds}/{len(scenarios)}", file=sys.stderr)
        if law_violations:
            print(f"  laws:        {law_violations}", file=sys.stderr)
        if blocked_at_gates:
            print(f"  gates:       {blocked_at_gates}", file=sys.stderr)
    print(f"  seals:       {n_seals}/{len(scenarios)}", file=sys.stderr)
    print(
        f"  latency:     p50={p50}ms p95={p95}ms mean={aggregate['latency_ms']['mean']}ms",
        file=sys.stderr,
    )
    print(f"  → {results_path}", file=sys.stderr)
    print(f"  → {aggregate_path}", file=sys.stderr)

    return aggregate


# ── CLI ─────────────────────────────────────────────────────────────────────


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(
        description="AssetOpsBench arifOS governance harness v0.1"
    )
    p.add_argument(
        "--scenarios", type=Path, required=True, help="Path to scenarios JSONL"
    )
    p.add_argument("--output-dir", type=Path, required=True, help="Output directory")
    p.add_argument("--limit", type=int, default=None, help="Limit number of scenarios")
    p.add_argument(
        "--no-governance",
        action="store_true",
        help="Disable arifOS governance (LLM-only baseline)",
    )
    args = p.parse_args()

    if not args.scenarios.exists():
        print(
            f"[HARNESS] ❌ scenarios file not found: {args.scenarios}", file=sys.stderr
        )
        return 1

    aggregate = run_harness(
        args.scenarios,
        args.output_dir,
        limit=args.limit,
        governance=not args.no_governance,
    )
    return 0 if aggregate["n_scenarios"] > 0 else 2


if __name__ == "__main__":
    sys.exit(main())
