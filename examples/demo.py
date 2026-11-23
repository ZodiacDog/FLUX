#!/usr/bin/env python3
"""Encode a few payloads and print measured size comparisons versus compact JSON."""

from flux_protocol import FluxClient, MessageType

client = FluxClient()

samples = {
    "small call": {
        "function": "process_batch",
        "args": {"items": [1, 2, 3, 4, 5], "priority": "high"},
    },
    "agent message": {
        "agent_id": "planner_01",
        "action": "delegate_task",
        "target": "executor_02",
        "payload": {"task_type": "analysis", "data": ["analysis", "analysis", "ok"]},
    },
    "batch": [{"id": i, "status": "ok", "type": "event"} for i in range(50)],
}

for name, data in samples.items():
    blob = client.encode(data, MessageType.GENERIC)
    assert client.decode(blob) == data
    stats = client.compare_sizes(data)
    print(
        f"{name}: JSON {stats['json_bytes']} B, FLUX {stats['flux_bytes']} B, "
        f"reduction {stats['reduction_percent']}%"
    )
