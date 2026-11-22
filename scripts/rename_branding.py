"""One-time, tracked-file-only ArkiLab -> OrkiLab rename for the source tree.

Usage: python scripts/rename_branding.py --apply
This intentionally does not rewrite Git history, local user data or binary blobs.
A preexisting destination always wins over an obsolete legacy asset.
"""
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OLD = "arki" + "lab"
NEW = "orki" + "lab"
PATTERN = re.compile(OLD, re.IGNORECASE)
BINARY = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".svgz",
          ".woff", ".woff2", ".ttf", ".otf", ".zip", ".pdf", ".db", ".sqlite3",
          ".safetensors", ".mp4", ".mp3", ".wav"}


def replace_brand(match):
    word = match.group()
    if word.isupper():
        return NEW.upper()
    if word.islower():
        return NEW
    return "OrkiLab"


def converted(value):
    return PATTERN.sub(replace_brand, value)


def files():
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT,
                            capture_output=True, check=True)
    return [Path(x.decode("utf-8")) for x in result.stdout.split(b"\0") if x]


def migrate(apply=False):
    changes = []
    for relative in files():
        source = ROOT / relative
        if not source.is_file():
            continue
        destination = ROOT / converted(relative.as_posix())
        name_changed = destination != source
        text = None
        if source.suffix.lower() not in BINARY and source.stat().st_size <= 4_000_000:
            try:
                original = source.read_text(encoding="utf-8")
                text = converted(original)
                if text == original:
                    text = None
            except (UnicodeError, OSError):
                pass
        if not name_changed and text is None:
            continue
        if name_changed and destination.exists():
            # Legacy artwork duplicates modern, actively used asset paths.
            # Never overwrite newer destination files with older branding assets.
            changes.append(f"DROP-OBSOLETE {relative}")
            if apply:
                source.unlink()
            continue
        changes.append(f"{relative} -> {destination.relative_to(ROOT) if name_changed else 'content'}")
        if not apply:
            continue
        if name_changed:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if text is None:
                destination.write_bytes(source.read_bytes())
            else:
                destination.write_text(text, encoding="utf-8")
            source.unlink()
        elif text is not None:
            source.write_text(text, encoding="utf-8")
    for line in changes:
        print(line)
    print(f"Total renamed/updated files: {len(changes)}")
    return len(changes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Modify tracked files in place (otherwise dry-run)")
    args = parser.parse_args()
    migrate(apply=args.apply)
