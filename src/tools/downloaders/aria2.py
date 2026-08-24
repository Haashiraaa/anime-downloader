# src/tools/downloaders/aria2.py

import subprocess

from .base import BaseDownloader, PathType


class Aria2Downloader(BaseDownloader):
    """Downloads via aria2c - 16 parallel connections."""

    def download(self, url: str, directory: PathType, filename: PathType, headers: dict[str, str]) -> None:

        headers = headers or {}
        referer = headers.get("Referer", "https://animeheaven.me/")
        user_agent = headers.get(
            "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        subprocess.run(
            [
                "aria2c",
                "-x", "16",
                "-s", "16",
                # actually resume a partial file instead of assuming its presence means "done"
                "-c",
                # required alongside -c so aria2c is willing to touch an existing file at all
                "--allow-overwrite=true",
                # don't spawn "episode_5 (1).mp4" duplicates on retry
                "--auto-file-renaming=false",
                "--referer", referer,
                "--user-agent", user_agent,
                "-d", str(directory),
                "-o", str(filename),
                url,
            ],
            check=True,
        )
        self.logger.debug("Downloaded with aria2c")
