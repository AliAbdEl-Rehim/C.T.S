#!/usr/bin/env python3
"""Static structure checks for mkt_handoff.pine."""

from __future__ import annotations

import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
PINE = ROOT / "mkt_handoff.pine"


def strip_strings_and_comments(source: str) -> str:
    no_block = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    no_line = re.sub(r"//.*?$", "", no_block, flags=re.M)
    no_strings = re.sub(r'"(?:\\.|[^"\\])*"', '""', no_line)
    return no_strings


def balance(source: str, opener: str, closer: str) -> int:
    return source.count(opener) - source.count(closer)


def main() -> int:
    text = PINE.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("// This Pine Script"):
        errors.append("missing MPL header")
    if "//@version=6" not in text.splitlines()[:6]:
        errors.append("missing //@version=6")
    if 'indicator(\n     "Global Cash Market Open Close Handoff Sequence"' not in text:
        errors.append("missing indicator declaration")

    required_snippets = [
        "GROUP_SIGNALS",
        "enableContinuationSignals",
        "f_continuationScore",
        "f_failureScore",
        "continueSignal",
        "failSignal",
        "barstate.isconfirmed",
        "twoBarConfirmation",
        "f_boundaryDuringBar",
        "f_volumeSupportive",
        "STRUCTURE PULLBACK",
        "time_close",
        "استكمال الصعود",
        "فشل الصعود",
        'alertcondition(continueSignal',
        'alertcondition(failSignal',
        "SIGNAL",
        "SETUP",
    ]
    for snippet in required_snippets:
        if snippet not in text:
            errors.append(f"missing required snippet: {snippet}")

    cleaned = strip_strings_and_comments(text)
    for opener, closer, name in (("(", ")", "parentheses"), ("[", "]", "brackets")):
        delta = balance(cleaned, opener, closer)
        if delta != 0:
            errors.append(f"unbalanced {name}: {delta}")

    if re.search(r"(?m)^\s+continue\b", cleaned):
        errors.append("found unsupported 'continue' statement")
    if re.search(r"for\s+\w+\s+in\s+", cleaned):
        errors.append("found unsupported for-in loop")

    function_defs = set(re.findall(r"^([A-Za-z_][A-Za-z0-9_]*)\(", text, flags=re.M))
    builtin_or_declared = function_defs | {
        "indicator",
        "input",
        "array",
        "color",
        "str",
        "math",
        "ta",
        "table",
        "label",
        "line",
        "plot",
        "plotshape",
        "alert",
        "alertcondition",
        "timestamp",
        "year",
        "month",
        "dayofmonth",
        "dayofweek",
        "na",
        "int",
        "float",
        "bool",
        "string",
        "switch",
        "not",
        "nz",
        "barstate",
        "timeframe",
        "chart",
        "syminfo",
        "display",
        "position",
        "size",
        "text",
        "font",
        "xloc",
        "yloc",
        "extend",
        "order",
        "location",
        "shape",
        "Market",
    }
    calls = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", cleaned))
    unknown = sorted(
        name
        for name in calls
        if name.startswith("f_") and name not in builtin_or_declared
    )
    if unknown:
        errors.append(f"undefined helper calls: {unknown}")

    if "max_labels_count = 400" not in text:
        errors.append("signal label budget was not raised")

    if errors:
        print("PINE STRUCTURE CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PINE STRUCTURE CHECK PASSED")
    print(f"lines={text.count(chr(10)) + 1}")
    print(f"helpers={len([name for name in function_defs if name.startswith('f_')])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
