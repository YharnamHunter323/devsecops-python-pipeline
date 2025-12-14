# clean_detect_secrets.py
import json, sys, os

if len(sys.argv) != 3:
    print("Usage: python clean_detect_secrets.py <input.json> <output.json>")
    sys.exit(1)

inp, out = sys.argv[1], sys.argv[2]

if not os.path.exists(inp):
    print(f"ERROR: input file not found: {inp}")
    sys.exit(2)

j = json.load(open(inp, 'r', encoding='utf-8'))
results = j.get('results', {})

# Files / substrings to exclude from cleaned results
exclude_substrings = [
    '.git/', '.github/',
    '.detect-secrets', 'detect-secrets',    # baseline and artifact names
    '.venv/', '.venv\\',                    # virtualenv (Windows/Unix path separators)
    'venv/', 'venv\\'
]

# Exact filenames to exclude
exclude_exact = {
    '.detect-secrets.baseline',
    '.detect-secrets.baseline.cleaned',
    '.detect-secrets.scan.json',
    'detect-secrets-current.json',
    'detect-secrets-current-cleaned.json',
    'detect-secrets-scan.json',
}

cleaned = {}
removed_files = 0
for fname, issues in results.items():
    # Normalize to a consistent representation for matching
    fname_norm = fname.replace('\\', '/')
    # exact-match check
    if os.path.basename(fname) in exclude_exact:
        removed_files += 1
        continue
    # substring-based exclusions
    skip = False
    for sub in exclude_substrings:
        # treat slash normalized substrings the same
        if sub.replace('\\','/') in fname_norm:
            skip = True
            break
    if skip:
        removed_files += 1
        continue
    cleaned[fname] = issues

j['results'] = cleaned
with open(out, 'w', encoding='utf-8') as fh:
    json.dump(j, fh, indent=2)

print(f"Wrote cleaned scan to {out}; removed {removed_files} files worth of findings.")
