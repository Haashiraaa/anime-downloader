

# src/scrapers/animeheaven.py


import re
import sys
from typing import Any

import requests
from bs4 import BeautifulSoup
from haashi.utility import Logger


class AnimeHeavenScraper:
    """Scraper for AnimeHeaven anime pages."""

    BASE_URL = "https://animeheaven.me/"
    GATE_URL = "https://animeheaven.me/gate.php"

    def __init__(self, logger: Logger) -> None:

        self.logger = logger
        self.headers: dict[str, str] = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://animeheaven.me/"
        }
        self.folder_name: str | None = None
        self.name: str = "AnimeHeaven"

    def get_page_res(self, page_url: str) -> requests.Response | None:

        response: requests.Response | None = None

        try:
            self.logger.debug(f"Scraping Anime episodes from {page_url}")
            response = requests.get(page_url, headers=self.headers)
            response.raise_for_status()
            self.logger.debug(f"Response: {response.status_code}")

        except requests.exceptions.Timeout:
            self.logger.error("Request timeout - site may be down")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch anime page: {e}")

        return response

        # todo: handle exceptions for response and parsing

    def parse_page_res(self, response: requests.Response | None) -> tuple[list[dict[str, Any]], str | None]:

        folder_name: str | None = None
        episodes: list[dict[str, Any]] = []

        self.logger.debug("Parsing HTML...")
        assert response
        soup = BeautifulSoup(response.text, 'lxml')

        # Extract and sanitize anime title for use as folder name
        title_tag = soup.find("meta", property="og:title")
        raw_name = str(title_tag["content"]) if title_tag else "Unknown"
        self.logger.info(f"Anime title: {raw_name}")
        clean = re.sub(r'[^\w\s-]', '', raw_name)
        clean = re.sub(r'[\s-]+', '-', clean).strip('-')
        folder_name = clean

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

            self.logger.debug(
                f"Episode #{episode_number} found: {episode_id}"
            )

            episodes.append({
                "episode": episode_number,
                "id": episode_id
            })

        self.logger.info("Extraction complete!")
        self.logger.info(f"Found {len(episodes)} episodes")

        return episodes, folder_name

    def get_video(self, episode_id: str) -> requests.Response | None:

        # AnimeHeaven uses the episode ID as a cookie to gate video access
        cookies = {"key": episode_id}

        response: requests.Response | None = None

        try:
            self.logger.debug(f"Fetching episode page: {episode_id}")
            response = requests.get(
                self.GATE_URL, headers=self.headers, cookies=cookies)
            response.raise_for_status()
            self.logger.debug(f"Response: {response.status_code}")

        except requests.exceptions.Timeout:
            self.logger.error("Request timeout - site may be down")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch episode page: {e}")

        return response

    def parse_video(self, response: requests.Response | None) -> str | None:

        video_url: str | None = None

        self.logger.debug("Parsing HTML...")
        assert response
        soup = BeautifulSoup(response.text, 'lxml')

        assert soup is not None
        video_tag = soup.find("video")
        source = video_tag.find("source") if video_tag else None

        if not source:
            self.logger.error("No video source found!")
            sys.exit(1)

        video_url = str(source["src"])
        return video_url
