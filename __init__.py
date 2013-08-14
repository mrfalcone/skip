"""
SAIL Kaldi Interface for Python (SKIP)

Provides a Python interface to Kaldi that manages Kaldi
files and caches results.
"""
__license__ = "Apache License, Version 2.0"
__version__ = 0.1
__all__ = ["KaldiContext", "KaldiError"]

from .context import KaldiContext
from .util import KaldiError
