#!/usr/bin/env python3
# run_detect_secrets_tracked_filtered.py
# Runs detect-secrets scan only on git-tracked files EXCLUDING common artifact and venv paths.
#
# Usage:
#   python run_detect_secrets_tracked_filtered.py <output.json>
#
import subprocess, sys, shutil, json, os

if len(sys.argv) != 2:
    print("Usage: python run_detect_secrets_tracked_filtered.py <output.json>")
    sys.exit(1)

out_path = sys.argv[1]

if not shutil.which("detect-secrets"):
    print("ERROR: detect-secrets not found in PATH. Activate your venv.")
    sys.exit(2)

# get tracked files
try:
    p = subprocess.run(["git", "ls-files"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    tracked = [s for s in p.stdout.splitlines() if s.strip()]
except subprocess.CalledProcessError as e:
    print("ERROR: git ls-files failed:", e.stderr)
    sys.exit(3)

if not tracked:
    print("No tracked files found.")
    sys.exit(0)

# exclusion patterns (substring matches)
exclude_substrings = [
    ".detect-secrets",
    "detect-secrets",
    ".venv/",
    ".venv\\",
    "venv/",
    "venv\\",
    ".git/",
    ".github/"
]

def keep_file(f):
    fnorm = f.replace("\\","/")
    for sub in exclude_substrings:
        if sub in fnorm:
            return False
    return True

filtered = [f for f in tracked if keep_file(f)]
if not filtered:
    print("No files left after filtering; aborting.")
    sys.exit(0)

print(f"Scanning {len(filtered)} tracked files (excluded patterns: {exclude_substrings})")

# Run detect-secrets on the filtered list
cmd = ["detect-secrets", "scan"] + filtered
try:
    p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw = p.stdout
    try:
        text = raw.decode("utf-8")
    except Exception:
        text = raw.decode("latin-1")
    parsed = json.loads(text)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(parsed, fh, indent=2)
    print(f"Wrote filtered scan to {out_path}")
    sys.exit(0)
except subprocess.CalledProcessError as e:
    stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
    print("detect-secrets failed. stderr:")
    print(stderr)
    sys.exit(4)
