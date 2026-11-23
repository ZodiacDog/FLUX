#!/usr/bin/env python3
"""Print measured FLUX vs compact-JSON sizes. Does not invent a dollar figure."""

from flux_protocol.utils import measure

samples = [
    {"function": "process_batch", "args": {"items": [1, 2, 3, 4, 5], "priority": "high"}},
    {
        "agent_id": "planner_01",
        "action": "delegate_task",
        "target": "executor_02",
        "payload": {"task_type": "analysis", "data": ["analysis"] * 20},
    },
    [{"id": i, "status": "ready", "channel": "jobs"} for i in range(200)],
]

def main() -> None:
    rows = measure(samples)
    labels = ["small", "repetitive agent", "200-item batch"]
    for label, row in zip(labels, rows):
        print(
            f"{label}: JSON={row['json_bytes']} FLUX={row['flux_bytes']} "
            f"reduction={row['reduction_percent']}% decoded_ok={row['decoded_ok']}"
        )

if __name__ == "__main__":
    main()
