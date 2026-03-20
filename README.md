# anime-dl

A command-line tool for downloading anime episodes from AnimeHeaven. Supports parallel downloads, retry logic, and flexible episode filtering.

---

## Requirements

- Python 3.10+
- aria2c (optional but recommended for faster downloads)
- Dependencies listed in `requirements.txt`

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Haashiraaa/anime-downloader
cd anime-downloader
pip install -r requirements.txt
```

---

## Usage

```bash
python3 -m anime_dl --url "https://animeheaven.me/anime.php?9rp26"
```

### Options

| Flag | Description |
|------|-------------|
| `--urls` | One or more anime page URLs (required) |
| `--limit N` | Download only N episodes |
| `--oldest` | Download oldest episodes first (default is newest) |
| `--episode N` | Download a specific episode by number |
| `-d, --debug` | Enable debug logging |

### Examples

```bash
# Download all episodes
python3 -m anime_dl --url "url"

# Download multiple anime at once
python3 -m anime_dl --url "url1" "url2" "url3"

# Download 3 newest episodes
python3 -m anime_dl --url "..." --limit 3

# Download 3 oldest episodes
python3 -m anime_dl --url "..." --limit 3 --oldest

# Download episode 5 only
python3 -m anime_dl --url "..." --episode 5

# Enable debug output
python3 -m anime_dl --url "..." --debug
```

---

## Project Structure

```
anime_dl/
    main.py             # AnimeDownloader class — orchestrates the pipeline
    downloader.py       # VideoDownloader — handles aria2c and requests downloads
    scrapers/
        animeheaven.py  # AnimeHeavenScraper — scrapes episodes and video URLs
    helpers/
        cli.py          # Argument parsing
        retry.py        # Retry logic with exponential backoff
```

Downloads are saved to `anime_downloads/` in the project root, organized by anime title.

---

## Dependencies

- `requests` — HTTP requests
- `beautifulsoup4` — HTML parsing
- `lxml` — HTML parser backend
- `haashi-pkg` — Custom utility library (logger, file handler, screen utilities)

---

## Notes

- aria2c is used for downloads when available, with a requests fallback if not installed
- Failed network calls are retried up to 3 times with exponential backoff
- Downloads run in parallel using a thread pool (default 5 workers)
- Anime titles are sanitized before being used as folder names to ensure cross-platform compatibility
