import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import wave


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import voicegen


def write_wav(path, frames=b"\x00\x00" * 32):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24_000)
        wav.writeframes(frames)


class VoicegenTests(unittest.TestCase):
    def run_main(self, *args, fish_run=None):
        argv = ["voicegen.py", *args]
        stderr = io.StringIO()
        stdout = io.StringIO()
        patches = [
            mock.patch.object(sys, "argv", argv),
            mock.patch.dict(os.environ, {"MODFORGE_FISH_SPEECH_BIN": "fake-fish"}),
            mock.patch("voicegen.subprocess.run", side_effect=fish_run),
        ]
        with patches[0], patches[1], patches[2], contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            voicegen.main()
        return stdout.getvalue(), stderr.getvalue()

    def test_fish_forwards_rvc_and_atomically_publishes_valid_wav(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "line.wav"
            out.write_bytes(b"old output")
            seen = []

            def fake_run(command, **kwargs):
                seen.append(command)
                temp_out = Path(command[command.index("--out") + 1])
                self.assertNotEqual(temp_out, out)
                write_wav(temp_out)
                return subprocess.CompletedProcess(command, 0, "", "")

            stdout, _ = self.run_main(
                "--engine", "fish-s2", "--text", "hello", "--out", str(out),
                "--rvc", "voice.pth", fish_run=fake_run,
            )

            self.assertIn("Generated:", stdout)
            self.assertEqual(seen[0][seen[0].index("--rvc") + 1], "voice.pth")
            voicegen._validate_wav(out)
            self.assertEqual(list(Path(directory).glob("*.tmp.wav")), [])

    def test_missing_fish_output_fails_without_blessing_stale_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "line.wav"
            out.write_bytes(b"known-good-old-output")

            def fake_run(command, **kwargs):
                return subprocess.CompletedProcess(command, 0, "", "")

            with self.assertRaises(SystemExit) as raised:
                self.run_main(
                    "--engine", "fish", "--text", "hello", "--out", str(out),
                    fish_run=fake_run,
                )

            self.assertEqual(raised.exception.code, 1)
            self.assertEqual(out.read_bytes(), b"known-good-old-output")
            self.assertEqual(list(Path(directory).glob("*.tmp.wav")), [])

    def test_unknown_engine_reports_failure_on_stderr(self):
        stderr = io.StringIO()
        stdout = io.StringIO()
        argv = ["voicegen.py", "--engine", "unknown", "--text", "x", "--out", "out.wav"]
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                voicegen.main()

        self.assertEqual(raised.exception.code, 1)
        self.assertIn("Unknown engine", stderr.getvalue())
        self.assertNotIn("Unknown engine", stdout.getvalue())

    def test_rejects_header_only_wav(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.wav"
            write_wav(path, frames=b"")
            with self.assertRaisesRegex(RuntimeError, "empty or invalid"):
                voicegen._validate_wav(path)


if __name__ == "__main__":
    unittest.main()
