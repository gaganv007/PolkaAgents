import logging
import time
from typing import Callable, Any, Dict
import hashlib
import json
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def time_execution(func: Callable) -> Callable:
    """Decorator to measure execution time of a function."""
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Function {func.__name__} executed in {duration:.4f} seconds")
        return result
    return wrapper

def generate_interaction_id(agent_id: int, query: str, timestamp: int = None) -> int:
    """Generate a deterministic interaction ID based on inputs."""
    if timestamp is None:
        timestamp = int(time.time())
    
    # Create a hash of the inputs
    data = f"{agent_id}:{query}:{timestamp}"
    hash_value = hashlib.md5(data.encode()).hexdigest()
    
    # Convert first 8 characters of hash to integer
    return int(hash_value[:8], 16)

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length and add ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def format_duration(seconds: int) -> str:
    """Format a duration in seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hours, {minutes} minutes"

def simulate_network_delay(min_delay: float = 0.1, max_delay: float = 0.5) -> None:
    """Simulate a network delay for testing."""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def format_price(price: int, decimals: int = 10) -> str:
    """Format price from blockchain format (with decimals) to human-readable."""
    return f"{price / (10 ** decimals):.4f} DOT"