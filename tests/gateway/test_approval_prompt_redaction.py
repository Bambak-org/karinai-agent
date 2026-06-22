"""Regression test for approval prompt credential redaction (issue #48456).

When Tirith flags a command for containing a credential-shaped pattern, the
gateway approval prompt must redact the credential from the command text
before sending it to the chat platform. Without this fix, the raw command
(with the credential in plaintext) is sent verbatim to Telegram/Discord/etc.,
undoing Tirith's redaction one layer up.

The redaction is wired through the module-level ``_redact_approval_command``
seam (the actual call site, ``_approval_notify_sync``, is a deeply nested
gateway closure that cannot be driven in a unit test). These tests bind that
seam — the production wiring — not just the underlying ``redact_sensitive_text``
helper, so they fail if the redaction call is removed from the approval path.
"""

import re

import pytest

from gateway.run import _redact_approval_command


class TestRedactApprovalCommand:
    """Contract for the approval-prompt redaction seam used by the gateway."""

    def test_redacts_github_pat(self):
        raw = "curl -H 'Authorization: token ghp_0123456789abcdefghijABCDEFGHIJ0123456789' https://api.github.com/user"
        out = _redact_approval_command(raw)
        assert "ghp_0123456789abcdefghijABCDEFGHIJ0123456789" not in out
        # command structure preserved so the operator can still judge the action
        assert "curl" in out
        assert "github.com" in out

    def test_redacts_openai_key(self):
        raw = "export OPENAI_API_KEY=sk-proj-ABCdef0123456789ABCdef0123456789ABCdef01 && python s.py"
        out = _redact_approval_command(raw)
        assert "sk-proj-ABCdef0123456789ABCdef0123456789ABCdef01" not in out
        assert "python s.py" in out

    def test_redacts_bearer_token(self):
        raw = "curl -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig' https://api.example.com"
        out = _redact_approval_command(raw)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig" not in out

    def test_clean_command_passes_through_unchanged(self):
        raw = "ls -la /tmp && echo hello"
        assert _redact_approval_command(raw) == raw

    def test_forces_redaction_even_when_disabled(self, monkeypatch):
        """force=True must redact even if security.redact_secrets is off — the
        approval prompt is a hard secret-egress boundary regardless of config."""
        raw = "curl -H 'Authorization: token ghp_0123456789abcdefghijABCDEFGHIJ0123456789' https://api.github.com"
        # With redaction globally disabled, the seam must STILL redact (force=True).
        monkeypatch.setattr("agent.redact._REDACT_ENABLED", False, raising=False)
        out = _redact_approval_command(raw)
        assert "ghp_0123456789abcdefghijABCDEFGHIJ0123456789" not in out

    def test_handles_none_and_empty(self):
        assert _redact_approval_command("") == ""
        assert _redact_approval_command(None) == ""


class TestApprovalCommandWiring:
    """Guard the production wiring: _approval_notify_sync must route the command
    through _redact_approval_command BEFORE any send, so neither the button path
    (send_exec_approval) nor the plain-text fallback emits the raw command."""

    def test_approval_notify_sync_redacts_before_send(self):
        import inspect
        import gateway.run as run

        src = inspect.getsource(run)
        # Locate the closure body.
        start = src.index("def _approval_notify_sync(")
        body = src[start:start + 4000]

        # The command is read, then redacted via the seam, and only THEN used.
        read_idx = body.index('approval_data.get("command"')
        redact_idx = body.index("_redact_approval_command(")
        assert redact_idx > read_idx, "command must be read before redaction"

        # The redaction must precede the first send that carries the command.
        send_idx = body.index("send_exec_approval(")
        assert redact_idx < send_idx, (
            "command must be redacted before send_exec_approval receives it"
        )
