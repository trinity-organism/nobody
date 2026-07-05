"""NOBODY — the filesystem-native semantic layer for agents.

No server. No database. No frontier. Just meaning, measured.
"""
__version__ = "0.1.0"

from .brain import Brain, load, frontier, stats  # noqa: F401
from .context import compile_context  # noqa: F401
from .lint import lint, has_errors  # noqa: F401
