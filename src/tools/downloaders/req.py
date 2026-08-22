# src/tools/downloaders/requests_dl.py

from pathlib import Path

import requests
from tqdm import tqdm

from .base import BaseDownloader, PathType


class RequestsDownloader(BaseDownloader):
    """Fallback downloader - chunked streaming, resume-capable."""

    def _resolve_file(
        self,
        url: str,
        directory: PathType,
        filename: PathType,
        headers: dict[str, str]
    ) -> tuple[PathType, str, dict[str, str]]:
        filepath = Path(directory) / filename
        filepath = self.handler.ensure_writable_path(filepath)

        existing_size = filepath.stat().st_size if filepath.exists() else 0

        required_headers = {**headers}
        if existing_size:
            required_headers["Range"] = f"bytes={existing_size}-"
            self.logger.debug(
                f"Resuming from {existing_size / (1024 * 1024):.1f}MB"
            )

        mode = "ab" if existing_size else "wb"

        return filepath, mode, required_headers

    def download(
        self,
        url: str,
        directory: PathType,
        filename: PathType,
        headers: dict[str, str] | None = None,
    ) -> None:

        assert headers is not None
        filepath, mode, required_headers = self._resolve_file(
            url, directory, filename, headers
        )

        with requests.get(url, stream=True, headers=required_headers) as res:
            res.raise_for_status()
            total = int(res.headers.get("content-length", 0))

            with tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=str(filename),
                leave=True,
            ) as bar, open(filepath, mode) as f:
                for chunk in res.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

        self.logger.debug("Downloaded with requests")
