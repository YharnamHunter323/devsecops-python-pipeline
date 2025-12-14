# Security Scan Summary

## Static Application Security Testing (Semgrep)
Findings detected: **0**
Output: `semgrep-report.sarif`

## Secrets Scanning (detect-secrets)
Baseline-based scanning enabled.
New secrets detected vs baseline: **0**
Output: `reports/summary.json`

## Container Image Scan (Trivy)
Total vulnerabilities found: **68**
Output: `trivy-report.json`

## Runtime / DAST Scan (OWASP ZAP)
Baseline scan completed against running application.
Warnings detected: **7**
No high-risk findings.
Output: `reports/zap-report.html`

_For full details see attached SARIF/JSON/HTML artifacts._
