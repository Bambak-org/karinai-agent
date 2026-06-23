"""Template rendering for KarinAI managed runtime prompts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping


_TEMPLATE_RE = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")


class TemplateRenderError(ValueError):
    """Raised when a KarinAI prompt template cannot be rendered safely."""


def prompt_template_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "prompts"


def render_template_text(template: str, variables: Mapping[str, object]) -> str:
    missing: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables or variables[key] is None:
            missing.add(key)
            return match.group(0)
        return str(variables[key])

    rendered = _TEMPLATE_RE.sub(replace, template)
    if missing:
        raise TemplateRenderError(
            "Missing KarinAI prompt template variables: " + ", ".join(sorted(missing))
        )
    unresolved = _TEMPLATE_RE.findall(rendered)
    if unresolved:
        raise TemplateRenderError(
            "Unresolved KarinAI prompt template variables: " + ", ".join(sorted(set(unresolved)))
        )
    return rendered.strip()


def render_template_file(name: str, variables: Mapping[str, object]) -> str:
    path = prompt_template_dir() / name
    if not path.is_file():
        raise TemplateRenderError(f"KarinAI prompt template not found: {name}")
    return render_template_text(path.read_text(encoding="utf-8"), variables)


def render_managed_system_prompt_from_variables(variables: Mapping[str, object]) -> str:
    return render_template_file("system.base.md.j2", variables)
