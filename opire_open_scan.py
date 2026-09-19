#!/usr/bin/env python3
"""opire-open-scan — pull Opire rewards, keep only OPEN GitHub issues that look claimable.

Filters out closed/deleted issues, farm repos, and overcrowded claim queues.
Needs: network + `gh` auth (or falls back to public API with rate limits).

Usage:
  python3 opire_open_scan.py
  python3 opire_open_scan.py --max-heat 10 --min-usd 5 --json
  python3 opire_open_scan.py --opire-json /path/to/rewards.json

Exit 0 always. Human table by default; --json for machine use.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from typing import Any

OPIRE_URL = "https://api.opire.dev/rewards"
ISSUE_RE = re.compile(r"github\.com/([^/]+)/([^/]+)/(?:issues|pull)/(\d+)", re.I)
FARM_RE = re.compile(
    r"(bounty-plaza|bountyfarmer|boxy-gh|agent-bounties|zeroeye|/bugb|"
    r"go-github|seed a paid|recursive bounty|ekeodkde)",
    re.I,
)
VERSION = "1.0.0"


def fetch_opire(path: str | None) -> list[dict[str, Any]]:
    if path:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        req = urllib.request.Request(
            OPIRE_URL,
            headers={"User-Agent": f"opire-open-scan/{VERSION}", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode())
    if not isinstance(data, list):
        raise SystemExit(f"unexpected Opire payload type: {type(data)}")
    return data


def issue_state(owner: str, repo: str, num: str) -> str:
    r = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/issues/{num}", "--jq", ".state"],
        capture_output=True,
        text=True,
    )
    out = (r.stdout or "").strip()
    if r.returncode == 0 and out in ("open", "closed"):
        return out
    err = (r.stderr or r.stdout or "").lower()
    if "404" in err or "not found" in err:
        return "missing"
    if "410" in err or "deleted" in err:
        return "deleted"
    return "error"


def usd_of(row: dict[str, Any]) -> float:
    pp = row.get("pendingPrice") or {}
    cents = pp.get("value") or 0
    try:
        return float(cents) / 100.0
    except (TypeError, ValueError):
        return 0.0


def heat_of(row: dict[str, Any]) -> int:
    return len(row.get("claimerUsers") or []) + len(row.get("tryingUsers") or [])


def scan(rows: list[dict[str, Any]], min_usd: float, max_heat: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        url = row.get("url") or ""
        title = row.get("title") or ""
        org = ((row.get("organization") or {}).get("name")) or ""
        usd = usd_of(row)
        heat = heat_of(row)
        blob = f"{org} {title} {url}"
        m = ISSUE_RE.search(url)
        if not m:
            continue
        owner, repo, num = m.groups()
        ref = f"{owner}/{repo}#{num}"
        if FARM_RE.search(blob) or FARM_RE.search(ref):
            continue
        if usd < min_usd:
            continue
        if heat > max_heat:
            continue
        state = issue_state(owner, repo, num)
        if state != "open":
            continue
        out.append(
            {
                "ref": ref,
                "usd": round(usd, 2),
                "heat": heat,
                "title": title,
                "url": url,
                "org": org,
                "state": state,
            }
        )
    out.sort(key=lambda r: (r["heat"], -r["usd"], r["ref"]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Filter Opire to OPEN, non-farm, low-heat bounties.")
    ap.add_argument("--opire-json", help="Use a saved Opire rewards JSON instead of live fetch")
    ap.add_argument("--min-usd", type=float, default=5.0, help="Minimum pending USD (default 5)")
    ap.add_argument("--max-heat", type=int, default=15, help="Max claimers+trying (default 15)")
    ap.add_argument("--json", action="store_true", help="Emit JSON array")
    ap.add_argument("--version", action="store_true")
    args = ap.parse_args()
    if args.version:
        print(VERSION)
        return

    rows = fetch_opire(args.opire_json)
    hits = scan(rows, min_usd=args.min_usd, max_heat=args.max_heat)

    if args.json:
        print(json.dumps({"version": VERSION, "count": len(hits), "hits": hits}, indent=2))
        return

    print(f"opire-open-scan {VERSION} — {len(hits)} clean OPEN hit(s) (min ${args.min_usd:g}, max heat {args.max_heat})")
    print(f"{'usd':>10}  {'heat':>4}  {'ref':36}  title")
    for h in hits:
        print(f"{h['usd']:10.2f}  {h['heat']:4d}  {h['ref']:36}  {h['title'][:60]}")
    if not hits:
        print("(none — boards quiet or filters too tight)")


if __name__ == "__main__":
    main()
