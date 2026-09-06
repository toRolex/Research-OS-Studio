"""Scoped CLI; the top-level research-os dispatcher is deliberately unchanged."""
from __future__ import annotations

import argparse
import json

from . import validate_ports


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate offline PORT admission evidence")
    parser.add_argument("--root", required=True)
    parser.add_argument("--inventory", default="inventory.json")
    parser.add_argument("--release-inventory")
    parser.add_argument("--mode", choices=("admission", "release"), default="release")
    parser.add_argument("--product-root", default="products")
    args = parser.parse_args()
    report = validate_ports(args.root, inventory=args.inventory,
                            release_inventory=args.release_inventory, mode=args.mode,
                            product_root=args.product_root)
    print(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False))
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
