

# src/tools/factory.py

import subprocess
from pathlib import Path

import requests
from haashi.utility import FileHandler, Logger

from src.tools.downloaders.aria2 import Aria2Downloader
from src.tools.downloaders.base import PathType
from src.tools.downloaders.req import RequestsDownloader


def _is_already_downloaded(
    url: str,
    filepath: Path,
    headers: dict[str, str],
    logger: Logger,
) -> bool:
    """
    Check whether filepath already holds a complete copy of url.

    Never trusts local presence alone — that's what caused files to be
    silently treated as done. Confirms size against the remote via HEAD.
    """
    if not filepath.exists():
        return False

    try:
        head = requests.head(
            url, headers=headers, allow_redirects=True, timeout=10
        )
        head.raise_for_status()
        expected = int(head.headers.get("content-length", 0))
    except requests.exceptions.RequestException as exc:
        logger.debug(
            f"Could not verify remote size for {filepath.name} ({exc}) - "
            f"treating as incomplete, will re-download"
        )
        return False

    if expected == 0:
        # Server didn't give us a usable content-length - can't verify, don't guess
        return False

    actual = filepath.stat().st_size
    return actual == expected


def download_video(
    url: str,
    directory: PathType,
    filename: PathType,
    logger: Logger,
    handler: FileHandler,
    headers: dict[str, str],
    parallel: bool,
) -> None:
    """
    Download url into directory/filename.
    Skips the download entirely if a verified-complete copy already exists.
    Uses aria2c when available, falls back to requests if aria2c
    is missing or dies mid-download.
    """
    filepath = Path(directory) / filename

    if _is_already_downloaded(url, filepath, headers, logger):
        logger.info(f"{filename} already downloaded - skipping")
        return

    if parallel:
        try:
            Aria2Downloader(logger, handler).download(
                url, directory, filename, headers=headers)
            logger.info("Download complete!")
            return
        except FileNotFoundError:
            # race: aria2c vanished between the which() check and the call
            logger.warning("aria2c not found. Falling back to requests..")
        except subprocess.CalledProcessError:
            logger.warning(
                "aria2c failed mid-download. Falling back to requests..")

    RequestsDownloader(logger, handler).download(
        url, directory, filename, headers=headers)
    logger.info("Download complete!")
