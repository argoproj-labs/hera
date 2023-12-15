"""Entrypoint for running hera as a CLI."""


def main():
    """Entrypoint for running hera as a CLI."""
    try:
        import cappa
    except ImportError:
        raise ImportError("Use of the `hera` CLI tool requires installing the 'cli' extra, `pip install hera[cli]`.")

    import rich

    from hera._cli.base import Hera

    rich.print(
        "[yellow bold]warning: The `hera` CLI is a currently work-in-progress, subject to change at any time![/yellow bold]"
    )

    cappa.invoke(Hera)


if __name__ == "__main__":
    main()
