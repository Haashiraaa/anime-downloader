# src/tools/factory.py

import shutil
import subprocess

from haashi.utility import FileHandler, Logger

from src.tools.downloaders.aria2 import Aria2Downloader
from src.tools.downloaders.base import PathType
from src.tools.downloaders.req import RequestsDownloader


def download_video(
    url: str,
    directory: PathType,
    filename: PathType,
    logger: Logger,
    handler: FileHandler,
    headers: dict[str, str],
) -> None:
    """
    Download url into directory/filename.
    Uses aria2c when available, falls back to requests if aria2c
    is missing or dies mid-download.
    """
    if shutil.which("aria2c"):
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
