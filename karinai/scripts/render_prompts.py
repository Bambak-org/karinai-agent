#!/usr/bin/env python3
"""Render KarinAI managed-runtime prompt templates from environment."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from karinai.runtime.managed import render_managed_system_prompt


def main() -> int:
    print(render_managed_system_prompt())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
