#!/usr/bin/env python3
"""Audit KarinAI product prompt/branding files for forbidden upstream identity leaks."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FORBIDDEN_PRODUCT_STRINGS = (
    "You are Hermes Agent",
    "You run on Hermes Agent",
    "Use Hermes local cron",
    "The user may configure unrestricted tools by editing HERMES_HOME",
)

DEFAULT_SCAN_DIRS = (
    REPO_ROOT / "karinai" / "prompts",
    REPO_ROOT / "karinai" / "runtime",
)


def iter_text_files(paths: list[Path]):
    for path in paths:
        if path.is_file():
            yield path
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix in {".py", ".md", ".j2", ".txt", ".yaml", ".yml"}:
                    yield child


def audit_files(paths: list[Path]) -> list[str]:
    failures: list[str] = []
    for path in iter_text_files(paths):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_PRODUCT_STRINGS:
            if forbidden in text:
                failures.append(f"{path.relative_to(REPO_ROOT)} contains forbidden product-facing text: {forbidden!r}")
    return failures


def audit_rendered_prompt() -> list[str]:
    from karinai.runtime.managed import render_managed_system_prompt

    sample_env = {
        **os.environ,
        "KARINAI_MANAGED_RUNTIME": "true",
        "KARINAI_USER_ID": "audit-user",
        "KARINAI_WORKSPACE_ID": "audit-workspace",
        "KARINAI_WORKSPACE_DIR": "/workspace",
        "KARINAI_RUNTIME_STATE_DIR": "/hermes",
        "API_SERVER_KEY": "audit-secret",
    }
    rendered = render_managed_system_prompt(env=sample_env)
    return [
        f"rendered managed prompt contains forbidden text: {forbidden!r}"
        for forbidden in FORBIDDEN_PRODUCT_STRINGS
        if forbidden in rendered
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="extra files/directories to audit")
    args = parser.parse_args(argv)

    failures = audit_files(list(DEFAULT_SCAN_DIRS) + args.paths)
    failures.extend(audit_rendered_prompt())
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("KarinAI prompt branding audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
