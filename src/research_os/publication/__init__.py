"""Explicit Publication boundary; no workflow chaining or implicit acceptance."""

from .contracts import manuscript_text, validate_manuscript
from .renderer import render_pdf
from .storage import PublicationError, canonical_bytes
from .workflow import (
    append_event, confirmation_text, freeze_publication, preflight,
    stage_publication, stale_audit, verify_publication,
)

__all__ = [
    'PublicationError', 'append_event', 'canonical_bytes', 'confirmation_text',
    'freeze_publication', 'manuscript_text', 'preflight', 'render_pdf',
    'stage_publication', 'stale_audit', 'validate_manuscript', 'verify_publication',
]
