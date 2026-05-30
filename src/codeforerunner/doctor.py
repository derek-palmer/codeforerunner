"""`forerunner doctor` — single-screen health report."""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from codeforerunner import distribution as _dist
from codeforerunner import skill_parity as _parity
from codeforerunner.config import CONFIG_FILENAME, ConfigError, load_from_repo

# Distribution artifact identity and markers come from the Distribution
# Inventory; re-exported here for callers/tests that import them off doctor.
CANONICAL_REL = _dist.CANONICAL_SKILL_REL
SKILL_COPIES_REL: tuple[Path, ...] = _dist.DISTRIBUTED_SKILL_COPIES_REL
MARKETPLACE_REL = _dist.MARKETPLACE_MANIFEST_REL

MARKER_BEGIN = _dist.MARKER_BEGIN
MARKER_END = _dist.MARKER_END


@dataclass(frozen=True)
class Finding:
    """Single health-check result with severity, check name, and human message."""

    severity: str  # "ok" | "warn" | "error"
    check: str
    message: str


def _installed_skill_destinations() -> list[Path]:
    """Return default install paths for the codeforerunner skill across supported agents."""
    home = Path(os.path.expanduser("~"))
    return [
        _dist.skill_destination(agent, "codeforerunner", home)
        for agent in _dist.SKILL_DEST_AGENTS
    ]


def _installed_marketplace_destination() -> Path:
    """Return default install path for the Codex marketplace manifest."""
    return _dist.marketplace_destination(Path(os.path.expanduser("~")))


def _load_script_module(repo: Path, relpath: str, module_name: str):
    """Load a Python script from the repo as a module with a unique name to avoid cache collisions."""
    # L3: unique name prevents stale cached module on repeated calls
    unique_name = f"{module_name}_{uuid.uuid4().hex}"
    script_path = repo / relpath
    spec = importlib.util.spec_from_file_location(unique_name, script_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"cannot load {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[unique_name] = module
    spec.loader.exec_module(module)
    return module


def _check_skill_body_parity(repo: Path, run_scripts: bool = False) -> list[Finding]:
    """Verify that all distributed skill copies match the canonical body.

    Body parity is owned by the Skill Body Parity module, which only reads
    files (no target-repo code is executed), so this runs regardless of
    ``run_scripts`` — that flag still gates checks that load repo scripts.
    """
    result = _parity.check_skill_body_parity(repo)
    if result.missing_canonical:
        return [
            Finding(
                "error",
                "skill-body-parity",
                f"canonical skill missing: {CANONICAL_REL}",
            )
        ]

    findings: list[Finding] = []
    for rel in result.missing_copies:
        findings.append(Finding("error", "skill-body-parity", f"copy missing: {rel}"))
    for rel in result.drifted_copies:
        findings.append(Finding("error", "skill-body-parity", f"body drift in {rel}"))
    if not findings:
        findings.append(
            Finding(
                "ok",
                "skill-body-parity",
                f"canonical body matches {len(SKILL_COPIES_REL)} distributed copies",
            )
        )
    return findings


def _check_codex_marketplace(repo: Path, run_scripts: bool = False) -> list[Finding]:
    """Validate the Codex marketplace manifest using the repo validation script."""
    if not run_scripts:
        return [
            Finding(
                "warn",
                "codex-marketplace",
                "skipping script validation (pass --run-scripts to allow executing repo scripts)",
            )
        ]
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
    """Check whether installed skill and marketplace files are present and managed."""
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
    """Try parsing forerunner.config.yaml; report error finding on ConfigError."""
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


_STARTER_CONFIG = """\
# forerunner.config.yaml — generated by `forerunner doctor --fix`
# See https://github.com/derek-palmer/codeforerunner for docs.

tasks:
  check:
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
    """Return the default forerunner.config.yaml content written by --fix."""
    return _STARTER_CONFIG


def run(repo: Path, run_scripts: bool = False) -> list[Finding]:
    """Run all health checks against *repo* and return findings."""
    repo = repo.resolve()
    findings: list[Finding] = []
    findings.extend(_check_skill_body_parity(repo, run_scripts=run_scripts))
    findings.extend(_check_codex_marketplace(repo, run_scripts=run_scripts))
    findings.extend(_check_installed_destinations(repo))
    findings.extend(_check_config_loadable(repo))
    return findings


def format_report(findings: list[Finding]) -> str:
    """Format findings as a human-readable report string with a summary line."""
    lines = [f"[{f.severity}] {f.check}: {f.message}" for f in findings]
    counts: dict[str, int] = {"ok": 0, "warn": 0, "error": 0}
    for f in findings:
        counts[f.severity] += 1
    summary = f"summary: {counts['ok']} ok, {counts['warn']} warn, {counts['error']} error"
    lines.append(summary)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Entry point for `forerunner doctor`; returns 1 when any finding is an error."""
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
    parser.add_argument(
        "--run-scripts",
        action="store_true",
        default=False,
        help="allow executing Python scripts from the target repo (off by default for safety)",
    )
    args = parser.parse_args(argv)

    findings = run(args.repo, run_scripts=args.run_scripts)
    print(format_report(findings))
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
