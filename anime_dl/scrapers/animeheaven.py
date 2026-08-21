

# anime_dl/scrapers/animeheaven.py

import requests
import logging
import sys
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from haashi.utility import Logger
from anime_dl import headers


class AnimeHeavenScraper:
    """Scraper for AnimeHeaven anime pages."""

    def __init__(self, url: str, logger: Optional[Logger] = None) -> None:
        """
        Args:
            url: Anime page URL.
            logger: Optional logger instance.
        """
        self.url1 = url
        self.url2 = "https://animeheaven.me/gate.php"
        self.url3 = "https://animeheaven.me/"

        self.logger = logger or Logger(logging.INFO)

        self.headers = headers
        self.episodes: List[Dict[str, Any]] = []
        self.folder_name: Optional[str] = None
        self.name: str = "AnimeHeaven"

    def scrape_episodes(self) -> List[Dict[str, Any]]:
        """
        Scrape episode IDs and numbers from the anime page.

        Returns:
            List of dicts with 'episode' and 'id' keys.
        """

        response: Optional[requests.Response] = None
        soup: Optional[BeautifulSoup] = None

        try:
            self.logger.debug(f"Scraping Anime episodes from {self.url1}")
            response = requests.get(self.url1, headers=self.headers)
            response.raise_for_status()
            self.logger.debug(f"Response: {response.status_code}")

        except requests.exceptions.Timeout:
            self.logger.error("Request timeout - site may be down")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch anime page: {e}")

        try:
            self.logger.debug("Parsing HTML...")
            assert response
            soup = BeautifulSoup(response.text, 'lxml')

        except Exception as e:
            self.logger.error(f"Failed to parse HTML: {e}")

        if soup is None:
            raise Exception("Failed to parse HTML")

        # Extract and sanitize anime title for use as folder name
        title_tag = soup.find("meta", property="og:title")
        raw_name = str(title_tag["content"]) if title_tag else "Unknown"
        self.logger.info(f"Anime title: {raw_name}")
        clean = re.sub(r'[^\w\s-]', '', raw_name)
        clean = re.sub(r'[\s-]+', '-', clean).strip('-')
        self.folder_name = clean

        episode_tags = soup.find_all('a', href='gate.php', id=True)
        if not episode_tags:
            self.logger.error("No episodes found!")
            sys.exit(1)

        self.logger.info("Extracting episode IDs and numbers...")
        for tag in episode_tags:
            episode_id = tag['id'] if tag['id'] else "Unknown"
            episode_num_tag = tag.find('div', class_='watch2')
            episode_number = (
                episode_num_tag.text.strip()
                if episode_num_tag else "Unknown"
            )

            self.episodes.append({
                "episode": episode_number,
                "id": episode_id
            })

            self.logger.debug(
                f"Episode #{episode_number} found: {episode_id}"
            )

        self.logger.info("Extraction complete!")
        self.logger.info(f"Found {len(self.episodes)} episodes")

        return self.episodes

    def fetch_video_url(self, episode_id: str) -> str:
        """
        Fetch the direct video URL for a given episode.

        Args:
            episode_id: The episode ID used as a cookie key.

        Returns:
            Direct video source URL.
        """

        # AnimeHeaven uses the episode ID as a cookie to gate video access
        cookies = {"key": episode_id}

        response: Optional[requests.Response] = None
        soup: Optional[BeautifulSoup] = None

        try:
            self.logger.debug(f"Fetching episode page: {episode_id}")
            response = requests.get(
                self.url2, headers=self.headers, cookies=cookies)
            response.raise_for_status()
            self.logger.debug(f"Response: {response.status_code}")

        except requests.exceptions.Timeout:
            self.logger.error("Request timeout - site may be down")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch episode page: {e}")

        try:
            self.logger.debug("Parsing HTML...")
            assert response
            soup = BeautifulSoup(response.text, 'lxml')

        except Exception as e:
            self.logger.error(f"Failed to parse HTML: {e}")

        if soup is None:
            raise Exception("Failed to parse HTML")

        video_tag = soup.find("video")
        source = video_tag.find("source") if video_tag else None

        if not source:
            self.logger.error("No video source found!")
            sys.exit(1)

        video_url = str(source["src"])
        return video_url
