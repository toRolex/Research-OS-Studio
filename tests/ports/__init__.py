"""Expose the leaf fixture import under full unittest discovery."""
import sys
from . import fixtures
sys.modules.setdefault("fixtures", fixtures)
