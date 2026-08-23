

# src/main.py — entry point

from src.helpers.cli import parse_args
from src.tools.handlers.downloads import run_downloads


def main() -> None:
    """Entry point — parse CLI args and kick off the download pipeline."""
    try:
        args = parse_args()
        run_downloads(
            urls=args.urls,
            num_workers=args.workers,
            limit=args.limit,
            newest_first=not args.oldest,
            episode=args.episode,
            debug=args.debug,
        )
    except KeyboardInterrupt:
        import logging
        import sys

        from haashi.utility import Logger
        from haashi.utility import ScreenUtil as su

        su.space()
        Logger(logging.INFO).info("Program interrupted by user/admin.")
        sys.exit()
