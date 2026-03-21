

# anime_dl/main.py

import logging
import sys
import shutil
from typing import Optional, Dict, List, cast
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from anime_dl.scrapers.animeheaven import AnimeHeavenScraper
from anime_dl.downloader import VideoDownloader
from haashi_pkg.utility import Logger, FileHandler, ScreenUtil as su
from functools import partial
from anime_dl.helpers.retry import retry
from anime_dl.helpers.cli import parse_args


class AnimeDownloader:
    """Orchestrates the full anime download pipeline."""

    @staticmethod
    def process_episode(
        ep: Dict[str, str],
        scraper: AnimeHeavenScraper,
        handler: FileHandler,
        project_root: Path,
        logger: Logger
    ) -> None:
        """
        Fetch and download a single episode.
        Intended to be called concurrently via ThreadPoolExecutor.

        Args:
            ep: Episode dict with 'episode' and 'id' keys.
            scraper: Scraper instance for fetching video URLs.
            handler: FileHandler for path management.
            project_root: Root path for saving downloads.
            logger: Logger instance.
        """
        try:
            episode_number = ep["episode"]
            episode_id = ep["id"]

            # Fetch video URL with retry in case of network hiccups
            video_url = cast(str, retry(
                lambda: scraper.fetch_video_url(episode_id),
                retries=10,
                delay=2,
                logger=logger
            ))
            downloader = VideoDownloader(video_url, logger=logger)

            assert scraper.folder_name
            folder_name = Path(scraper.folder_name)
            folder = handler.ensure_writable_path(
                project_root / "anime_downloads" / folder_name
            )

            filepath = f"episode_{episode_number}.mp4"

            retry(
                lambda: downloader.download_video(folder, filepath),
                retries=10,
                logger=logger
            )

        except Exception as e:
            raise e

    @classmethod
    def run(cls) -> None:
        """Entry point — parse CLI args and kick off main."""
        args = parse_args()
        cls.main(
            urls=args.urls,
            limit=args.limit,
            newest_first=not args.oldest,
            episode=args.episode,
            debug=args.debug,
        )

    @staticmethod
    def main(
        urls: List[str],
        num_workers: int = 5,
        limit: Optional[int] = None,
        newest_first: bool = True,  # default: download newest first
        episode: Optional[int] = None,
        debug: bool = False,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Main download pipeline.

        Args:
            urls: List of anime page URLs.
            num_workers: Number of parallel download threads.
            limit: Max episodes to download.
            newest_first: If True, download newest episodes first.
            episode: Download a specific episode number only.
            debug: Enable debug logging.
            logger: Optional logger instance.
        """
        logger = logger or Logger(logging.INFO)
        logger = Logger(logging.DEBUG) if debug else logger

        try:
            for url in urls:

                scraper = AnimeHeavenScraper(url, logger=logger)
                handler = FileHandler(logger=logger)

                su.space()
                logger.info("=" * 60)
                logger.info(f"{scraper.name} Downloader")
                logger.info("=" * 60)
                logger.info(f"Target URL: {scraper.url1}")
                su.space()

                episodes = retry(
                    lambda: scraper.scrape_episodes(),
                    retries=10,
                    logger=logger
                )
                assert episodes

                # Filter to a single episode if requested
                if episode and episode > 0:
                    episodes = [
                        ep for ep in episodes
                        if ep.get("episode") == str(episode)  # type: ignore
                    ]
                    if not episodes:
                        logger.error(f"Episode {episode} not found")
                        sys.exit(1)

                # Apply limit only when not targeting a specific episode
                if limit and not episode:
                    episodes = (
                        episodes[:limit] if newest_first else episodes[-limit:]
                    )

                project_root = handler.get_parent_path(levels_up=1)

                if not shutil.which("aria2c"):
                    su.space()
                    logger.warning(
                        "aria2c not found. Downloads will be sequential."
                    )

                    for ep in episodes:
                        AnimeDownloader.process_episode(
                            ep,
                            scraper=scraper,
                            handler=handler,
                            project_root=project_root,
                            logger=logger
                        )

                else:
                    with ThreadPoolExecutor(
                        max_workers=num_workers
                    ) as executor:
                        executor.map(
                            partial(
                                AnimeDownloader.process_episode,
                                scraper=scraper,
                                handler=handler,
                                project_root=project_root,
                                logger=logger
                            ),
                            episodes
                        )

        except KeyboardInterrupt:
            su.space()
            logger.info("Process interrupted by user")
            sys.exit(1)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.error(exception=e, save_to_json=True)
            sys.exit(1)


if __name__ == "__main__":
    AnimeDownloader.run()
