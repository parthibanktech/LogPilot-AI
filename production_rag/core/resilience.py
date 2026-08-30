"""
production_rag.core.resilience - API Call Retry & Fault Tolerance Decorator
"""

import time
import random
import functools
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Resilience")

def retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0, jitter=True):
    """
    Decorator for retrying functions on exception using exponential backoff and jitter.
    Handles rate limits (429), API timeouts, and transient connection drops.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"[Retry Exhausted] Function {func.__name__} failed after {max_retries} attempts. Error: {e}")
                        raise e
                    
                    sleep_time = delay * (backoff_factor ** (attempt - 1))
                    if jitter:
                        sleep_time += random.uniform(0, 0.5)
                        
                    logger.warning(f"[Attempt {attempt}/{max_retries}] {func.__name__} failed ({e}). Retrying in {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
            raise last_exception
        return wrapper
    return decorator
