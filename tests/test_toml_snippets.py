# pytest test that validates Python snippets embedded in TOML files using flake8.
# It discovers all *.toml files recursively (from a configurable root), reads each table
# that contains both `src` (multiline code string) and `expected_codes` (list of flake8 codes),
# runs flake8 on the snippet, and asserts the codes match.
#
# Usage:
#   1) Ensure flake8 is installed (and any plugins you need).
#   2) Put your .toml files anywhere under the search root (default: the project root).
#   3) Run:  pytest -q
#
# Optional env vars:
#   - SNIPPET_TOML_ROOT: set a custom search root (default: current working directory)
#   - FLAKE8_ARGS: extra args for the flake8 CLI (e.g. "--max-line-length=100")
#   - FLAKE8_ISOLATED: if set to "1", run flake8 with --isolated (ignore project configs)
#
# TOML parsing uses the stdlib `tomllib` (Python 3.11+) or `tomli` fallback.

from __future__ import annotations

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import tomllib  # Python 3.11+
    def load_toml_bytes(data: bytes) -> dict:
        return tomllib.loads(data.decode("utf-8"))
except Exception:
    try:
        import tomli as tomllib  # type: ignore
        def load_toml_bytes(data: bytes) -> dict:
            return tomllib.loads(data.decode("utf-8"))
    except Exception as e:  # pragma: no cover
        raise RuntimeError("Install Python 3.11+ or `pip install tomli` for TOML support") from e


# --- Discovery ----------------------------------------------------------------

def iter_toml_files(search_roots: Iterable[Union[str, Path]]) -> List[Path]:
    files: List[Path] = []
    for root in search_roots:
        root = Path(root)  # normalize str/Path/os.PathLike into Path
        files.extend(p for p in root.rglob("*.toml") if p.is_file())
    return files

def load_tests_from_toml(path: Path) -> List[Tuple[str, str, List[str]]]:
    """
    Returns a list of (case_id, src, expected_codes)
    For each top-level table in the TOML file that has `src` and `expected_codes`.
    """
    data = load_toml_bytes(path.read_bytes())
    cases: List[Tuple[str, str, List[str]]] = []
    if not isinstance(data, dict):
        return cases

    for table_name, table in data.items():
        if not isinstance(table, dict):
            continue
        if "src" in table and "expected_codes" in table:
            src = table["src"]
            exp = table["expected_codes"]
            if not isinstance(src, str):
                raise AssertionError(f"{path} [{table_name}]: `src` must be a string")
            if not (isinstance(exp, list) and all(isinstance(x, str) for x in exp)):
                raise AssertionError(f"{path} [{table_name}]: `expected_codes` must be a list[str]")
            case_id = f"{path.name}::{table_name}"
            cases.append((case_id, src, exp))
    return cases


# --- Flake8 runner ------------------------------------------------------------

def flake8_codes_for_snippet(src: str) -> Tuple[List[str], str]:
    """
    Write `src` to a temp .py file and run flake8 on it.
    Returns (sorted_unique_codes, full_stdout).
    """
    extra_args = os.getenv("FLAKE8_ARGS", "").split()
    isolated = ["--isolated"] if os.getenv("FLAKE8_ISOLATED", "") == "1" else []

    with tempfile.TemporaryDirectory() as td:
        py_path = Path(td) / "snippet.py"
        py_path.write_text(src, encoding="utf-8")

        cmd = ["flake8", str(py_path), *isolated, *extra_args]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        except FileNotFoundError:  # pragma: no cover
            raise RuntimeError("flake8 not found. Install with `pip install flake8` (and plugins if needed).")

        out = proc.stdout.strip()
        codes = []
        if out:
            for line in out.splitlines():
                # Expected format: path:line:col: CODE message
                # Example: /tmp/tmpabc/snippet.py:1:1: E302 expected 2 blank lines, found 1
                try:
                    _path, _line, _col, rest = line.split(":", 3)
                    code = rest.strip().split()[0]
                    # Filter out non-code garbage just in case
                    if code and code[0].isalpha():
                        codes.append(code)
                except ValueError:
                    # Non-standard line? Ignore but keep output for debug
                    pass
        codes_sorted = sorted(set(codes))
        return codes_sorted, out


# --- Pytest generation --------------------------------------------------------

def pytest_generate_tests(metafunc):
    if "case_id" in metafunc.fixturenames and "src" in metafunc.fixturenames and "expected_codes" in metafunc.fixturenames:
        if os.getenv("SNIPPET_PATH") is not None:
            parts = os.getenv("SNIPPET_PATH").split(os.pathsep)
            snippet_roots = [Path(p).resolve() for p in parts if p.strip()]
        else:
            snippet_roots = metafunc.config.getini("testpaths")
        toml_files = iter_toml_files(snippet_roots)
        all_cases: List[Tuple[str, str, List[str]]] = []
        for tf in toml_files:
            all_cases.extend(load_tests_from_toml(tf))

        if not all_cases:
            metafunc.parametrize(("case_id", "src", "expected_codes"), [], ids=[])
            return

        ids = [cid for (cid, _src, _exp) in all_cases]
        metafunc.parametrize(("case_id", "src", "expected_codes"), all_cases, ids=ids)


def test_snippet(case_id: str, src: str, expected_codes: List[str]):
    got_codes, flake8_output = flake8_codes_for_snippet(src)
    exp_set = set(expected_codes)
    got_set = set(got_codes)

    missing = sorted(exp_set - got_set)
    unexpected = sorted(got_set - exp_set)

    debug_note = ""
    if missing or unexpected:
        # Include the full flake8 output for debugging
        debug_note = "\n\n--- flake8 raw output ---\n" + (flake8_output or "<no output>") + "\n"

    assert not missing and not unexpected, (
        f"{case_id}: flake8 codes mismatch\n"
        f"  expected: {sorted(exp_set)}\n"
        f"  got     : {sorted(got_set)}\n"
        f"  missing : {missing}\n"
        f"  unexpected: {unexpected}"
        f"{debug_note}"
    )
