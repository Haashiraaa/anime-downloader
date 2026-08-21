

# src/helpers/cli.py

import argparse

ArgLike = argparse.Namespace


def check_workers(value: str) -> int:
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "n_workers must be a integer."
        )
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(
            "n_workers must be a positive integer."
        )
    return ivalue


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the anime downloader."""

    parser = argparse.ArgumentParser(description="Download anime episodes")

    parser.add_argument(
        '--workers',
        type=check_workers,
        default=3,
        help='Number of concurrent workers'
    )

    parser.add_argument(
        "--urls",
        type=str,
        nargs='+',
        required=True,
        help="Anime page URL"
    )

    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Number of episodes to download'
    )

    parser.add_argument(
        '--oldest',
        action='store_true',
        default=False,
        help='Download oldest episodes first (default is newest)'
    )

    parser.add_argument(
        '--episode',
        type=int,
        default=None,
        help='Download a specific episode by number'
    )

    return parser.parse_args()
