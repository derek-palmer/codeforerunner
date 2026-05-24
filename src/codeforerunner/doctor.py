"""`forerunner doctor` — single-screen health report. See SPEC.md §T35."""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from codeforerunner.config import CONFIG_FILENAME, ConfigError, load_from_repo

CANONICAL_REL = Path("agent/codeforerunner.skill.md")
SKILL_COPIES_REL: tuple[Path, ...] = (
    Path("plugins/codeforerunner/skills/codeforerunner/SKILL.md"),
    Path("skills/codeforerunner/SKILL.md"),
)
MARKETPLACE_REL = Path("plugins/codex/marketplace.json")

MARKER_BEGIN = "<!-- forerunner:begin managed=codeforerunner.skill -->"
MARKER_END = "<!-- forerunner:end -->"

_DEFAULT_PROVIDER_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "ollama": "OLLAMA_HOST",
}


@dataclass(frozen=True)
class Finding:
    severity: str  # "ok" | "warn" | "error"
    check: str
    message: str


def _installed_skill_destinations() -> list[Path]:
    home = Path(os.path.expanduser("~"))
    return [
        home / ".codex/skills/codeforerunner/SKILL.md",
        home / ".claude/plugins/codeforerunner/skills/codeforerunner/SKILL.md",
    ]


def _installed_marketplace_destination() -> Path:
    return Path(os.path.expanduser("~")) / ".codex/marketplaces/codeforerunner.json"


def _load_script_module(repo: Path, relpath: str, module_name: str):
    script_path = repo / relpath
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"cannot load {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _check_skill_body_parity(repo: Path) -> list[Finding]:
    try:
        skill_mod = _load_script_module(
            repo, "scripts/validate_skill_copies.py", "_forerunner_doctor_skill_copies"
        )
        strip_frontmatter: Callable[[str], str] = skill_mod.strip_frontmatter
    except Exception as exc:  # pragma: no cover - defensive
        return [Finding("error", "skill-body-parity", f"loader failure: {exc}")]

    canonical_path = repo / CANONICAL_REL
    if not canonical_path.is_file():
        return [
            Finding(
                "error",
                "skill-body-parity",
                f"canonical skill missing: {CANONICAL_REL}",
            )
        ]
    canonical_body = strip_frontmatter(canonical_path.read_text(encoding="utf-8"))

    findings: list[Finding] = []
    for rel in SKILL_COPIES_REL:
        p = repo / rel
        if not p.is_file():
            findings.append(
                Finding("error", "skill-body-parity", f"copy missing: {rel}")
            )
            continue
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        if body != canonical_body:
            findings.append(
                Finding("error", "skill-body-parity", f"body drift in {rel}")
            )
    if not findings:
        findings.append(
            Finding(
                "ok",
                "skill-body-parity",
                f"canonical body matches {len(SKILL_COPIES_REL)} distributed copies",
            )
        )
    return findings


def _check_codex_marketplace(repo: Path) -> list[Finding]:
    try:
        mp_mod = _load_script_module(
            repo,
            "scripts/validate_codex_marketplace.py",
            "_forerunner_doctor_codex_marketplace",
        )
        validate: Callable[[Path], list[str]] = mp_mod.validate
    except Exception as exc:  # pragma: no cover - defensive
        return [Finding("error", "codex-marketplace", f"loader failure: {exc}")]

    errors = validate(repo)
    if not errors:
        return [
            Finding("ok", "codex-marketplace", f"{MARKETPLACE_REL} validates")
        ]
    return [Finding("error", "codex-marketplace", msg) for msg in errors]


def _check_installed_destinations(repo: Path) -> list[Finding]:
    findings: list[Finding] = []

    for dest in _installed_skill_destinations():
        if not dest.exists():
            findings.append(
                Finding(
                    "ok",
                    "installed-destinations",
                    f"{dest}: not installed (skip)",
                )
            )
            continue
        try:
            text = dest.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append(
                Finding(
                    "warn",
                    "installed-destinations",
                    f"{dest}: unreadable ({exc})",
                )
            )
            continue
        if MARKER_BEGIN in text and MARKER_END in text:
            findings.append(
                Finding(
                    "ok",
                    "installed-destinations",
                    f"{dest}: managed (markers present)",
                )
            )
        else:
            findings.append(
                Finding(
                    "warn",
                    "installed-destinations",
                    f"{dest}: exists without managed-region markers (installer will refuse to overwrite)",
                )
            )

    mp_dest = _installed_marketplace_destination()
    if not mp_dest.exists():
        findings.append(
            Finding(
                "ok",
                "installed-destinations",
                f"{mp_dest}: not installed (skip)",
            )
        )
    else:
        src = repo / MARKETPLACE_REL
        try:
            installed = mp_dest.read_text(encoding="utf-8").rstrip()
            canonical = src.read_text(encoding="utf-8").rstrip()
        except OSError as exc:
            findings.append(
                Finding(
                    "warn",
                    "installed-destinations",
                    f"{mp_dest}: unreadable ({exc})",
                )
            )
        else:
            if installed == canonical:
                findings.append(
                    Finding(
                        "ok",
                        "installed-destinations",
                        f"{mp_dest}: matches {MARKETPLACE_REL}",
                    )
                )
            else:
                findings.append(
                    Finding(
                        "warn",
                        "installed-destinations",
                        f"{mp_dest}: drifted from {MARKETPLACE_REL}",
                    )
                )

    return findings


def _check_config_loadable(repo: Path) -> list[Finding]:
    cfg_path = repo / CONFIG_FILENAME
    if not cfg_path.is_file():
        return [
            Finding(
                "ok",
                "config-loadable",
                f"no {CONFIG_FILENAME}; check is a no-op",
            )
        ]
    try:
        load_from_repo(repo)
    except ConfigError as exc:
        return [Finding("error", "config-loadable", str(exc))]
    return [Finding("ok", "config-loadable", f"{CONFIG_FILENAME} parses cleanly")]


def _check_provider_api_key(repo: Path) -> list[Finding]:
    cfg_path = repo / CONFIG_FILENAME
    if not cfg_path.is_file():
        return [
            Finding(
                "ok",
                "provider-api-key",
                f"no {CONFIG_FILENAME}; provider key not checked",
            )
        ]
    try:
        cfg = load_from_repo(repo)
    except ConfigError:
        # config-loadable check will surface this; skip here
        return [
            Finding(
                "ok",
                "provider-api-key",
                "config unparseable; skipped (see config-loadable)",
            )
        ]
    if cfg is None:  # pragma: no cover - defensive
        return [
            Finding(
                "ok",
                "provider-api-key",
                f"no {CONFIG_FILENAME}; provider key not checked",
            )
        ]
    provider = cfg.provider
    if provider == "ollama":
        return [
            Finding(
                "ok",
                "provider-api-key",
                "ollama needs no API key (OLLAMA_HOST optional)",
            )
        ]
    env_var = cfg.api_key_env.get(provider) or _DEFAULT_PROVIDER_ENV.get(provider, "")
    if os.environ.get(env_var):
        return [Finding("ok", "provider-api-key", f"{provider}: {env_var} is set")]
    return [
        Finding(
            "warn",
            "provider-api-key",
            f"{provider}: ${env_var} is not set; `forerunner generate` will refuse to run",
        )
    ]


_STARTER_CONFIG = """\
# forerunner.config.yaml — generated by `forerunner doctor --fix`
# See https://github.com/derek-palmer/codeforerunner for docs.

enabled_rules:
  - R1-no-cli
  - R2-no-pre-commit
  - R3-no-ci
  - R4-no-installer
  - R5-no-python-package
  - R7-no-mcp
  - R8-no-marketplace
ignore_paths: []
"""


def starter_config() -> str:
    return _STARTER_CONFIG


def run(repo: Path) -> list[Finding]:
    repo = repo.resolve()
    findings: list[Finding] = []
    findings.extend(_check_skill_body_parity(repo))
    findings.extend(_check_codex_marketplace(repo))
    findings.extend(_check_installed_destinations(repo))
    findings.extend(_check_config_loadable(repo))
    findings.extend(_check_provider_api_key(repo))
    return findings


def format_report(findings: list[Finding]) -> str:
    lines = [f"[{f.severity}] {f.check}: {f.message}" for f in findings]
    counts = {"ok": 0, "warn": 0, "error": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    summary = (
        f"summary: {counts.get('ok', 0)} ok, "
        f"{counts.get('warn', 0)} warn, "
        f"{counts.get('error', 0)} error"
    )
    lines.append(summary)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="forerunner doctor",
        description="Single-screen health report for codeforerunner repo.",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="repo root (default: cwd)",
    )
    args = parser.parse_args(argv)

    findings = run(args.repo)
    print(format_report(findings))
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
