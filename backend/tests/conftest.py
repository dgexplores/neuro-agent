"""Local isolated storage for backend tests; no persistent demo records."""
import pytest
from backend.services.case_store import SQLiteCaseStore, get_case_store

@pytest.fixture
def case_store(tmp_path):
    return SQLiteCaseStore(str(tmp_path / "cases.sqlite3"))

@pytest.fixture(autouse=True)
def isolated_case_store(case_store):
    from backend.main import app
    app.dependency_overrides[get_case_store] = lambda: case_store
    yield
    app.dependency_overrides.pop(get_case_store, None)
