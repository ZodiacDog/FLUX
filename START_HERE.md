# FLUX — start here

This repository now contains a working, tested codec in `flux_protocol/`.

The December 2025 upload had a README, this file, `setup.py`, and four
PNG charts, but **no implementation**. This file previously described a
launch checklist (HN, star counts, pip numbers, a SaaS server, and a
`$52k/year` savings claim) as if that package already existed. Those
items are not part of this repository.

What to run:

```bash
pip install -e ".[dev]"
python -m pytest -q
python examples/demo.py
python benchmarks/run_benchmarks.py
```

See [README.md](README.md) for **measured** size and encode-time
comparisons versus compact JSON. Do not use the committed PNG charts as
current results.

Contact: ml.innovation.research.lab@gmail.com · Pheba, Mississippi
