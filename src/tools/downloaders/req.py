# src/tools/downloaders/req.py

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
    ) -> tuple[PathType, int, dict[str, str]]:
        filepath = Path(directory) / filename
        filepath = self.handler.ensure_writable_path(filepath)

        existing_size = filepath.stat().st_size if filepath.exists() else 0

        required_headers = {**headers}
        if existing_size:
            required_headers["Range"] = f"bytes={existing_size}-"
            self.logger.debug(
                f"Resuming from {existing_size / (1024 * 1024):.1f}MB"
            )

        return filepath, existing_size, required_headers

    def download(
        self,
        url: str,
        directory: PathType,
        filename: PathType,
        headers: dict[str, str],
    ) -> None:

        filepath, existing_size, required_headers = self._resolve_file(
            url, directory, filename, headers
        )

        with requests.get(url, stream=True, headers=required_headers) as res:
            res.raise_for_status()

            resumed = existing_size > 0 and res.status_code == 206
            if existing_size > 0 and not resumed:
                # We asked the server to resume via Range, but it ignored us and sent
                # the whole file back with a 200. Appending now would duplicate/corrupt
                # the file, so start over clean instead.
                self.logger.debug(
                    "Server ignored Range request - restarting download from scratch"
                )
                existing_size = 0

            mode = "ab" if resumed else "wb"

            content_length = int(res.headers.get("content-length", 0))
            # content-length on a 206 response is only the *remaining* bytes -
            # add back what's already on disk to get the true expected total.
            total = existing_size + content_length if resumed else content_length

            with tqdm(
                total=total,
                initial=existing_size if resumed else 0,
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

        # Verify what actually landed on disk before calling it a success -
        # a silently truncated or duplicated file must not pass as complete.
        filepath = Path(filepath)
        final_size = filepath.stat().st_size
        if total and final_size != total:
            filepath.unlink(missing_ok=True)
            raise requests.exceptions.RequestException(
                f"Incomplete download: expected {total} bytes, got {final_size} bytes"
            )

        self.logger.debug("Downloaded with requests")
