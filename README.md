# DevSecOps Pipeline with Automated Security Scanning

## Overview

This project implements a **local and CI-based DevSecOps pipeline** for a Python application. The goal is to demonstrate how security can be integrated throughout the software delivery lifecycle using industry-standard tools for **SAST, secrets detection, container scanning, and DAST**.

The pipeline runs:

* **Locally** via a single PowerShell script (`run_all_local.ps1`)
* **In CI** using GitHub Actions (`.github/workflows/full-security-scan.yml`)

This project was developed for an academic DevSecOps assignment and emphasizes clarity, reproducibility, and realistic tooling.

---

## Architecture & Tools

### Application

* **Language:** Python
* **Runtime:** Docker + Docker Compose
* **App entry point:** `app.py`

### Security Tooling

| Category  | Tool           | Purpose                                       |
| --------- | -------------- | --------------------------------------------- |
| SAST      | CodeQL         | Static code analysis (GitHub-native)          |
| SAST      | Semgrep        | Custom Python security rules                  |
| Secrets   | detect-secrets | Detect hardcoded secrets in Git history       |
| Container | Trivy          | Scan Docker images for vulnerabilities        |
| DAST      | OWASP ZAP      | Baseline dynamic application security testing |

---

## Repository Structure

```
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run_all_local.ps1
├── run_detect_secrets_tracked_filtered.py
├── clean_detect_secrets.py
├── compare_and_summarize.py
├── .detect-secrets.baseline
├── .semgrep/
│   └── rules/
├── .github/
│   ├── workflows/
│   │   └── full-security-scan.yml
│   └── scripts/
│       └── report-aggregate.py
├── reports/              # Generated locally / in CI
├── README.md
```

Generated artifacts (reports, scan outputs) are **excluded from Git** and only uploaded as CI artifacts.

---

## Local Pipeline Execution

### Prerequisites

* Docker Desktop (running)
* Python 3.10+
* PowerShell (Windows)

Optional but recommended:

* Python virtual environment (`.venv`)

### One-Time Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pre-commit install
```

### Run the Full Local Pipeline

```powershell
.\run_all_local.ps1
```

This will:

1. Build the Docker image
2. Start the application via Docker Compose
3. Run Semgrep (SAST)
4. Run detect-secrets and compare against baseline
5. Run Trivy image scan
6. Run OWASP ZAP baseline scan
7. Aggregate results into a security summary
8. Tear down the environment

Artifacts are written locally for inspection.

---

## GitHub Actions CI Pipeline

### Workflow Trigger

The workflow runs on:

* Pushes to `main`
* A nightly scheduled run (02:00 UTC)

### CI Jobs

1. **CodeQL Analysis**

   * GitHub-native SAST
   * Results appear in the *Security → Code scanning* tab

2. **Trivy Image Scan**

   * Builds the Docker image
   * Scans for OS and dependency vulnerabilities
   * Uploads JSON artifact

3. **OWASP ZAP DAST**

   * Starts the application container
   * Runs ZAP baseline scan against the live app
   * Generates `zap_report.html`

4. **Aggregation**

   * Combines Trivy + ZAP results
   * Produces `reports/security-summary.md`

All reports are uploaded as GitHub Actions artifacts.

---

## OWASP ZAP Notes

The ZAP baseline scan may produce warnings such as:

```
WARN-NEW: Insufficient Site Isolation Against Spectre
```

These are **informational security warnings**, not exploitable application bugs. For this reason:

* ZAP findings **do not fail the pipeline**
* Reports are reviewed manually

This reflects real-world CI/CD security practices.

---

## Secrets Management

* `detect-secrets` is enforced via **pre-commit hooks**
* `.detect-secrets.baseline` is the approved baseline
* New secrets introduced after baseline creation will block commits

Generated scan files are excluded via `.gitignore`.

---

## Educational Outcomes

This project demonstrates:

* Shift-left security practices
* Tool chaining in DevSecOps pipelines
* Differences between local and CI execution
* Handling security findings without blocking delivery

---

## Future Improvements

Possible extensions:

* Runtime security (Falco / eBPF)
* Dependency update automation (Dependabot)
* Policy-as-code enforcement
* CVSS-based gating

---
