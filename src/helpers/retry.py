# src/helpers/retry.py

import time
from collections.abc import Callable
from typing import Any

from haashi.utility import Logger, ScreenUtil

from src.exceptions.errors import AnimeDownloaderError


def retry(
    func: Callable[[], Any],
    logger: Logger,
    retries: int = 3,
    delay: float = 2,
    backoff: int = 2,
) -> Any | None:
    """
    Retry a callable on failure with exponential backoff.

    Args:
        func: Zero-argument callable to retry.
        retries: Max number of attempts.
        delay: Initial wait time in seconds.
        backoff: Multiplier applied to delay after each failure.
        logger: logger for warnings.

    Returns:
        Return value of func on success.

    Raises:
        Exception: Re-raises the last exception after all retries exhausted.
    """
    for attempt in range(1, retries + 1):
        try:
            return func()
        except AnimeDownloaderError as exc:

            if attempt == retries:
                raise
            # Exponential backoff: 2s, 4s, 8s...
            sleep_time = delay * (backoff ** (attempt - 1))
            ScreenUtil.space()

            logger.warning(
                f"Attempt {attempt}/{retries} failed: {exc}. "
                f"Retrying in {sleep_time}s..."
            )
            time.sleep(sleep_time)
