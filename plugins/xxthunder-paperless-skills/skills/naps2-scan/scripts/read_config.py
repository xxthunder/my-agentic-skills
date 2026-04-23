# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Read naps2-scan config; print JSON to stdout.

Exit codes:
  0 — config parsed (and, with --validate-exe, exe_path is valid)
  1 — config missing, unreadable, or invalid JSON
  2 — config parsed but --validate-exe and exe_path points at a nonexistent file
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


def load_config(path: Path) -> dict | None:
    """Return the config dict at *path*, or None on any read/parse error."""
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def exe_is_valid(data: dict) -> bool:
    """True if *data* has no `exe_path` key, or the path points at a file."""
    exe = data.get("exe_path")
    if not exe:
        return True
    return Path(exe).is_file()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-exe", action="store_true")
    args = parser.parse_args()

    data = load_config(config_path())
    if data is None:
        return 1

    print(json.dumps(data))

    if args.validate_exe and not exe_is_valid(data):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
