from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cappa import Arg, Subcommands, command
from typing_extensions import Annotated


@dataclass
class Hera:
    subcommand: Subcommands[Generate]


@command(help="Subcommands for converting to/from hera Workflows.")
@dataclass
class Generate:
    subcommand: Subcommands[GenerateYaml]


@command(
    name="yaml",
    help="Generate yaml from python Workflow definitions.",
    invoke="hera._cli.generate.yaml.generate_yaml",
)
class GenerateYaml:
    from_: Annotated[
        Path,
        Arg(
            value_name="from",
            help=(
                "The path from which the yaml is generated. This can be a file, "
                "or a folder. When a folder is provided, all python files in the "
                "folder will be generated."
            ),
        ),
    ]
    to: Annotated[
        Path | None,
        Arg(
            long=True,
            help=(
                "Optional destination for the produced yaml. If 'from' is a "
                "file this is assumed to be a file. If 'from' is a folder, "
                "this is assumed to be a folder, and individual file names "
                "will match the source file."
            ),
        ),
    ] = None
    recursive: Annotated[bool, Arg(help="Enables recursive traversal of an input folder")] = False
