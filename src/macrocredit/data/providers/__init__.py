"""
Data provider implementations for different sources.

Providers handle the specifics of fetching data from files, Bloomberg, APIs, etc.
"""

from .file import fetch_from_file

__all__ = [
    "fetch_from_file",
]
