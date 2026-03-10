"""
Generate a lightweight token/process efficiency audit from git metadata.

This is a proxy report for agent efficiency retrospectives.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import re
import subprocess
import sys


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def parse_shortstat(text: str) -> tuple[int, int, int]:
    files = insertions = deletions = 0
    file_match = re.search(r"(\d+)\s+files?\s+changed", text)
    ins_match = re.search(r"(\d+)\s+insertions?\(\+\)", text)
    del_match = re.search(r"(\d+)\s+deletions?\(-\)", text)
    if file_match:
        files = int(file_match.group(1))
    if ins_match:
        insertions = int(ins_match.group(1))
    if del_match:
        deletions = int(del_match.group(1))
    return files, insertions, deletions


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate token/process efficiency report.")
    parser.add_argument(
        "--output",
        help="Output markdown file path. Defaults to scripts/qa_artifacts/TOKEN-AUDIT-YYYY-MM-DD.md",
    )
    args = parser.parse_args()

    today = dt.date.today().isoformat()
    default_output = pathlib.Path("scripts/qa_artifacts") / f"TOKEN-AUDIT-{today}.md"
    output_path = pathlib.Path(args.output) if args.output else default_output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    shortstat = run_git(["diff", "--shortstat"])
    files_changed, insertions, deletions = parse_shortstat(shortstat)
    status_lines = run_git(["status", "--short"]).splitlines()
    staged = sum(1 for line in status_lines if len(line) >= 2 and line[0] != " " and line[0] != "?")
    unstaged = sum(1 for line in status_lines if len(line) >= 2 and line[1] != " " and line[0] != "?")
    untracked = sum(1 for line in status_lines if line.startswith("??"))

    total_line_delta = insertions + deletions
    churn_ratio = f"{(deletions / insertions):.2f}" if insertions > 0 else "n/a"

    report = f"""# Token/Process Efficiency Audit - {today}

## Snapshot

- Branch: `{branch}`
- Files changed (working tree): {files_changed}
- Lines added: {insertions}
- Lines deleted: {deletions}
- Total line delta: {total_line_delta}
- Churn ratio (deletions/additions): {churn_ratio}
- Staged files: {staged}
- Unstaged files: {unstaged}
- Untracked files: {untracked}

## Interpretation

- Higher churn ratio often indicates rework loops.
- Large unstaged/untracked sets can increase agent context and token spend.
- Smaller scoped diffs usually produce faster, cheaper verification cycles.

## Suggested Actions

1. Use `/verify-gates` before QA or deploy decisions.
2. Use `/commit-safe` to stage only intentional scope.
3. Split large batches into smaller verifier-backed units.
4. Document blockers early to avoid speculative rewrites.
"""

    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote audit report: {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
