"""Offline PORT admission. No retrieval, code execution, or release mutation.

``validate_ports(root, inventory="inventory.json", release_inventory=None,
mode="release", product_root="products")`` returns a deterministic JSON-ready
report. Release mode requires a nonempty exact inventory and allowlist; admission
mode can validate explicitly non-shippable fixtures but never authorizes release.
All paths are canonical POSIX paths relative to root, except tree file paths,
which are relative to their tree. Symlinks and special files are forbidden.
Tree digests hash compact UTF-8 JSON of sorted {path, sha256} entries. Evaluation
receipts bind a distinct run ID/time, tree digest, harness and environment digest;
the validator checks stored evidence, never claims to rerun the harness.
"""
from .validator import tree_digest, validate_ports

__all__ = ["tree_digest", "validate_ports"]
