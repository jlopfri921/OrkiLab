"""Audit obsolete product branding in tracked source files and filenames.

Legacy internal compatibility identifiers may require migration before renaming;
this diagnostic intentionally reports, rather than blindly rewriting, those.
"""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
OLD = "arki" + "lab"
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}
BINARY = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".svgz",
          ".woff", ".woff2", ".ttf", ".otf", ".zip", ".pdf", ".db", ".sqlite3",
          ".safetensors", ".mp4", ".mp3", ".wav"}
MAX_BYTES = 4_000_000

class BrandAudit(unittest.TestCase):
    def test_report_obsolete_brand_occurrences(self):
        report = []
        for path in ROOT.rglob("*"):
            if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
                continue
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if OLD in rel.lower():
                report.append(f"FILEPATH {rel}")
            if path.suffix.lower() in BINARY or path.stat().st_size > MAX_BYTES:
                continue
            try:
                data = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for number, line in enumerate(data.splitlines(), 1):
                if OLD in line.lower():
                    report.append(f"{rel}:{number}: {line.strip()[:220]}")
        self.assertEqual(report, [], "Obsolete OrkiLab references (including filenames):\n" +
                         "\n".join(report[:500]) +
                         ("\n[truncated]" if len(report) > 500 else ""))

if __name__ == "__main__":
    unittest.main()
