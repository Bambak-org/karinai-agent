"""KarinAI beta managed-runtime tool policy.

The policy is intentionally expressed as existing upstream toolset names so the
first product layer can stay thin and continue to use Hermes' tool filtering.
"""

from __future__ import annotations

from typing import Iterable


BETA_ENABLED_TOOLSETS: tuple[str, ...] = (
    "file",
    "terminal",
    "code_execution",
    "web",
    "vision",
    "todo",
)

BETA_DISABLED_TOOLSETS: tuple[str, ...] = (
    "cronjob",
    "skills",
    "memory",
    "session_search",
    "delegation",
    "image_gen",
    "video",
    "video_gen",
    "tts",
    "homeassistant",
    "computer_use",
    "kanban",
    "discord",
    "discord_admin",
    "feishu_doc",
    "feishu_drive",
    "spotify",
    "x_search",
    "yuanbao",
    "moa",
)

FORBIDDEN_BETA_TOOLS: frozenset[str] = frozenset(
    {
        "cronjob",
        "skill_manage",
        "skills_list",
        "skill_view",
        "memory",
        "session_search",
        "delegate_task",
        "browser_navigate",
        "browser_snapshot",
        "browser_click",
        "browser_type",
        "browser_scroll",
        "browser_back",
        "browser_press",
        "browser_get_images",
        "browser_vision",
        "browser_console",
        "browser_cdp",
        "browser_dialog",
        "image_generate",
        "video_analyze",
        "video_generate",
        "text_to_speech",
        "computer_use",
        "kanban_show",
        "kanban_list",
        "kanban_complete",
        "kanban_block",
        "kanban_heartbeat",
        "kanban_comment",
        "kanban_create",
        "kanban_link",
        "kanban_unblock",
        "ha_list_entities",
        "ha_get_state",
        "ha_list_services",
        "ha_call_service",
        "discord",
        "discord_admin",
        "spotify_playback",
        "spotify_devices",
        "spotify_queue",
        "spotify_search",
        "spotify_playlists",
        "spotify_albums",
        "spotify_library",
    }
)


def _resolve_tool_names(toolsets: Iterable[str]) -> set[str]:
    from toolsets import resolve_toolset

    names: set[str] = set()
    for toolset_name in toolsets:
        names.update(resolve_toolset(str(toolset_name)))
    return names


def effective_tool_names(
    enabled_toolsets: Iterable[str],
    disabled_toolsets: Iterable[str] = (),
) -> set[str]:
    names = _resolve_tool_names(enabled_toolsets)
    names.difference_update(_resolve_tool_names(disabled_toolsets))
    return names


def validate_beta_tool_policy(
    enabled_toolsets: Iterable[str] = BETA_ENABLED_TOOLSETS,
    disabled_toolsets: Iterable[str] = BETA_DISABLED_TOOLSETS,
) -> None:
    exposed = effective_tool_names(enabled_toolsets, disabled_toolsets)
    forbidden = sorted(exposed & FORBIDDEN_BETA_TOOLS)
    if forbidden:
        raise ValueError(
            "KarinAI beta policy exposes forbidden tools: " + ", ".join(forbidden)
        )


def beta_policy_summary() -> dict[str, object]:
    exposed = sorted(effective_tool_names(BETA_ENABLED_TOOLSETS, BETA_DISABLED_TOOLSETS))
    return {
        "mode": "beta",
        "enabled_toolsets": list(BETA_ENABLED_TOOLSETS),
        "disabled_toolsets": list(BETA_DISABLED_TOOLSETS),
        "exposed_tools": exposed,
        "forbidden_tools": sorted(FORBIDDEN_BETA_TOOLS),
    }
