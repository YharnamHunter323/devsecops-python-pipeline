#!/usr/bin/env python3
import json, argparse, os


def load(path):
    try:
        return json.load(open(path))
    except Exception:
        return None


parser = argparse.ArgumentParser()
parser.add_argument('--trivy')
parser.add_argument('--zapprobe')
parser.add_argument('--output', required=True)
args = parser.parse_args()


lines = ['# Security Scan Summary\n']


if args.trivy and os.path.exists(args.trivy):
    data = load(args.trivy)
    if data:
        vulns = 0
        if isinstance(data, dict) and 'Results' in data:
            for r in data['Results']:
                vulns += len(r.get('Vulnerabilities') or [])
        lines.append('## Container Image Scan (Trivy)\nTotal vulnerabilities found: **{}**\n'.format(vulns))


if args.zapprobe and os.path.exists(args.zapprobe):
    zap = load(args.zapprobe)
    if zap:
        # ZAP JSON structure varies; attempt to find alerts
        alerts = 0
        if 'site' in zap and isinstance(zap['site'], list):
            for s in zap['site']:
                alerts += len(s.get('alerts') or [])
        lines.append('## DAST (ZAP)\nFindings (approx): **{}**\n'.format(alerts))


lines.append('\n_For full details see attached SARIF/JSON artifacts._\n')
open(args.output, 'w').write('\n'.join(lines))
print('Wrote', args.output)