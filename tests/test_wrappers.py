from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WrapperTests(unittest.TestCase):
    def test_f5_default_venv_is_inside_standalone_repo(self):
        script = (ROOT / "voicegen-f5.sh").read_text(encoding="utf-8")
        self.assertIn('${MODFORGE_VOICEGEN_VENV:-$HERE/.venvs/f5}', script)
        self.assertNotIn('$HERE/../..', script)

    def test_legacy_default_venv_is_inside_standalone_repo(self):
        script = (ROOT / "voicegen.sh").read_text(encoding="utf-8")
        self.assertIn('${MODFORGE_VOICEGEN_VENV:-$HERE/venv_voice}', script)
        self.assertNotIn('$HERE/../..', script)


if __name__ == "__main__":
    unittest.main()
