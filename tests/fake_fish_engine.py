#!/usr/bin/env python3
"""Deterministic process-boundary fake used by the ModForge live contract test."""

import argparse
import json
import os
from pathlib import Path
import sys
import wave


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--ref-audio")
    parser.add_argument("--ref-text")
    parser.add_argument("--model")
    parser.add_argument("--rvc")
    parser.add_argument("--seed")
    parser.add_argument("--speed")
    parser.add_argument("--exaggeration")
    parser.add_argument("--language")
    parser.add_argument("--emotion")
    parser.add_argument("--intensity")
    args = parser.parse_args()

    log_path = os.environ.get("MODFORGE_FAKE_FISH_LOG")
    if not log_path:
        print("MODFORGE_FAKE_FISH_LOG is required", file=sys.stderr)
        return 2
    with Path(log_path).open("a", encoding="utf-8") as log:
        log.write(json.dumps(vars(args), sort_keys=True) + "\n")

    if args.text == "__nonzero__":
        print("deterministic fake failure", file=sys.stderr)
        return 23
    if args.text == "__missing__":
        return 0

    out = Path(args.out)
    if args.text == "__header_only__":
        with wave.open(str(out), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(24_000)
        return 0
    if args.text == "__truncated__":
        out.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt ")
        return 0

    with wave.open(str(out), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24_000)
        wav.writeframes(b"\x00\x00\x01\x00" * 32)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
