#!/usr/bin/env python3
# compare_and_summarize.py
# Usage:
#   python compare_and_summarize.py <baseline.json> <current.json> [--limit N] [--topfiles M]
#
# Outputs:
#   - new_findings.txt       (human-readable list, limited to --limit)
#   - top_files.txt          (top M files by finding count)
#   - summary.json           (counts: baseline, current, new)
#
import json, sys, argparse, collections, os

def load(path):
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)

def extract_findings(scan_json):
    """
    Return list of tuples (file, plugin, sample)
    """
    out = []
    results = scan_json.get('results') or {}
    # results may be dict filename -> list
    if isinstance(results, dict):
        for fname, issues in results.items():
            for issue in issues or []:
                plugin = issue.get('type') or issue.get('check_name') or issue.get('name') or issue.get('plugin') or ''
                secret = issue.get('secret') or issue.get('hashed_secret') or issue.get('line') or ''
                sample = str(secret)[:200]
                out.append((fname, str(plugin), sample))
    # fallback if different layout: try scanning top-level list
    elif isinstance(scan_json, list):
        for issue in scan_json:
            fname = issue.get('filename') or issue.get('path') or ''
            plugin = issue.get('type') or issue.get('name') or ''
            sample = str(issue.get('secret') or '')[:200]
            out.append((fname, plugin, sample))
    return out

def make_key(t):
    # file|plugin|first40chars
    f,p,s = t
    return f + '|' + p + '|' + (s[:40] if s else '')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('baseline')
    p.add_argument('current')
    p.add_argument('--limit', type=int, default=100, help='max number of new findings to include in new_findings.txt')
    p.add_argument('--topfiles', type=int, default=20, help='number of top files to list')
    args = p.parse_args()

    base = load(args.baseline)
    cur  = load(args.current)

    base_list = extract_findings(base)
    cur_list  = extract_findings(cur)

    base_set = set(make_key(x) for x in base_list)
    cur_set  = set(make_key(x) for x in cur_list)

    new_keys = cur_set - base_set

    new_items = [x for x in cur_list if make_key(x) in new_keys]

    # top files by count in current scan
    file_counts = collections.Counter([f for f,_,_ in cur_list])
    top_files = file_counts.most_common(args.topfiles)

    # write outputs
    os.makedirs('reports', exist_ok=True)
    with open('reports/new_findings.txt','w',encoding='utf-8') as fh:
        fh.write(f"New findings (showing up to {args.limit} items)\n")
        fh.write("="*60 + "\n\n")
        for i, (f,p,s) in enumerate(new_items[:args.limit], start=1):
            fh.write(f"{i}. file: {f}\n   plugin: {p}\n")
            if s:
                fh.write(f"   sample: {s}\n")
            fh.write("\n")
        if len(new_items) > args.limit:
            fh.write(f"... output truncated ({len(new_items)} total new findings)\n")

    with open('reports/top_files.txt','w',encoding='utf-8') as fh:
        fh.write("Top files by total findings in current scan\n")
        fh.write("="*60 + "\n\n")
        for i,(fname,cnt) in enumerate(top_files, start=1):
            fh.write(f"{i:3d}. {cnt:4d}  {fname}\n")

    summary = {
        "baseline_findings": len(base_list),
        "current_findings": len(cur_list),
        "new_findings_total": len(new_items),
        "top_files_report": "reports/top_files.txt",
        "new_findings_report": "reports/new_findings.txt"
    }
    with open('reports/summary.json','w',encoding='utf-8') as fh:
        json.dump(summary, fh, indent=2)

    print("Wrote:")
    print(" - reports/new_findings.txt")
    print(" - reports/top_files.txt")
    print(" - reports/summary.json")
    print(f"Total new findings: {len(new_items)} (summary in reports/summary.json)")

if __name__ == '__main__':
    main()
