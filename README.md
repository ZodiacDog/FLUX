# FLUX

A compact binary encoding for JSON-like values (objects, arrays, strings,
integers, floats, booleans, null, and bytes), with per-message string
deduplication and a CRC-32 check.

FLUX is a **small codec**, not a network stack and not a promise of lower
cloud bills. Size reduction versus JSON depends entirely on the payload.

## Measured results (2026-11-23, America/Chicago)

These numbers were measured on the audit machine (Python 3.13) against
**compact JSON** (`json.dumps(..., separators=(",", ":"))`). Re-run
`python examples/demo.py` and `python benchmarks/run_benchmarks.py` to
reproduce.

| Payload | JSON | FLUX | Size vs JSON | Encode time vs `json.dumps` |
|---|---:|---:|---:|---:|
| Small function-call object (one short dict) | 75 B | 80 B | **6.7% larger** | 3.19× slower |
| Agent message with repeated `"analysis"` × 20 | 337 B | 159 B | **52.8% smaller** | 5.04× slower |
| 200 similar event records | 8,891 B | 2,974 B | **66.6% smaller** | 7.49× slower |
| Demo “agent message” (less repetition) | 144 B | 126 B | **12.5% smaller** | — |
| Demo 50-item batch | 1,941 B | 732 B | **62.3% smaller** | — |

Takeaway: **small, non-repetitive messages can be larger than JSON**
because of the 4-byte magic, type byte, length, and CRC-32 trailer.
Repeated keys and batch records are where this encoding shrinks. This
Python implementation was **3.2×–7.5× slower to encode** than
`json.dumps` on the same machine. Network or dollar savings were **not
measured**.

Charts checked into the repo (`flux_*.png`) came from an earlier write-up
whose generating code was not published. They are **not** the measurements
above and should not be cited as current results.

## Install

```bash
git clone https://github.com/ZodiacDog/FLUX.git
cd FLUX
pip install -e ".[dev]"
```

Python 3.10+, no runtime dependencies.

## Quick start

```python
from flux_protocol import FluxClient, MessageType

client = FluxClient()
data = {
    "function": "process_batch",
    "args": {"items": [1, 2, 3, 4, 5], "priority": "high"},
}
blob = client.encode(data, MessageType.FUNCTION_CALL)
assert client.decode(blob) == data
print(client.compare_sizes(data))
```

## Tests

```bash
python -m pytest -q
```

On the 2026-11 audit machine: **8 passed** (including 21 subtests in the
scalar/container round-trip test), 0 failed.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

Developed and created by ML Innovations Research Lab (Michael L. McKnight).
Contributor: Korg (AI assistant, Grok Bot).

## Contact

**M. L. McKnight**  
ML Innovations Research Lab  
Pheba, Mississippi  

Email: [ml.innovation.research.lab@gmail.com](mailto:ml.innovation.research.lab@gmail.com)
