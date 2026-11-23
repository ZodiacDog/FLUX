"""Helpers for measuring FLUX vs JSON on a list of sample payloads."""

from __future__ import annotations

from typing import Any, Iterable

from .client import FluxClient


def measure(samples: Iterable[Any]) -> list[dict]:
    client = FluxClient()
    rows = []
    for sample in samples:
        row = client.compare_sizes(sample)
        row["decoded_ok"] = client.decode(client.encode(sample)) == sample
        rows.append(row)
    return rows
