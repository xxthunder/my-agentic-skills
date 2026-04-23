# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Merge values into naps2-scan config (atomic write).

Only keys passed via flags are updated; existing keys are preserved.
Exit 0 on success, 1 if the file or its parent dir cannot be written.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def config_path() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "naps2-scan" / "config.json"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "naps2-scan" / "config.json"


_FLAG_TO_KEY = {
    "exe_path": "exe_path",
    "profile": "default_profile",
    "ocr_lang": "default_ocr_lang",
    "scanner_type": "default_scanner_type",
}


def merge_config(existing: dict, updates: dict) -> dict:
    """Return existing merged with non-None entries of updates.

    `updates` uses the CLI flag names (with underscores). Only keys whose
    value is not None overwrite the corresponding config key.
    """
    merged = dict(existing)
    for flag, key in _FLAG_TO_KEY.items():
        value = updates.get(flag)
        if value is not None:
            merged[key] = value
    return merged


def atomic_write(path: Path, data: dict) -> None:
    """Write JSON to *path* via tmp-file + os.replace."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe-path")
    parser.add_argument("--profile")
    parser.add_argument("--ocr-lang")
    parser.add_argument("--scanner-type", choices=["simplex", "duplex"])
    args = parser.parse_args()

    path = config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"cannot create config dir: {e}", file=sys.stderr)
        return 1

    existing: dict = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                existing = loaded
        except (OSError, json.JSONDecodeError):
            existing = {}

    data = merge_config(existing, vars(args))

    try:
        atomic_write(path, data)
    except OSError as e:
        print(f"cannot write config: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
