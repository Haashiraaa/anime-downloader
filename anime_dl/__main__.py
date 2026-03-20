

# anime_dl/__main__.py

try:
    from anime_dl.main import AnimeDownloader

    # Entry point for `python3 -m anime_dl`
    AnimeDownloader.run()

except KeyboardInterrupt:
    print()
    print("Aborted by user")

