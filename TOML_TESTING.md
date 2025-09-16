

# TOML Testing

The unittest for this repo is set up to read .toml files, and consider each entry a test item.
It runs the src-value (Python code) through Flake and asserts that the reported codes match
the ones in `expected_codes`.

## Example TOML

```toml
[test1]
expected_codes = [
    "FUR901",
    "FUR911",
]
src = """
a = [
    1,
    2,
]
"""

[test2]
expected_codes = [
    "FUR901",
    "FUR911",
]
src = """
a = [
    1,
    2,
    ]
"""
```

> **Note:** toml handles strips multiline values of their first newline, if one such is present, but preserves the trailing newline. 

## Run the tests

```bash
pytest -q
```

### Optional env vars

- `SNIPPET_PATH`: set the directory/directories to search for `.toml` files (defaults to the search paths that pytest uses to collect test items).
- `FLAKE8_ARGS`: extra CLI args to pass to flake8, e.g. `--max-line-length=100`.
- `FLAKE8_ISOLATED=1`: run flake8 with `--isolated` to ignore project/user config files.

Examples:
```bash
SNIPPET_PATH=tests:snippets:snippets_extra pytest -q
FLAKE8_ARGS="--max-line-length=100" pytest -q
FLAKE8_ISOLATED=1 pytest -q
```
