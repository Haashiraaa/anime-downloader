

# src/tools/handlers/episode.py

import sys
from pathlib import Path
from typing import cast

from haashi.utility import FileHandler, Logger

from src.helpers.retry import retry
from src.scrapers.animeheaven import AnimeHeavenScraper
from src.tools.factory import download_video


def filter_episodes(
    episodes: list[dict[str, str]],
    episode: int | None,
    limit: int | None,
    newest_first: bool,
    logger: Logger,
) -> list[dict[str, str]]:
    """Apply --episode / --limit / --oldest filtering to a scraped episode list."""
    if episode and episode > 0:
        matched = [ep for ep in episodes if ep.get("episode") == str(episode)]
        if not matched:
            logger.error(f"Episode {episode} not found")
            sys.exit(1)
        return matched

    if limit and not episode:
        return episodes[:limit] if newest_first else episodes[-limit:]

    return episodes


def download_episode(
    ep: dict[str, str],
    scraper: AnimeHeavenScraper,
    handler: FileHandler,
    project_root: Path,
    logger: Logger,
    folder_name: str | Path,
    headers: dict[str, str],
    parallel: bool,
) -> None:
    """
    Fetch the video URL for one episode and download it.
    Intended to be called concurrently via ThreadPoolExecutor.

    Args:
        ep: Episode dict with 'episode' and 'id' keys.
        scraper: Scraper instance for fetching video URLs.
        handler: FileHandler for path management.
        project_root: Root path for saving downloads.
        logger: Logger instance.
    """
    episode_number = ep["episode"]
    episode_id = ep["id"]

    video_url = cast(str, retry(
        lambda: scraper.fetch_video_url(episode_id),
        retries=10,
        delay=2,
        logger=logger,
    ))

    assert folder_name
    folder_name = Path(folder_name)
    folder = handler.ensure_writable_path(
        project_root / "Downloads" / folder_name
    )

    filepath = f"episode_{episode_number}.mp4"

    retry(
        lambda: download_video(
            video_url, folder, filepath,
            logger=logger, handler=handler, headers=headers,
            parallel=parallel,
        ),
        retries=10,
        logger=logger,
    )
