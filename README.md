
# anime-downloader

A command-line tool for downloading anime episodes from AnimeHeaven. Supports parallel downloads, retry logic, and flexible episode filtering.

---

## Requirements

- Python 3.10+
- aria2c (optional but recommended for faster, parallel downloads — a per-OS install hint is printed if it's missing)
- Dependencies are managed via `pyproject.toml`

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/Haashiraaa/anime-downloader
cd anime-downloader
pip install -e .
```

This installs the `anime` console script and pulls in all dependencies automatically.

---

## Usage

```bash
anime --urls "https://animeheaven.me/anime.php?9rp26"
```

Alternatively, without installing the console script:

```bash
python3 -m app --urls "https://animeheaven.me/anime.php?9rp26"
```

### Options

| Flag | Description |
|------|-------------|
| `--urls` | One or more anime page URLs (required) |
| `--limit N` | Download only N episodes |
| `--oldest` | Download oldest episodes first (default is newest) |
| `--episode N` | Download a specific episode by number |
| `--workers N` | Number of concurrent download workers (default: 3) |
| `-d, --debug` | Enable debug logging |

### Examples

```bash
# Download all episodes
anime --urls "url"

# Download multiple anime at once
anime --urls "url1" "url2" "url3"

# Download 3 newest episodes
anime --urls "..." --limit 3

# Download 3 oldest episodes
anime --urls "..." --limit 3 --oldest

# Download episode 5 only
anime --urls "..." --episode 5

# Enable debug output
anime --urls "..." --debug
```

---

## Project Structure

```
app/
    __main__.py           # Entry point — `python3 -m app`
src/
    main.py                # main() — parses args, runs the download pipeline
    helpers/
        cli.py              # Argument parsing
        retry.py            # Retry logic with exponential backoff
        hint.py              # OS-aware aria2c install hint
    scrapers/
        animeheaven.py      # AnimeHeavenScraper — scrapes episodes and video URLs
    tools/
        factory.py          # Picks aria2c or requests, with fallback on failure
        downloaders/
            base.py           # BaseDownloader ABC
            aria2.py          # Aria2Downloader — parallel, 16 connections
            req.py            # RequestsDownloader — chunked streaming, resume-capable
        handlers/
            downloads.py      # run_downloads / download_anime / download_factory
            episode.py        # filter_episodes / download_episode
    exceptions/
        errors.py            # Base exception type
```

Downloads are saved to `Downloads/` at the project root, organized by anime title.

---

## Dependencies

- `requests` — HTTP requests
- `beautifulsoup4` — HTML parsing
- `lxml` — HTML parser backend
- `tqdm` — download progress bars
- `haashi` — utility library (logger, file handler, screen utilities)

Dev dependencies (`pip install -e ".[dev]"`): `ruff`, `pyright`, `autopep8`, `pytest`, `pytest-cov`, `build`.

---

## Notes

- aria2c is used for downloads when available, with a requests fallback if it's missing or fails mid-download
- If aria2c isn't installed, downloads run sequentially with a progress bar, and an OS-specific install hint (apt/pacman/dnf/brew/winget/choco) is printed
- If aria2c is installed, downloads run in parallel using a thread pool (default 3 workers, configurable with `--workers`)
- Failed network calls are retried up to 10 times with exponential backoff
- Partial downloads (via the requests fallback) are resumed automatically on retry rather than restarting from scratch
- Anime titles are sanitized before being used as folder names to ensure cross-platform compatibility
