"""FLUX — a compact binary encoding for JSON-like values."""

from .client import FluxClient
from .codec import FluxError, decode, encode
from .types import MessageType

__version__ = "0.2.0"
__all__ = [
    "FluxClient",
    "FluxError",
    "MessageType",
    "encode",
    "decode",
    "__version__",
]
