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
    subcommand: Subcommands[GenerateYaml | GeneratePython]


@command(
    name="yaml",
    help="Generate YAML from Python Workflow definitions.",
    invoke="hera._cli.generate.yaml.generate_yaml",
)
@dataclass
class GenerateYaml:
    from_: Annotated[
        Path,
        Arg(
            value_name="from",
            help=(
                "The path of a Python file or folder from which the YAML is generated. "
                "When a folder is provided, all Python files in the folder containing Workflow objects "
                "will be used."
            ),
        ),
    ]
    to: Annotated[
        Union[Path, None],
        Arg(
            long=True,
            help=(
                "Optional file or folder for the produced YAML. Will output to stdout if not provided. "
                "If the input 'from' is a file, 'to' is assumed to be a file. If 'from' is a folder, "
                "'to' is assumed to be a folder, and the folder structure of 'from' will be preserved "
                "in the 'to' output (when using '--recursive')."
            ),
        ),
    ] = None
    recursive: Annotated[
        bool,
        Arg(
            help="Enables recursive traversal of an input folder. Output folder structure will match input folder structure unless '--flatten' is specified."
        ),
    ] = False
    flatten: Annotated[
        bool,
        Arg(
            help="If 'to' is a folder and you have specified '--recursive', then use 'flatten' to output to YAML files without matching the input directory structure. No effect if 'to' is a file (all Workflows will be output in one file)."
        ),
    ] = False
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


@command(
    name="python",
    help="Generate Python from YAML Workflow definitions.",
    invoke="hera._cli.generate.python.generate_python",
)
@dataclass
class GeneratePython:
    from_: Annotated[
        Path,
        Arg(
            value_name="from",
            help=(
                "The path of a YAML file or folder from which the Python code is generated. "
                "When a folder is provided, all YAML files in the folder containing eligible "
                "Workflow specs will be used. If a given file has multiple definitions in it, "
                "all the Python definitions will also be in a single file."
            ),
        ),
    ]
    to: Annotated[
        Union[Path, None],
        Arg(
            long=True,
            help=(
                "Optional file or folder for the produced YAML. Will output to stdout if not provided. "
                "If the input 'from' is a file, 'to' is assumed to be a file. If 'from' is a folder, "
                "'to' is assumed to be a folder, and the folder structure of 'from' will be preserved "
                "in the 'to' output (when using '--recursive')."
            ),
        ),
    ] = None
    recursive: Annotated[
        bool,
        Arg(
            help="Enables recursive traversal of an input folder. Output folder structure will match input folder structure unless '--flatten' is specified."
        ),
    ] = False
    flatten: Annotated[
        bool,
        Arg(
            help="If 'to' is a folder and you have specified '--recursive', then use 'flatten' to output to YAML files without matching the input directory structure. No effect if 'to' is a file (all Workflows will be output in one file)."
        ),
    ] = False
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
