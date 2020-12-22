"""Tests for the pyavreceiver library."""
import asyncio
from functools import wraps

def async_test(func):
    """
    Decorator to create asyncio context for asyncio methods or functions.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))
    return inner
