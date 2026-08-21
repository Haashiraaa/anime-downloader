

# src/__main__.py

try:
    from src.main import AnimeDownloader

    # Entry point for `python3 -m src`
    AnimeDownloader.run()

except KeyboardInterrupt:
    print()
    print("Aborted by user")

