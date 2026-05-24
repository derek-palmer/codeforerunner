from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from codeforerunner.cli import main
from codeforerunner.providers import CompletionResult

REPO = Path(__file__).resolve().parents[1]


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
    rc = main(["--repo", str(REPO), "doc", "scan"])
    out = capsys.readouterr().out
    assert rc == 0
    scan_body = (REPO / "prompts" / "tasks" / "scan.md").read_text(encoding="utf-8")
    first_line = scan_body.splitlines()[0]
    assert first_line in out
    assert "<!-- task: scan.md -->" in out


def test_doc_unknown_task_exits_nonzero(capsys):
    rc = main(["--repo", str(REPO), "doc", "definitely-not-a-task"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "unknown task" in err


@pytest.mark.parametrize(
    "cmd,task_file",
    [("init", "init-agent-onboarding.md"), ("scan", "scan.md")],
)
def test_init_scan_resolve_bundle(cmd, task_file, capsys):
    rc = main(["--repo", str(REPO), cmd])
    out = capsys.readouterr().out
    assert rc == 0
    assert f"<!-- task: {task_file} -->" in out
    body = (REPO / "prompts" / "tasks" / task_file).read_text(encoding="utf-8")
    assert body.splitlines()[0] in out


def test_init_agents_only_matches_default(capsys):
    rc = main(["--repo", str(REPO), "init", "--agents-only"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "<!-- task: init-agent-onboarding.md -->" in out
    assert "<!-- task: scan.md -->" not in out


def test_init_full_prepends_scan(capsys):
    rc = main(["--repo", str(REPO), "init", "--full"])
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
        main(["--repo", str(REPO), "init", "--full", "--agents-only"])


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


def test_scan_prints_env_hint(tmp_path, capsys):
    _seed_repo_with_config(tmp_path)
    rc = main(["--repo", str(tmp_path), "scan"])
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

        def complete(self, *, prompt, model=None, api_key=None):
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

        def complete(self, *, prompt, model=None, api_key=None):  # pragma: no cover
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

        def complete(self, *, prompt, model=None, api_key=None):
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

        def complete(self, *, prompt, model=None, api_key=None):
            calls.append({"model": model})
            return CompletionResult(text="ok", model=model or "default-model")

    monkeypatch.setitem(providers.REGISTRY, "fake", FakeProvider)
    monkeypatch.setenv("FAKE_API_KEY", "secret")

    rc = main(["--repo", str(tmp_path), "generate", "readme", "--provider", "fake", "--model", "custom-v2"])
    assert rc == 0
    assert calls == [{"model": "custom-v2"}]


def test_check_with_violations_exits_one(tmp_path, capsys):
    (tmp_path / "prompts" / "tasks").mkdir(parents=True)
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
    (tmp_path / "prompts" / "tasks").mkdir(parents=True)
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

        def complete(self, *, prompt, model=None, api_key=None):
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
