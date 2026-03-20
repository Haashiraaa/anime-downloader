

# anime_dl/helpers/cli.py

import argparse

ArgLike = argparse.Namespace


def parse_args() -> ArgLike:
    """Parse CLI arguments for the anime downloader."""

    parser = argparse.ArgumentParser(description="Download anime episodes")

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

