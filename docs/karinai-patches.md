# KarinAI patch log

This fork tracks upstream NousResearch Hermes Agent while carrying KarinAI-specific integration work.

Upstream remote:

- https://github.com/NousResearch/hermes-agent

Local remotes expected in this clone:

- origin: git@github.com:Bambak-org/karinai-agent.git
- upstream: https://github.com/NousResearch/hermes-agent.git

## Patch policy

- Keep KarinAI-specific code isolated under `karinai/`, runtime packaging/config directories, or clearly named docs whenever possible.
- If a core Hermes file must change, document the reason here before or in the same commit.
- Mark each core patch as either upstreamable, temporary, or permanent product-specific behavior.
- Prefer small commits that are easy to rebase or merge across upstream updates.

## Current KarinAI-specific changes

Initial fork setup and managed-runtime scaffolding:

- Added this patch log.
- Added `docs/karinai-runtime-notes.md`.
- Added `docs/karinai-runtime-contract.md`.
- Added `docs/karinai-prompt-branding.md`.
- Added `karinai/README.md`.
- Added `karinai/runtime/` managed runtime config, prompt rendering, startup, and tool-policy helpers.
- Added `karinai/prompts/system.base.md.j2`.
- Added `karinai/config/managed-runtime.env.example` and `karinai/config/tool-policy.beta.yaml`.
- Added `karinai/scripts/` prompt rendering and branding audit helpers.
- Added `tests/karinai/test_managed_runtime.py`.

## Core upstream file patches

### `agent/system_prompt.py`

Status: permanent product-specific behavior unless upstream later grows a generic branding/prompt-template hook.

Reason: KarinAI managed mode must present product-facing identity and policy from KarinAI templates, not the upstream default “You are Hermes Agent…” identity or user-editable `SOUL.md`. The patch is gated by `KARINAI_MANAGED_RUNTIME`; normal upstream Hermes behavior is unchanged when the env flag is absent.

Behavior:

- In managed mode, render the KarinAI system prompt from `karinai/prompts/system.base.md.j2`.
- Do not let user-editable `SOUL.md` override managed product policy.
- Do not inject upstream Hermes help/profile guidance into the product-facing managed prompt.

### `gateway/platforms/api_server.py`

Status: temporary/product-specific bridge until a generic managed-runtime/platform-policy hook exists upstream.

Reason: KarinAI runtime-manager must control the beta tool policy for private `/v1/runs` containers instead of trusting user-editable platform tool config. The patch is gated by `KARINAI_MANAGED_RUNTIME`; normal API server toolset resolution is unchanged otherwise.

Behavior:

- In managed mode, use `karinai.runtime.managed_agent_toolsets()` for `AIAgent.enabled_toolsets` and `AIAgent.disabled_toolsets`.
- Outside managed mode, keep the existing `platform_toolsets.api_server`/`hermes-api-server` resolution.

## Upstream sync checklist

1. Confirm the tree is clean or commit/stash local KarinAI work first.
2. `git fetch upstream main`
3. Review upstream changes before merging into the KarinAI branch.
4. Prefer `git merge --no-edit upstream/main` on the public product branch so sync points stay explicit.
5. Resolve conflicts in the smallest possible patches.
6. Run targeted tests around API server `/v1/runs`, Docker/runtime startup, tool policy, cron/scheduler behavior, prompt rendering, and any touched files.
7. Run KarinAI product tests under `tests/karinai/` once they exist.
8. Update this file only if KarinAI patches change.
