from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union

from cappa import Arg, Subcommands, command
from typing_extensions import Annotated


@dataclass
class Hera:
    subcommand: Subcommands[Generate]


@command(help="Subcommands for generating yaml, code, and docs from Hera Workflows.")
@dataclass
class Generate:
    subcommand: Subcommands[GenerateYaml]


@command(
    name="yaml",
    help="Generate yaml from python Workflow definitions.",
    invoke="hera._cli.generate.yaml.generate_yaml",
)
@dataclass
class GenerateYaml:
    from_: Annotated[
        Path,
        Arg(
            value_name="from",
            help=(
                "The path from which the yaml is generated. This can be a file "
                "or a folder. When a folder is provided, all Python files in the "
                "folder will be generated."
            ),
        ),
    ]
    to: Annotated[
        Union[Path, None],
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
    include: Annotated[
        List[str],
        Arg(
            short=True,
            long=True,
            help=(
                "Filter the set of input files by including only files matching the `--include`. "
                "Note this also accepts glob specifiers like 'folder/*'. "
            ),
        ),
    ] = field(default_factory=list)
    exclude: Annotated[
        List[str],
        Arg(
            short=True,
            long=True,
            help=(
                "Filter the set of input files by excluding files matching the `--exclude`. "
                "Note this also accepts glob specifiers like 'folder/*'. "
            ),
        ),
    ] = field(default_factory=list)
