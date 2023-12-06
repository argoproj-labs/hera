"""The main entrypoint for hera CLI."""
from __future__ import annotations

from hera._cli import generate


def main():
    try:
        import typer
    except ImportError:
        raise ImportError("Use of the `hera` CLI tool requires installing the 'cli' extra, `pip install hera[cli]`.")

    app = typer.Typer()

    generate_app = typer.Typer()
    app.add_typer(
        generate_app,
        name="generate",
        help="Subcommands for converting to/from hera Workflows.",
    )

    register_yaml_command = generate_app.command("yaml")
    register_yaml_command(generate.yaml.generate_yaml)

    app()
