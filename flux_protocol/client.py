"""High-level encode/decode helper with size comparison against JSON."""

from __future__ import annotations

import json
from typing import Any, Optional

from . import codec
from .types import MessageType


class FluxClient:
    def encode(self, data: Any, message_type: Optional[MessageType] = None) -> bytes:
        kind = int(message_type) if message_type is not None else 0
        return codec.encode(data, message_type=kind)

    def decode(self, blob: bytes) -> Any:
        return codec.decode(blob)

    def compare_sizes(self, data: Any) -> dict:
        json_bytes = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        flux_bytes = self.encode(data)
        json_len = len(json_bytes)
        flux_len = len(flux_bytes)
        reduction = 0.0 if json_len == 0 else (1.0 - (flux_len / json_len)) * 100.0
        return {
            "json_bytes": json_len,
            "flux_bytes": flux_len,
            "reduction_percent": round(reduction, 1),
        }
