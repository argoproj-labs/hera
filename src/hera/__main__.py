"""Entrypoint for running hera as a CLI."""
import sys

if __name__ == "__main__":
    from hera._cli.main import main as _main

    sys.exit(_main())
