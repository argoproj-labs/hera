"""The main entrypoint for hera CLI."""

import sys
from typing import List, Optional


def main(args: Optional[List[str]] = None) -> int:
    if args is None:
        args = sys.argv[1:]

    print("args:", args)
