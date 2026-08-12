#!/bin/bash
# Legacy wrapper: run voicegen.py inside the older venv_voice (python 3.12). The live
# pipeline uses voicegen-f5.sh (.venvs/f5, python 3.11) — prefer that. Kept for reference.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${MODFORGE_VOICEGEN_VENV:-$HERE/venv_voice}"
source "$VENV/bin/activate"
exec python3 "$HERE/voicegen.py" "$@"
