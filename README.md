# DevSecOps Pipeline with Automated Code Scanning (Python)


Demo project that shows a two-tier security pipeline for a Python Flask app using GitHub Actions:


- PR quick checks: semgrep (SAST), detect-secrets (secrets), dependency-review (SCA)
- Full scans on `main` / nightly: CodeQL, Trivy (image scanning), OWASP ZAP (DAST)
- Aggregated report artifact


See `.github/workflows/` for CI definitions and `.github/scripts/report-aggregate.py` for report generation.


## How to run locally


1. Build and run the sample app with Docker Compose:


```bash
docker-compose up --build
```
2. Visit http://localhost:8080.

3. Run local semgrep scan (if installed):
semgrep --config .semgrep/rules

4.Generate detect-secrets baseline (locally):
pip install detect-secrets
detect-secrets scan > .detect-secrets.baseline

