import logging
import time

logger = logging.getLogger(__name__)

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed_time = (end - start) * 1000  # convert to milliseconds
        logger.info(f"{func.__name__} executed in {elapsed_time:.2f} ms")
        return result
    return wrapper