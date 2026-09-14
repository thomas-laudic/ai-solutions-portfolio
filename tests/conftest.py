"""Make the src layout importable when pytest runs from the repository root."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from trustreply.app import app
from trustreply.audit import MemoryAuditSink, get_audit_sink


@pytest.fixture(autouse=True)
def audit_sink():
    """No HTTP test writes to the application's persistent audit sink."""
    sink = MemoryAuditSink()
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_audit_sink] = lambda: sink
    yield sink
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)
