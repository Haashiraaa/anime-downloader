

# src/tools/handlers/downloads.py

import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

from haashi.utility import FileHandler, Logger
from haashi.utility import ScreenUtil as su

from src.helpers.hint import aria2_install_hint
from src.helpers.retry import retry
from src.scrapers.animeheaven import AnimeHeavenScraper

from .episode import download_episode, filter_episodes


def build_logger(debug: bool) -> Logger:
    """Return a Logger at DEBUG level if requested, otherwise INFO."""
    return Logger(logging.DEBUG if debug else logging.INFO)


def download_factory(
    episodes: list[dict[str, str]],
    scraper: AnimeHeavenScraper,
    handler: FileHandler,
    project_root: Path,
    logger: Logger,
    folder_name: str | Path,
    num_workers: int,
) -> None:

    parallel: bool = True

    if not shutil.which("aria2c"):
        logger.warning(
            "aria2c not found — downloads will be sequential and slower."
        )
        logger.warning(
            f"For faster parallel downloads, install it: {aria2_install_hint()}")

        parallel = False
        for ep in episodes:
            download_episode(
                ep,
                scraper=scraper,
                handler=handler,
                project_root=project_root,
                logger=logger,
                folder_name=folder_name,
                headers=scraper.headers,
                parallel=parallel,
            )
        return

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(
            partial(
                download_episode,
                scraper=scraper,
                handler=handler,
                project_root=project_root,
                logger=logger,
                folder_name=folder_name,
                headers=scraper.headers,
            ),
            episodes,
        )


def download_anime(
    url: str,
    num_workers: int,
    limit: int | None,
    newest_first: bool,
    episode: int | None,
    handler: FileHandler,
    logger: Logger,
) -> None:
    """Scrape one anime page and download its episodes (sequential or threaded)."""
    scraper = AnimeHeavenScraper(logger=logger)

    su.space()
    logger.info("=" * 60)
    logger.info(f"{scraper.name} Downloader")
    logger.info("=" * 60)
    logger.info(f"Target URL: {url}")
    su.space()

    episodes, folder_name = retry(
        lambda: scraper.scrape_episodes(url),
        retries=10,
        logger=logger,
    )
    assert episodes

    episodes = filter_episodes(episodes, episode, limit, newest_first, logger)

    project_root = handler.get_parent_path(levels_up=1)

    download_factory(
        episodes=episodes,
        scraper=scraper,
        handler=handler,
        project_root=project_root,
        logger=logger,
        folder_name=folder_name,
        num_workers=num_workers,
    )


def run_downloads(
    urls: list[str],
    num_workers: int,
    limit: int | None = None,
    newest_first: bool = True,  # default: download newest first
    episode: int | None = None,
    debug: bool = False,
    logger: Logger | None = None,
) -> None:
    """
    Main download pipeline — iterates every anime URL and downloads its episodes.

    Args:
        urls: List of anime page URLs.
        num_workers: Number of parallel download threads.
        limit: Max episodes to download.
        newest_first: If True, download newest episodes first.
        episode: Download a specific episode number only.
        debug: Enable debug logging.
        logger: Optional logger instance.
    """
    logger = logger or build_logger(debug)
    handler = FileHandler(logger=logger)

    for url in urls:
        download_anime(
            url,
            num_workers=num_workers,
            limit=limit,
            newest_first=newest_first,
            episode=episode,
            handler=handler,
            logger=logger,
        )
