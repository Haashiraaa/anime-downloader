# src/tools/base.py

from abc import ABC, abstractmethod
from pathlib import Path

from haashi.utility import FileHandler, Logger

PathType = str | Path


class BaseDownloader(ABC):
    """Common interface every download strategy must implement."""

    def __init__(self, logger: Logger, handler: FileHandler) -> None:
        self.logger = logger
        self.handler = handler

    @abstractmethod
    def download(self, url: str, directory: PathType, filename: PathType, headers: dict[str, str]) -> None:
        """Download url into directory/filename."""
        raise NotImplementedError
