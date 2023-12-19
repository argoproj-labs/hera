"""Entrypoint for running hera as a CLI."""
import importlib.util
import sys


def main(argv=None):
    """Entrypoint for running hera as a CLI."""
    try:
        importlib.util.find_spec("cappa")
    except ImportError as e:
        raise ImportError(
            "Use of the `hera` CLI tool requires installing the 'cli' extra, `pip install hera[cli]`."
        ) from e

    import cappa
    import rich

    from hera._cli.base import Hera

    rich.print(
        "[yellow bold]warning: The `hera` CLI is a work-in-progress, subject to change at any time![/yellow bold]",
        file=sys.stderr,
    )

    cappa.invoke(Hera, argv=argv)


if __name__ == "__main__":
    main()
