

# anime_dl/downloader.py

import requests
import subprocess
import logging
from typing import Optional
from haashi_pkg.utility import Logger, ScreenUtil as su
from pathlib import Path


class VideoDownloader:
    """Handles video downloads via aria2c with requests fallback."""

    def __init__(
        self, url: str, logger: Optional[Logger] = None,
    ) -> None:
        """
        Args:
            url: Direct video URL to download.
            logger: Optional logger instance.
        """
        self.url = url
        self.logger = logger or Logger(logging.INFO)

    def _download_with_aria2(
        self, directory: str | Path, filename: str | Path
    ) -> None:
        """Download using aria2c with 16 connections for speed."""
        subprocess.run(
            ["aria2c", "-x", "16", "-s", "16",
             "-d", directory, "-o", filename, self.url],
            check=True
        )

    def _download_with_requests(
        self, directory: str | Path, filename: str | Path
    ) -> None:
        """Fallback downloader using requests with 1MB chunked streaming."""
        filepath = Path(directory) / filename
        with requests.get(self.url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

    def download_video(
        self, directory: str | Path, filename: str | Path
    ) -> None:
        """
        Download video to the given directory.
        Tries aria2c first, falls back to requests if unavailable or failed.

        Args:
            directory: Destination folder.
            filename: Output filename.
        """
        su.space()
        try:
            self.logger.debug("Trying aria2c...")
            self._download_with_aria2(directory, filename)
            self.logger.debug("Downloaded with aria2c")
            self.logger.info("Download complete!")

        except FileNotFoundError:
            # aria2c not installed on this system
            self.logger.warning("aria2c not installed. Falling back...")
            self._download_with_requests(directory, filename)

        except subprocess.CalledProcessError:
            # aria2c failed mid-download
            self.logger.warning(
                "aria2c failed during download. Falling back...")
            self._download_with_requests(directory, filename)

