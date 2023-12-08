"""Entrypoint for running hera as a CLI."""


def main():
    """Entrypoint for running hera as a CLI."""
    try:
        import cappa
    except ImportError:
        raise ImportError("Use of the `hera` CLI tool requires installing the 'cli' extra, `pip install hera[cli]`.")

    from hera._cli.base import Hera

    cappa.invoke(Hera)


if __name__ == "__main__":
    main()
