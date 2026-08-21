

# anime_dl/downloader.py

import logging
import subprocess
from pathlib import Path
from typing import Union

import requests
from haashi.utility import FileHandler, Logger
from tqdm import tqdm

from anime_dl import headers

PathLike = Union[str, Path]


class VideoDownloader:
    """Handles video downloads via aria2c with requests fallback."""

    def __init__(
        self,
        url: str,
        logger: Logger | None = None,
        handler: FileHandler | None = None,
    ) -> None:
        """
        Args:
            url: Direct video URL to download.
            logger: Optional logger instance.
        """
        self.url = url
        self.logger = logger or Logger(logging.INFO)
        self.handler = handler or FileHandler(logger=self.logger)
        self.headers = headers

    def _download_with_aria2(
        self, directory: PathLike, filename: PathLike
    ) -> None:
        """Download using aria2c with 16 connections for speed."""
        subprocess.run([
            "aria2c",
            "-x",
            "16",
            "-s",
            "16",
            "--referer", "https://animeheaven.me/",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "-d",
            directory,
            "-o",
            filename,
            self.url
        ],
            check=True
        )

    def _download_with_requests(
        self, directory: PathLike, filename: PathLike
    ) -> None:
        """Fallback downloader using requests with 1MB chunked streaming."""
        filepath = Path(directory) / filename
        filepath = self.handler.ensure_writable_path(filepath)

        existing_size = filepath.stat().st_size if filepath.exists() else 0

        headers = {**self.headers}
        if existing_size:
            headers['Range'] = f'bytes={existing_size}-'
            self.logger.debug(
                f"Resuming from {existing_size / (1024*1024):.1f}MB")

        mode = "ab" if existing_size else "wb"  # append if resuming

        with requests.get(self.url, stream=True, headers=headers) as r:
            r.raise_for_status()

            total = int(r.headers.get('content-length', 0))

            with tqdm(
                total=total,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=str(filename),
                leave=True
            ) as bar, open(filepath, mode) as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

    def download_video(
        self, directory: PathLike, filename: PathLike
    ) -> None:
        """
        Download video to the given directory.
        Tries aria2c first, falls back to requests if unavailable or failed.

        Args:
            directory: Destination folder.
            filename: Output filename.
        """

        try:
            self.logger.debug("Trying aria2c...")
            self._download_with_aria2(directory, filename)
            self.logger.debug("Downloaded with aria2c")
            self.logger.info("Download complete!")

        except FileNotFoundError:
            # aria2c not installed on this system
            self.logger.warning(
                "aria2c not installed. Falling back to requests..")
            self._download_with_requests(directory, filename)

        except subprocess.CalledProcessError:
            # aria2c failed mid-download
            self.logger.warning(
                "aria2c failed during download. Falling back to requests..")
            self._download_with_requests(directory, filename)
