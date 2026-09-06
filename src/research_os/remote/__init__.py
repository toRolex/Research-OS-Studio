"""Fail-closed SSH/SLURM capabilities; no remote configuration or work is implicit."""

from .adapter import RemoteAdapter, RemoteExecutor, RemoteReceipt
from .config import RemoteConfig

__all__ = ["RemoteAdapter", "RemoteConfig", "RemoteExecutor", "RemoteReceipt"]
