from __future__ import annotations

import json
import math
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    data = json.loads((root / "data.json").read_text(encoding="utf-8"))
    values = data["values"]
    mean = math.fsum(values) / len(values)
    squared_error = math.fsum((value - mean) ** 2 for value in values)
    result = {
        "algorithm": "constant-mean-baseline",
        "count": len(values),
        "mean": mean,
        "mean_squared_error": squared_error / len(values),
    }
    (root / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
