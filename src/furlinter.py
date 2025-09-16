"""
furlinter: Flake8 plugin for indentation/style rules.

Currently implements:
- FUR901: In a multiline bracket context, if the final line is a closer-only line,
          the closer must be indented to the same column as inner continuation lines.

Example that triggers FUR901:

a = [
    1,
    2,
]
# ^ closer-only line at column 0, but inner lines start at column 4

Preferred (per this rule):

a = [
    1,
    2,
    ]
"""

from __future__ import annotations

import io
import tokenize
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
from collections import Counter


CODE_FUR901 = "FUR901"

@dataclass
class Context:
    kind: str  # "[]", "()", "{}"
    opener_line: int
    opener_col: int
    opener_line_text: str
    inner_line_first_cols: Dict[int, int] = field(default_factory=dict)  # line -> first token col (per physical line)
    closer_line: Optional[int] = None
    closer_col: Optional[int] = None
    element_and_closer_same_line: bool = False  # True if closer shares its line with element tokens

def _first_non_ws_col(line: str) -> int:
    i = 0
    while i < len(line) and line[i] in " \t":
        i += 1
    return i

def _iter_contexts(srccode_bytes: bytes) -> Iterable[Context]:
    """Yield bracket contexts discovered via tokenize (stack-based)."""
    tokgen = tokenize.tokenize(io.BytesIO(srccode_bytes).readline)

    stack: List[Context] = []
    seen_first_token_on_line: Set[Tuple[int, int]] = set()  # (line, depth) to avoid duplicates

    def record_first_token_for_open_contexts(line: int, col: int):
        # For each open context, if this token appears on a line after the opener,
        # record the first token column for that line (once per context).
        for depth, ctx in enumerate(stack):
            if line > ctx.opener_line and ctx.closer_line is None:
                key = (line, depth)
                if key not in seen_first_token_on_line:
                    ctx.inner_line_first_cols.setdefault(line, col)
                    seen_first_token_on_line.add(key)

    for tok in tokgen:
        ttype, tstr, (srow, scol), (erow, ecol), line_text = tok

        if ttype == tokenize.OP and tstr in "([{":
            kind = {"(": "()", "[": "[]", "{": "{}"}[tstr]
            stack.append(Context(kind=kind, opener_line=srow, opener_col=scol, opener_line_text=line_text or ""))

        # Register first token columns for open contexts (skip trivia)
        if ttype not in (tokenize.NL, tokenize.NEWLINE, tokenize.ENCODING, tokenize.ENDMARKER, tokenize.COMMENT):
            record_first_token_for_open_contexts(srow, scol)

        if ttype == tokenize.OP and tstr in ")]}":
            if stack:
                ctx = stack[-1]
                ctx.closer_line = srow
                ctx.closer_col = scol
                # If we recorded a first token on this same line and it starts before closer,
                # then it's an element+closer line.
                if srow in ctx.inner_line_first_cols and ctx.inner_line_first_cols[srow] < scol:
                    ctx.element_and_closer_same_line = True
                yield stack.pop()

    # Yield any unterminated contexts (syntax errors) to be defensive
    while stack:
        yield stack.pop()

def _desired_inner_col(ctx: Context) -> Optional[int]:
    """Choose the 'continuation indent column' representative for the context.
    We pick the **mode** (most common) of inner first-token columns, or min if tie.
    """
    if not ctx.inner_line_first_cols:
        return None
    counts = Counter(ctx.inner_line_first_cols.values())
    maxfreq = max(counts.values())
    candidates = [col for col, n in counts.items() if n == maxfreq]
    return min(candidates)

def _is_closer_only_line(srccode_lines: List[str], ctx: Context) -> bool:
    """Return True if the line with the closer has no non-whitespace tokens before the closer."""
    if ctx.closer_line is None or ctx.closer_col is None:
        return False
    line = srccode_lines[ctx.closer_line - 1]
    prefix = line[:ctx.closer_col]
    # If there's any non-space/tab char in prefix, then there's code before closer
    return all(ch in " \t" for ch in prefix)

def _check_FUR901(srccode: str) -> Iterable[Tuple[int,int,str]]:
    """Yield (line, col, message) for FUR901 violations."""
    srccode_bytes = srccode.encode("utf-8")
    contexts = list(_iter_contexts(srccode_bytes))
    lines = srccode.splitlines(keepends=False)

    for ctx in contexts:
        # Only care about multiline contexts with at least one inner line
        if ctx.closer_line is None or not ctx.inner_line_first_cols:
            continue
        # We only flag when the ending is closer-only (no element before closer on that line)
        closer_only = _is_closer_only_line(lines, ctx) and not ctx.element_and_closer_same_line
        if not closer_only:
            continue

        desired_col = _desired_inner_col(ctx)
        if desired_col is None:
            continue

        # If closer's column differs from the desired inner continuation column → violation
        if ctx.closer_col != desired_col:
            msg = (f"{CODE_FUR901} closer-only line must align with continuation indent "
                   f"(expected col {desired_col}, found col {ctx.closer_col})")
            yield (ctx.closer_line, ctx.closer_col, msg)

def _check_all(srccode: str):
    yield from _check_FUR901(srccode)

class FurLinter:
    """Flake8 plugin entry point."""
    name = "furlinter"
    version = "0.1.0"

    def __init__(self, tree, filename: str = None, lines: List[str] = None) -> None:
        # flake8 passes in 'tree' (AST) which we don't use for token-level checks
        self.filename = filename
        self._lines = lines  # may be provided by flake8 for stdin
        self._srccode: Optional[str] = None

    def run(self) -> Iterable[Tuple[int, int, str, type]]:
        # Load source code either from flake8-provided lines or from the file
        if self._lines is not None:
            self._srccode = "".join(self._lines)
        else:
            if self.filename in (None, "stdin", "-"):
                return
            try:
                self._srccode = Path(self.filename).read_text(encoding="utf-8")
            except Exception:
                return

        for line, col, message in _check_all(self._srccode):
            yield line, col, message, type(self)
