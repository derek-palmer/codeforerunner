"""Shared prompt resolution used by cli.py and mcp_server.py."""
from __future__ import annotations

from pathlib import Path


def _package_prompts() -> Path:
    """Return the path to the bundled prompts directory inside the package."""
    return Path(__file__).parent / "prompts"


def find_prompts_root(repo_arg: str | Path | None = None) -> Path:
    """Return the prompts root directory (parent of tasks/).

    Resolution order:
    1. {repo_arg}/prompts/ if given and contains tasks/
    2. Walk up from cwd looking for prompts/tasks/ (checkout compat)
    3. Package-bundled prompts (always available after pip install)
    """
    if repo_arg is not None:
        p = Path(repo_arg) / "prompts"
        if (p / "tasks").is_dir():
            return p
        raise FileNotFoundError(
            f"no prompts/tasks/ found under {str(repo_arg)!r}"
        )

    here = Path.cwd().resolve()
    parents = list(here.parents)
    for candidate in [here, *parents[:10]]:
        if (candidate / "prompts" / "tasks").is_dir():
            return candidate / "prompts"

    pkg = _package_prompts()
    if (pkg / "tasks").is_dir():
        return pkg

    raise FileNotFoundError(
        "could not find prompts/tasks/; specify --repo or reinstall the package"
    )


def resolve_bundle(prompts_root: Path, task: str) -> str:
    """Concatenate system/base.md + sorted partials/*.md + tasks/<task>.md."""
    task_path = prompts_root / "tasks" / f"{task}.md"
    if not task_path.is_file():
        raise FileNotFoundError(f"unknown task {task!r} (no {task_path})")

    parts: list[str] = []
    base = prompts_root / "system" / "base.md"
    if base.is_file():
        parts.append(f"<!-- system: base.md -->\n{base.read_text(encoding='utf-8').rstrip()}")

    partials_dir = prompts_root / "partials"
    if partials_dir.is_dir():
        for p in sorted(partials_dir.glob("*.md")):
            parts.append(f"<!-- partial: {p.name} -->\n{p.read_text(encoding='utf-8').rstrip()}")

    parts.append(f"<!-- task: {task_path.name} -->\n{task_path.read_text(encoding='utf-8').rstrip()}")
    return "\n\n".join(parts) + "\n"
