import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


# Snapshot of the original activities state
_original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before each test."""
    yield
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


@pytest.fixture
def client():
    """Provide a FastAPI TestClient instance."""
    return TestClient(app)
