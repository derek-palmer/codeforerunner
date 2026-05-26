from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import codeforerunner
import pytest

from codeforerunner.cli import main
from codeforerunner.providers import CompletionResult

REPO = Path(__file__).resolve().parents[1]
# Prompts are bundled inside the package; use the installed path.
PROMPTS = Path(codeforerunner.__file__).parent / "prompts"


def test_help_exit_zero():
    proc = subprocess.run(
        [sys.executable, "-m", "codeforerunner.cli", "--help"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "forerunner" in proc.stdout


def test_doc_scan_emits_task_body(capsys):
    rc = main(["doc", "scan"])
    out = capsys.readouterr().out
    assert rc == 0
    scan_body = (PROMPTS / "tasks" / "scan.md").read_text(encoding="utf-8")
    first_line = scan_body.splitlines()[0]
    assert first_line in out
    assert "<!-- task: scan.md -->" in out


def test_doc_unknown_task_exits_nonzero(capsys):
    rc = main(["doc", "definitely-not-a-task"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "unknown task" in err


@pytest.mark.parametrize(
    "cmd,task_file",
    [("init", "init-agent-onboarding.md"), ("scan", "scan.md")],
)
def test_init_scan_resolve_bundle(cmd, task_file, capsys):
    rc = main([cmd])
    out = capsys.readouterr().out
    assert rc == 0
    assert f"<!-- task: {task_file} -->" in out
    body = (PROMPTS / "tasks" / task_file).read_text(encoding="utf-8")
    assert body.splitlines()[0] in out


def test_init_agents_only_matches_default(capsys):
    rc = main(["init", "--agents-only"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "<!-- task: init-agent-onboarding.md -->" in out
    assert "<!-- task: scan.md -->" not in out


def test_init_full_prepends_scan(capsys):
    rc = main(["init", "--full"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "section 1/2 (scan)" in out
    assert "<!-- task: scan.md -->" in out
    assert "section 2/2 (onboarding)" in out
    assert "<!-- task: init-agent-onboarding.md -->" in out
    assert out.index("<!-- task: scan.md -->") < out.index(
        "<!-- task: init-agent-onboarding.md -->"
    )


def test_init_full_and_agents_only_mutually_exclusive(capsys):
    with pytest.raises(SystemExit):
        main(["init", "--full", "--agents-only"])


def _seed_repo_with_config(tmp_path):
    (tmp_path / "prompts/system").mkdir(parents=True)
    (tmp_path / "prompts/system/base.md").write_text("# base\n", encoding="utf-8")
    (tmp_path / "prompts/partials").mkdir()
    (tmp_path / "prompts/tasks").mkdir()
    (tmp_path / "prompts/tasks/readme.md").write_text("# readme task\n", encoding="utf-8")
    (tmp_path / "prompts/tasks/scan.md").write_text("# scan task\n", encoding="utf-8")
    (tmp_path / "prompts/tasks/init-agent-onboarding.md").write_text(
        "# onboarding\n", encoding="utf-8"
    )
    (tmp_path / "forerunner.config.yaml").write_text("", encoding="utf-8")


def test_doc_non_exempt_with_config_warns_without_env(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    monkeypatch.delenv("FORERUNNER_SCAN_DONE", raising=False)
    rc = main(["--repo", str(tmp_path), "doc", "readme"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "scan-first" in cap.err
    assert "FORERUNNER_SCAN_DONE" in cap.err


def test_doc_non_exempt_with_env_set_no_warning(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    monkeypatch.setenv("FORERUNNER_SCAN_DONE", "1")
    rc = main(["--repo", str(tmp_path), "doc", "readme"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "scan-first" not in cap.err


def test_doc_exempt_task_no_warning(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    monkeypatch.delenv("FORERUNNER_SCAN_DONE", raising=False)
    rc = main(["--repo", str(tmp_path), "doc", "scan"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "scan-first" not in cap.err


def test_doc_without_config_no_warning(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    monkeypatch.delenv("FORERUNNER_SCAN_DONE", raising=False)
    rc = main(["--repo", str(tmp_path), "doc", "readme"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "scan-first" not in cap.err


def test_version_flag_prints_package_version(capsys):
    from codeforerunner import __version__
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    cap = capsys.readouterr()
    assert __version__ in cap.out


def test_scan_prints_env_hint(capsys):
    rc = main(["scan"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "FORERUNNER_SCAN_DONE" in cap.err


def test_check_no_config_exits_zero(tmp_path, capsys):
    rc = main(["--repo", str(tmp_path), "check"])
    assert rc == 0


def test_generate_calls_provider_with_resolved_bundle(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    calls: list[dict] = []

    class FakeProvider:
        default_env_var = "FAKE_API_KEY"
        default_model = "fake-default"

        def generate(self, *, prompt, model=None, api_key=None):
            calls.append({"prompt": prompt, "model": model, "api_key": api_key})
            return CompletionResult(text="generated text", model=model or "fake-default")

    from codeforerunner import providers

    monkeypatch.setitem(providers.REGISTRY, "fake", FakeProvider)
    monkeypatch.setenv("FAKE_API_KEY", "secret")

    rc = main(["--repo", str(tmp_path), "generate", "readme", "--provider", "fake"])
    cap = capsys.readouterr()

    assert rc == 0
    assert cap.out == "generated text\n"
    assert "# fake fake-default" in cap.err
    assert calls == [
        {
            "prompt": "<!-- system: base.md -->\n# base\n\n<!-- task: readme.md -->\n# readme task\n",
            "model": "fake-default",
            "api_key": "secret",
        }
    ]


def test_generate_missing_api_key_exits_three(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()

    class FakeProvider:
        default_env_var = "FAKE_API_KEY"
        default_model = "fake-default"

        def generate(self, *, prompt, model=None, api_key=None):  # pragma: no cover
            raise AssertionError("provider should not be called without API key")

    from codeforerunner import providers

    monkeypatch.setitem(providers.REGISTRY, "fake", FakeProvider)
    monkeypatch.delenv("FAKE_API_KEY", raising=False)

    rc = main(["--repo", str(tmp_path), "generate", "readme", "--provider", "fake"])
    cap = capsys.readouterr()

    assert rc == 3
    assert "missing API key" in cap.err


def test_generate_provider_error_exits_four(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    from codeforerunner import providers
    from codeforerunner.providers import ProviderError

    class FakeProvider:
        default_env_var = "FAKE_API_KEY"
        default_model = "fake-default"

        def generate(self, *, prompt, model=None, api_key=None):
            raise ProviderError("quota exceeded")

    monkeypatch.setitem(providers.REGISTRY, "fake", FakeProvider)
    monkeypatch.setenv("FAKE_API_KEY", "secret")

    rc = main(["--repo", str(tmp_path), "generate", "readme", "--provider", "fake"])
    cap = capsys.readouterr()

    assert rc == 4
    assert "quota exceeded" in cap.err


def test_generate_model_override(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    calls: list[dict] = []
    from codeforerunner import providers
    from codeforerunner.providers import CompletionResult

    class FakeProvider:
        default_env_var = "FAKE_API_KEY"
        default_model = "default-model"

        def generate(self, *, prompt, model=None, api_key=None):
            calls.append({"model": model})
            return CompletionResult(text="ok", model=model or "default-model")

    monkeypatch.setitem(providers.REGISTRY, "fake", FakeProvider)
    monkeypatch.setenv("FAKE_API_KEY", "secret")

    rc = main(["--repo", str(tmp_path), "generate", "readme", "--provider", "fake", "--model", "custom-v2"])
    assert rc == 0
    assert calls == [{"model": "custom-v2"}]


def test_check_with_violations_exits_one(tmp_path, capsys):
    (tmp_path / "README.md").write_text("no CLI exists\n", encoding="utf-8")
    (tmp_path / "src" / "codeforerunner").mkdir(parents=True)
    (tmp_path / "src" / "codeforerunner" / "cli.py").write_text("# cli\n", encoding="utf-8")
    (tmp_path / "forerunner.config.yaml").write_text(
        "enabled_rules:\n  - R1-no-cli\n", encoding="utf-8"
    )
    rc = main(["--repo", str(tmp_path), "check"])
    cap = capsys.readouterr()
    assert rc == 1
    assert "R1-no-cli" in cap.err


def test_check_invalid_config_exits_two(tmp_path, capsys):
    (tmp_path / "forerunner.config.yaml").write_text(
        "provider: unknown_xyz\n", encoding="utf-8"
    )
    rc = main(["--repo", str(tmp_path), "check"])
    cap = capsys.readouterr()
    assert rc == 2
    assert "invalid config" in cap.err


def test_generate_uses_config_api_key_env_override(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").write_text(
        "provider: anthropic\napi_key_env:\n  anthropic: MY_ANTHROPIC_KEY\n",
        encoding="utf-8",
    )
    calls: list[dict] = []

    class FakeAnthropicProvider:
        default_env_var = "ANTHROPIC_API_KEY"
        default_model = "fake-claude"

        def generate(self, *, prompt, model=None, api_key=None):
            calls.append({"model": model, "api_key": api_key})
            return CompletionResult(text="ok", model=model or "fake-claude")

    from codeforerunner import providers

    monkeypatch.setitem(providers.REGISTRY, "anthropic", FakeAnthropicProvider)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("MY_ANTHROPIC_KEY", "override-secret")

    rc = main(["--repo", str(tmp_path), "generate", "readme"])
    cap = capsys.readouterr()

    assert rc == 0
    assert cap.out == "ok\n"
    assert calls == [{"model": "claude-opus-4-7", "api_key": "override-secret"}]


# ── Ollama local-mode fallback ─────────────────────────────────────────────────

def test_generate_falls_back_to_ollama_when_no_key_and_ollama_running(
    tmp_path, capsys, monkeypatch
):
    """No explicit provider, no API key, Ollama reachable → auto-switch to Ollama."""
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    calls: list[dict] = []

    class FakeOllamaProvider:
        default_env_var = "OLLAMA_HOST"
        default_model = "llama3"

        def generate(self, *, prompt, model=None, api_key=None):
            calls.append({"model": model, "api_key": api_key})
            return CompletionResult(text="ollama output", model=model or "llama3")

    from codeforerunner import providers
    from unittest.mock import patch

    monkeypatch.setitem(providers.REGISTRY, "ollama", FakeOllamaProvider)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with patch("codeforerunner.providers.ollama_available", return_value=True):
        rc = main(["--repo", str(tmp_path), "generate", "readme"])

    cap = capsys.readouterr()
    assert rc == 0
    assert "local mode" in cap.err
    assert cap.out == "ollama output\n"
    assert calls[0]["model"] == "llama3"


def test_generate_no_fallback_when_provider_explicit_and_key_missing(
    tmp_path, capsys, monkeypatch
):
    """Explicit --provider means no auto-fallback even if Ollama is running."""
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()

    class FakeProvider:
        default_env_var = "FAKE_API_KEY"
        default_model = "fake-default"

        def generate(self, *, prompt, model=None, api_key=None):  # pragma: no cover
            raise AssertionError("should not be called")

    from codeforerunner import providers
    from unittest.mock import patch

    monkeypatch.setitem(providers.REGISTRY, "fake", FakeProvider)
    monkeypatch.delenv("FAKE_API_KEY", raising=False)

    with patch("codeforerunner.providers.ollama_available", return_value=True):
        rc = main(["--repo", str(tmp_path), "generate", "readme", "--provider", "fake"])

    cap = capsys.readouterr()
    assert rc == 3
    assert "missing API key" in cap.err


def test_generate_no_fallback_when_config_provider_set_and_key_missing(
    tmp_path, capsys, monkeypatch
):
    """Provider in config file counts as explicit — no auto-fallback."""
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").write_text(
        "provider: anthropic\n", encoding="utf-8"
    )

    from unittest.mock import patch

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with patch("codeforerunner.providers.ollama_available", return_value=True):
        rc = main(["--repo", str(tmp_path), "generate", "readme"])

    cap = capsys.readouterr()
    assert rc == 3
    assert "missing API key" in cap.err


def test_generate_no_key_no_ollama_no_explicit_provider_emits_bundle(
    tmp_path, capsys, monkeypatch
):
    """No explicit provider, no API key, Ollama not running → skill-mode auto-detect:
    emit bundle to stdout and return 0 (the calling agent is the model)."""
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()

    from unittest.mock import patch

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with patch("codeforerunner.providers.ollama_available", return_value=False):
        rc = main(["--repo", str(tmp_path), "generate", "readme"])

    cap = capsys.readouterr()
    assert rc == 0
    assert "system: base.md" in cap.out


def test_generate_ollama_fallback_uses_explicit_model(tmp_path, capsys, monkeypatch):
    """--model flag is preserved when falling back to Ollama."""
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    calls: list[dict] = []

    class FakeOllamaProvider:
        default_env_var = "OLLAMA_HOST"
        default_model = "llama3"

        def generate(self, *, prompt, model=None, api_key=None):
            calls.append({"model": model})
            return CompletionResult(text="ok", model=model or "llama3")

    from codeforerunner import providers
    from unittest.mock import patch

    monkeypatch.setitem(providers.REGISTRY, "ollama", FakeOllamaProvider)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with patch("codeforerunner.providers.ollama_available", return_value=True):
        rc = main(["--repo", str(tmp_path), "generate", "readme", "--model", "llama3.2"])

    assert rc == 0
    assert calls[0]["model"] == "llama3.2"


# ── --prompt-only and skill-mode auto-detect ─────────────────────────────────

def test_generate_prompt_only_outputs_bundle_without_api_call(tmp_path, capsys, monkeypatch):
    """--prompt-only emits the bundle and returns 0; no model is invoked."""
    _seed_repo_with_config(tmp_path)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("FORERUNNER_SCAN_DONE", "1")  # silence scan-first warning

    rc = main(["--repo", str(tmp_path), "generate", "--prompt-only", "readme"])

    cap = capsys.readouterr()
    assert rc == 0
    assert "system: base.md" in cap.out
    assert "missing API key" not in cap.err  # no provider error messages


def test_generate_prompt_only_scan_task(tmp_path, capsys, monkeypatch):
    """--prompt-only works for the scan task (scan is exempt from scan-first warning)."""
    _seed_repo_with_config(tmp_path)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    rc = main(["--repo", str(tmp_path), "generate", "--prompt-only", "scan"])

    cap = capsys.readouterr()
    assert rc == 0
    assert "scan task" in cap.out  # stub scan.md content present


def test_generate_skill_mode_autodetect_no_tty(tmp_path, capsys, monkeypatch):
    """No key + no Ollama + no explicit provider + non-TTY stdout → bundle emitted cleanly."""
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()

    from unittest.mock import patch

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with patch("codeforerunner.providers.ollama_available", return_value=False):
        rc = main(["--repo", str(tmp_path), "generate", "readme"])

    cap = capsys.readouterr()
    assert rc == 0
    assert "system: base.md" in cap.out
    # Non-TTY: no "info:" message on stderr
    assert "info:" not in cap.err


def test_generate_explicit_provider_no_key_still_errors(tmp_path, capsys, monkeypatch):
    """Explicit --provider with no key → error (not silent bundle output)."""
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()

    from unittest.mock import patch

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with patch("codeforerunner.providers.ollama_available", return_value=False):
        rc = main(["--repo", str(tmp_path), "generate", "--provider", "anthropic", "readme"])

    cap = capsys.readouterr()
    assert rc == 3
    assert "missing API key" in cap.err


def test_generate_stream_flag_yields_chunks(tmp_path, capsys, monkeypatch):
    """--stream calls provider.stream() and writes chunks to stdout."""
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    chunks = ["hello", " ", "world"]

    class FakeProvider:
        default_env_var = "FAKE_API_KEY"
        default_model = "fake-stream"

        def stream(self, *, prompt, model=None, api_key=None):
            yield from chunks

    from codeforerunner import providers

    monkeypatch.setitem(providers.REGISTRY, "fake", FakeProvider)
    monkeypatch.setenv("FAKE_API_KEY", "secret")

    rc = main(["--repo", str(tmp_path), "generate", "--provider", "fake", "--stream", "readme"])
    cap = capsys.readouterr()

    assert rc == 0
    assert cap.out == "hello world\n"


# ── Error / edge paths ────────────────────────────────────────────────────────

def test_get_bundle_error_when_repo_has_no_prompts(tmp_path, capsys):
    rc = main(["--repo", str(tmp_path), "doc", "scan"])
    cap = capsys.readouterr()
    assert rc == 2
    assert "error:" in cap.err


def test_get_bundle_catches_resolve_bundle_error(tmp_path, capsys, monkeypatch):
    from unittest.mock import patch
    _seed_repo_with_config(tmp_path)
    with patch("codeforerunner.cli._resolve_bundle", side_effect=FileNotFoundError("gone")):
        rc = main(["--repo", str(tmp_path), "doc", "readme"])
    cap = capsys.readouterr()
    assert rc == 2
    assert "error:" in cap.err


def test_cmd_init_full_exits_when_scan_fails(tmp_path, capsys):
    # no prompts/tasks in tmp_path → scan bundle lookup fails → early return
    rc = main(["--repo", str(tmp_path), "init", "--full"])
    capsys.readouterr()
    assert rc == 2


def test_cmd_mcp_server_bad_repo_exits_two(tmp_path, capsys):
    rc = main(["--repo", str(tmp_path), "mcp-server"])
    cap = capsys.readouterr()
    assert rc == 2
    assert "mcp_server:" in cap.err


def test_cmd_mcp_server_success_path(capsys):
    from unittest.mock import patch
    with patch("codeforerunner.mcp_server.serve", return_value=0) as mock_serve:
        rc = main(["mcp-server"])
    capsys.readouterr()
    assert rc == 0
    mock_serve.assert_called_once()


def test_generate_exits_when_bundle_not_found(tmp_path, capsys, monkeypatch):
    # no prompts in tmp_path → _get_bundle returns rc=2
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    rc = main(["--repo", str(tmp_path), "generate", "readme"])
    capsys.readouterr()
    assert rc == 2


def test_generate_stream_error_exits_four(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    from codeforerunner import providers
    from codeforerunner.providers import ProviderError

    class FakeProvider:
        default_env_var = "FAKE_API_KEY"
        default_model = "fake-stream"

        def stream(self, *, prompt, model=None, api_key=None):
            raise ProviderError("stream failed")

    monkeypatch.setitem(providers.REGISTRY, "fake", FakeProvider)
    monkeypatch.setenv("FAKE_API_KEY", "secret")

    rc = main(["--repo", str(tmp_path), "generate", "--provider", "fake", "--stream", "readme"])
    cap = capsys.readouterr()
    assert rc == 4
    assert "stream failed" in cap.err


def test_generate_skill_mode_tty_prints_info(tmp_path, monkeypatch):
    import io as _io
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    fake_out = _io.StringIO()
    fake_err = _io.StringIO()

    class _FakeTTYStdout:
        def write(self, s):
            fake_out.write(s)
        def isatty(self):
            return True
        def flush(self):
            pass

    from unittest.mock import patch
    with patch("codeforerunner.providers.ollama_available", return_value=False), \
         patch("sys.stdout", _FakeTTYStdout()), \
         patch("sys.stderr", fake_err):
        rc = main(["--repo", str(tmp_path), "generate", "readme"])

    assert rc == 0
    assert "info:" in fake_err.getvalue()
