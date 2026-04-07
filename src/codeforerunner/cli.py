"""CLI entrypoint for the forerunner command."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from codeforerunner import __version__

CONFIG_FILENAME = "forerunner.config.yaml"


def _placeholder_command(args: argparse.Namespace) -> int:
    print(f"`forerunner {args.command_path}` is not implemented yet.", file=sys.stderr)
    return 1


def _add_placeholder_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    name: str,
    help_text: str,
    *,
    command_path: str | None = None,
) -> argparse.ArgumentParser:
    command_parser = subparsers.add_parser(name, help=help_text)
    command_parser.set_defaults(
        handler=_placeholder_command,
        parser=command_parser,
        command_path=command_path or name,
    )
    return command_parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forerunner",
        description="Generate and maintain repository documentation artifacts.",
        epilog=f"Default configuration file: {CONFIG_FILENAME}",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    _add_placeholder_command(
        subparsers,
        "init",
        "Bootstrap documentation generation for the current repository.",
    )
    _add_placeholder_command(
        subparsers,
        "generate",
        "Generate repository documentation artifacts.",
    )
    _add_placeholder_command(
        subparsers,
        "check",
        "Check whether generated documentation is stale.",
    )
    _add_placeholder_command(
        subparsers,
        "review",
        "Review pending documentation changes.",
    )

    hook_parser = subparsers.add_parser("hook", help="Manage workflow hook integration.")
    hook_parser.set_defaults(parser=hook_parser)
    hook_subparsers = hook_parser.add_subparsers(dest="hook_command")
    _add_placeholder_command(
        hook_subparsers,
        "install",
        "Install the documentation enforcement hook.",
        command_path="hook install",
    )

    config_parser = subparsers.add_parser("config", help="Manage forerunner configuration.")
    config_parser.set_defaults(parser=config_parser)
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    _add_placeholder_command(
        config_subparsers,
        "init",
        f"Create a starter {CONFIG_FILENAME} file.",
        command_path="config init",
    )

    adapters_parser = subparsers.add_parser("adapters", help="Inspect configured model adapters.")
    adapters_parser.set_defaults(parser=adapters_parser)
    adapters_subparsers = adapters_parser.add_subparsers(dest="adapters_command")
    _add_placeholder_command(
        adapters_subparsers,
        "list",
        "List available model adapters.",
        command_path="adapters list",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()

    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        return 1

    selected_parser = getattr(args, "parser", parser)
    handler = getattr(args, "handler", None)

    if handler is None:
        selected_parser.print_help()
        return 0

    return int(handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
