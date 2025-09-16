import pytest

# conftest.py
def pytest_addoption(parser):
    grp = parser.getgroup("furlinter")
    grp.addoption(
        "--fselect",
        action="store",
        default="",
        help="Comma-separated Flake8 select codes (e.g. FUR,E9)",
    )
    grp.addoption(
        "--fignore",
        action="store",
        default="",
        help="Comma-separated Flake8 ignore codes (e.g. E215,E216)",
    )

def _csv_list(val: str):
    return [x.strip() for x in val.split(",") if x.strip()]

@pytest.fixture(scope="session")
def selected_codes(request):
    return _csv_list(request.config.getoption("--fselect"))

@pytest.fixture(scope="session")
def ignored_codes(request):
    return _csv_list(request.config.getoption("--fignore"))
