"""arifbench CLI — arifOS-governed AssetOpsBench agent runner.

Usage:
    uv run arifbench-agent run "What is the status of WorkOrder WO-2024-001?"
    uv run arifbench-agent run --scenario benchmarks/scenario_suite/scenarios/39.txt

Environment variables:
    ARIFOS_URL          — arifOS kernel URL (default: http://localhost:8088)
    ARIFOS_SESSION_ID   — session ID for existing session (optional)
    ASSETOPSBENCH_MODEL — model ID (default: opencode/gpt-5.1-codex)
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as _dt
import json
import logging
import os
import sys
import time
import urllib.request as urllib_http
from pathlib import Path

# Ensure repo root on path
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agent.arifbench.arif_os_client import ArifOSClient
from agent.arifbench.constitutional_runner import ConstitutionalRunner
from agent.runner import DEFAULT_SERVER_PATHS
from observability import agent_run_span

_log = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="arifOS-governed AssetOpsBench agent runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # run command
    run = sub.add_parser("run", help="Run agent on a question or scenario file")
    run.add_argument("question", help="Question or path to scenario .txt file")
    run.add_argument(
        "--model", default=os.environ.get("ASSETOPSBENCH_MODEL", "opencode/gpt-5.1-codex"),
        help="Model ID (default: opencode/gpt-5.1-codex)",
    )
    run.add_argument(
        "--server-path", action="append", dest="server_paths",
        help="Override server path (name=path); can be repeated",
    )
    run.add_argument(
        "--max-steps", type=int, default=30,
        help="Max agent steps (default: 30)",
    )
    run.add_argument(
        "--timeout", type=int, default=900,
        help="Timeout in seconds (default: 900)",
    )
    run.add_argument(
        "--no-governance", action="store_true",
        help="Disable arifOS governance (baseline comparison run)",
    )
    run.add_argument(
        "--output", type=Path,
        help="Write result JSON to file",
    )
    run.add_argument(
        "--verbose", action="store_true",
    )

    # health command
    health = sub.add_parser("health", help="Check all organ health")
    health.add_argument("--verbose", action="store_true")

    return parser.parse_args()


async def _run_command(args: argparse.Namespace) -> int:
    """Execute the 'run' subcommand."""
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)-20s %(levelname)-8s %(message)s",
    )

    # ── Resolve question ──────────────────────────────────────────────────
    question = args.question
    if Path(question).exists():
        question = Path(question).read_text().strip()
        _log.info("Loaded question from file (first 200 chars): %s", question[:200])

    # ── Resolve server paths ───────────────────────────────────────────────
    server_paths: dict[str, Path | str] = dict(DEFAULT_SERVER_PATHS)
    if args.server_paths:
        for override in args.server_paths:
            if "=" not in override:
                _log.error("--server-path must be name=path, got: %s", override)
                return 1
            name, path = override.split("=", 1)
            server_paths[name] = Path(path)

    # ── Create runner ─────────────────────────────────────────────────────
    governed = not args.no_governance
    runner = ConstitutionalRunner(
        server_paths=server_paths,
        model=args.model,
        max_steps=args.max_steps,
        timeout_s=args.timeout,
        governed=governed,
    )

    # ── Health check ───────────────────────────────────────────────────────
    arif = ArifOSClient()
    if governed:
        arif.init_session()
        healthy = arif.health_check()
        if not healthy:
            _log.warning(
                "arifOS kernel unreachable at %s — continuing with degraded governance",
                os.environ.get("ARIFOS_URL", "http://localhost:8088"),
            )
        else:
            _log.info("arifOS governance active (session=%s)", arif.session_id)

    # ── Run ────────────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        result = await runner.run(question)
    except TimeoutError as e:
        _log.error("%s", e)
        return 124
    except Exception as e:
        _log.exception("Runner failed: %s", e)
        return 1
    elapsed_ms = (time.perf_counter() - t0) * 1000

    # ── Output ─────────────────────────────────────────────────────────────
    output = {
        "question": result.question,
        "answer": result.answer,
        "governed": governed,
        "arif_session_id": runner._arif.session_id,
        "turns": len(result.trajectory.turns),
        "tool_calls": [
            {"name": tc.name, "input": tc.input}
            for tc in result.trajectory.all_tool_calls
        ],
        "elapsed_ms": round(elapsed_ms, 1),
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2))
        _log.info("Result written to %s", args.output)

    # ── Console output ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"arifbench — governed={governed}")
    print(f"{'='*60}")
    print(f"Question : {result.question[:200]}")
    print(f"Answer   :\n{result.answer[:500]}")
    print(f"Tool calls: {len(result.trajectory.all_tool_calls)}")
    print(f"Turns    : {len(result.trajectory.turns)}")
    print(f"Elapsed  : {elapsed_ms:.0f}ms")
    if governed:
        print(f"Session  : {runner._arif.session_id}")
    print(f"{'='*60}\n")

    return 0


def _health_command(args: argparse.Namespace) -> int:
    """Check health of all relevant services."""
    import urllib.request

    print("arifbench Health Check")
    print("=" * 50)

    services = [
        ("arifOS", "http://localhost:8088/health"),
        ("iot MCP",  "http://localhost:8088/health"),  # placeholder
        ("CouchDB", "http://localhost:5984/"),
    ]

    all_ok = True
    for name, url in services:
        try:
            req = urllib_http.Request(url)
            with urllib_http.urlopen(req, timeout=5) as r:
                ok = r.status < 400
        except Exception as e:
            ok = False
            print(f"  {name}: ❌ {e}")
            all_ok = False
        if ok:
            print(f"  {name}: ✅")

    arif = ArifOSClient()
    arif.init_session()
    arif_healthy = arif.health_check()
    print(f"  arifOS kernel: {'✅' if arif_healthy else '❌'}")

    print(f"\n{'All services healthy' if all_ok and arif_healthy else 'Some services DOWN'}")
    return 0 if all_ok and arif_healthy else 1


def main() -> int:
    args = _parse_args()

    if args.command == "health":
        return _health_command(args)
    if args.command == "run":
        return asyncio.run(_run_command(args))

    return 0


if __name__ == "__main__":
    sys.exit(main())
