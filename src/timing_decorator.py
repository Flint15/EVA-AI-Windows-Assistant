# Measure the time of function execution
from functools import wraps
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def functime(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = time.time()
        logger.info(f'{function.__name__} is started')
        result = function(*args, **kwargs)
        logger.info(f'{function.__name__} is finished')
        end = time.time()
        logger.info(f'Execution time: {end - start:.4f} seconds')
        return result
    return wrapper