#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import subprocess
import struct
import sys
import uuid

def _temporary_output(out_path):
    """Return a unique sibling path so a failed run cannot bless a stale output."""
    out = Path(out_path)
    return out.with_name(f".{out.name}.{uuid.uuid4().hex}.tmp.wav")


def _validate_wav(path):
    """Reject missing, truncated, and header-only RIFF/WAVE output."""
    try:
        file_size = Path(path).stat().st_size
        with Path(path).open("rb") as wav:
            header = wav.read(12)
            if len(header) != 12 or header[:4] != b"RIFF" or header[8:] != b"WAVE":
                raise RuntimeError("engine output is not a RIFF/WAVE file")
            riff_size = struct.unpack_from("<I", header, 4)[0]
            if riff_size + 8 > file_size:
                raise RuntimeError("engine created a truncated WAV")

            fmt_valid = False
            data_size = 0
            riff_end = riff_size + 8
            while wav.tell() + 8 <= riff_end:
                chunk_header = wav.read(8)
                chunk_id, chunk_size = struct.unpack("<4sI", chunk_header)
                chunk_start = wav.tell()
                chunk_end = chunk_start + chunk_size
                if chunk_end > riff_end or chunk_end > file_size:
                    raise RuntimeError("engine created a truncated WAV")
                if chunk_id == b"fmt ":
                    fmt = wav.read(min(chunk_size, 16))
                    if len(fmt) < 16:
                        raise RuntimeError("engine created an invalid WAV format chunk")
                    _, channels, frame_rate, _, block_align, _ = struct.unpack("<HHIIHH", fmt)
                    fmt_valid = channels > 0 and frame_rate > 0 and block_align > 0
                elif chunk_id == b"data":
                    data_size = chunk_size
                wav.seek(chunk_end + (chunk_size & 1))
    except (FileNotFoundError, OSError, EOFError, struct.error) as exc:
        raise RuntimeError(f"engine did not create a valid WAV: {exc}") from exc

    if not fmt_valid or data_size <= 0:
        raise RuntimeError("engine created an empty or invalid WAV")


def _publish_output(temp_path, out_path):
    _validate_wav(temp_path)
    try:
        os.replace(temp_path, out_path)
    except OSError as exc:
        raise RuntimeError(f"could not publish WAV: {exc}") from exc


def main():
    print(f"DEBUG voicegen.py received args: {sys.argv}", file=sys.stderr)
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--ref-wav")
    parser.add_argument("--ref-text")
    parser.add_argument("--model")
    parser.add_argument("--rvc")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--speed", type=float, default=1.0)
    # Engine-specific knobs: accepted for every engine so callers can always pass them;
    # engines that have no use for one simply ignore it (with a stderr note) instead of crashing.
    parser.add_argument("--exaggeration", type=float, default=None)
    parser.add_argument("--language", default=None)
    # Delivery emotion from the dialogue INFO record (Skyrim's 8: Neutral/Anger/Disgust/
    # Fear/Sad/Happy/Surprise/Puzzled) + intensity 0-100. Engines map these to expressive
    # delivery if they can; an engine with no equivalent notes+ignores, like --exaggeration.
    parser.add_argument("--emotion", default=None)
    parser.add_argument("--intensity", type=int, default=None)
    args = parser.parse_args()

    engine = args.engine.lower()
    temp_out = _temporary_output(args.out)

    try:
        if engine == "f5":
            # F5-TTS only supports speed; exaggeration/emotion have no equivalent and the
            # language is inferred from the reference clip/text. Note + ignore rather than fail.
            if args.exaggeration is not None:
                print("NOTE: f5 engine has no exaggeration control; ignoring --exaggeration", file=sys.stderr)
            if args.emotion is not None and args.emotion not in ("", "Neutral"):
                print(f"NOTE: f5 engine has no emotion control; ignoring --emotion {args.emotion} (intensity {args.intensity})", file=sys.stderr)
            if args.language is not None and args.language not in ("en", ""):
                print(f"NOTE: f5 engine infers language from the reference; ignoring --language {args.language}", file=sys.stderr)
            try:
                from f5_tts.api import F5TTS
                f5 = F5TTS()

                # F5 auto-transcribes the reference clip (its own ASR) when ref_text is "".
                # We pass "" rather than None so a vanilla-extracted clip needs no hand transcript.
                ref_text = args.ref_text if args.ref_text else ""

                f5.infer(
                    ref_file=args.ref_wav,
                    ref_text=ref_text,
                    gen_text=args.text,
                    file_wave=str(temp_out),
                    seed=args.seed,
                    speed=args.speed
                )
            except Exception as exc:
                print(f"ERROR in F5-TTS: {exc}", file=sys.stderr)
                sys.exit(1)
            engine_name = "F5-TTS"

        elif engine in ("fish", "fish-s2", "fishspeech", "fish-speech"):
            fish_bin = os.environ.get("MODFORGE_FISH_SPEECH_BIN")
            if not fish_bin:
                print(
                    "ERROR: fish-s2 requires MODFORGE_FISH_SPEECH_BIN. Point it at a local Fish Speech "
                    "wrapper that accepts --text/--out/--ref-audio/--ref-text and writes a WAV.",
                    file=sys.stderr,
                )
                sys.exit(1)

            cmd = [fish_bin, "--text", args.text, "--out", str(temp_out)]
            if args.ref_wav:
                cmd += ["--ref-audio", args.ref_wav]
            if args.ref_text:
                cmd += ["--ref-text", args.ref_text]
            if args.model:
                cmd += ["--model", args.model]
            if args.rvc:
                cmd += ["--rvc", args.rvc]
            if args.seed is not None:
                cmd += ["--seed", str(args.seed)]
            if args.speed is not None:
                cmd += ["--speed", str(args.speed)]
            if args.exaggeration is not None:
                cmd += ["--exaggeration", str(args.exaggeration)]
            if args.language:
                cmd += ["--language", args.language]
            if args.emotion:
                cmd += ["--emotion", args.emotion]
            if args.intensity is not None:
                cmd += ["--intensity", str(args.intensity)]

            print(f"    Fish Speech command: {' '.join(cmd)}", file=sys.stderr)
            try:
                result = subprocess.run(cmd, check=False, text=True, capture_output=True)
            except FileNotFoundError:
                print(f"ERROR: MODFORGE_FISH_SPEECH_BIN not found: {fish_bin}", file=sys.stderr)
                sys.exit(1)

            if result.stdout:
                print(result.stdout, file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            if result.returncode != 0:
                print(f"ERROR: Fish Speech wrapper failed with exit code {result.returncode}", file=sys.stderr)
                sys.exit(result.returncode)
            engine_name = "Fish Speech wrapper"

        else:
            print(f"Unknown engine: {args.engine}", file=sys.stderr)
            sys.exit(1)

        try:
            _publish_output(temp_out, args.out)
        except RuntimeError as exc:
            print(f"ERROR: {engine_name} {exc}", file=sys.stderr)
            sys.exit(1)
        print(f"Generated: {args.out}")
    finally:
        try:
            temp_out.unlink()
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    main()
