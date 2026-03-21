# anime_dl/helpers/retry.py

import time
from typing import Callable, Optional, Any
from haashi_pkg.utility import Logger, ScreenUtil as su


def retry(
    func: Callable[[], Any],
    retries: int = 3,
    delay: float = 2,
    backoff: int = 2,
    logger: Optional[Logger] = None
) -> Optional[Any]:
    """
    Retry a callable on failure with exponential backoff.

    Args:
        func: Zero-argument callable to retry.
        retries: Max number of attempts.
        delay: Initial wait time in seconds.
        backoff: Multiplier applied to delay after each failure.
        logger: Optional logger for warnings.

    Returns:
        Return value of func on success.

    Raises:
        Exception: Re-raises the last exception after all retries exhausted.
    """
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == retries:
                raise
            # Exponential backoff: 2s, 4s, 8s...
            sleep_time = delay * (backoff ** (attempt - 1))
            su.space()
            if logger:
                logger.warning(
                    f"Attempt {attempt}/{retries} failed: {e}. "
                    f"Retrying in {sleep_time}s..."
                )
            time.sleep(sleep_time)

