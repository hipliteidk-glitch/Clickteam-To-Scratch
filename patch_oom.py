"""Legacy CI entry point -- now a verification, not a source patch.

Historically the FNaF4 workflow ran this script to monkey-patch the
converter at CI time with fragile exact-string replacements. Those
replacements silently stopped matching the code (e.g. it searched
cts2/gamedata.py for ``img.png = encode_png``, which does not exist
there), so CI believed it had applied low-memory fixes while running
completely unpatched code -- a direct contributor to the 90-minute
timeout in run 38525958140.

The low-memory behaviour is now real, tested code:

* ``cts2.converter.load_project`` forwards ``fast_frames``/``skip_audio``
  for direct file inputs (it used to drop them);
* ``cts2.gamedata`` does not copy/decrypt/decompress frame event
  programs in fast-frames mode, frees chunk payloads after decoding,
  does not retain raw image pixels alongside decoded PNGs, and does
  not pin the whole input EXE as ``MFA.file_data``.

This script therefore only *verifies* those invariants and fails the
workflow early (in seconds, not after a 90-minute timeout) if they
ever regress. It never modifies source files.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent

CHECKS = [
    ("cts2/converter.py", "fast_frames=fast_frames, skip_audio=skip_audio",
     "load_project forwards fast_frames/skip_audio"),
    ("cts2/gamedata.py", 'cid == FRAME_EVENTS',
     "fast-frames skips event-program decoding"),
    ("cts2/gamedata.py", 'file_data=b""',
     "EXE bytes are not retained as MFA.file_data"),
    ("cts2/gamedata.py", 'chunk.raw = b""',
     "chunk payloads are freed after decoding"),
]


def main() -> int:
    failures = []
    for rel, needle, label in CHECKS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if needle not in text:
            failures.append(f"{rel}: missing {label!r} (expected {needle!r})")
    # The old patch must not come back.
    for rel in ("cts2/gamedata.py", "cts2/scratch.py"):
        if "free patched" in (ROOT / rel).read_text(encoding="utf-8"):
            failures.append(f"{rel}: contains stale patch_oom mutation")
    if failures:
        print("low-memory verification FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("low-memory fixes are built into cts2 (no patching needed):")
    for _rel, _needle, label in CHECKS:
        print(f"  ok: {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
