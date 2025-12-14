# DevSecOps Pipeline with Automated Code Scanning (Python)

## 1. Project Overview

This project implements a **DevSecOps pipeline** for a simple Python web application, focusing on integrating security checks throughout the software development lifecycle. The goal is to demonstrate how security can be automated and embedded into development workflows using industry-standard tools.

The pipeline covers:
- **Commit-time security** (secrets detection)
- **Build-time security** (static analysis and dependency/container scanning)
- **Runtime security** (dynamic application security testing)
- **Automated reporting and aggregation** of results

The project is intentionally small in scope (a minimal Python application) to keep the focus on the **security tooling, automation, and trade-offs**, rather than application complexity.

---

## 2. Architecture and Tooling

### Application
- **Language:** Python
- **Framework:** Minimal Flask-based web service
- **Containerized:** Docker + Docker Compose

### Security Toolchain

| Phase | Tool | Purpose |
|-----|-----|-----|
| Pre-commit | detect-secrets | Prevent committing secrets to the repository |
| SAST | Semgrep | Static code analysis for insecure patterns |
| Image / Dependency Scan | Trivy | Scan container images for known vulnerabilities |
| DAST / Runtime | OWASP ZAP | Scan the running application for runtime security issues |
| Reporting | Custom aggregation scripts | Summarize results into readable artifacts |

---

## 3. Security Use Cases

This project explicitly addresses multiple security use cases, as required for a DevSecOps pipeline.

### 3.1 Commit-Time Security: Secrets Scanning

- **Tool:** detect-secrets
- **Mechanism:**
  - A baseline file (`.detect-secrets.baseline`) is generated and tracked.
  - New scans are compared against this baseline to detect newly introduced secrets.
  - Integrated via **pre-commit hooks**, preventing accidental leakage before code reaches CI.

**Rationale:**
Secrets are easiest and cheapest to fix before code is committed. Baseline comparison reduces noise from historical findings.

---

### 3.2 Build-Time Security: Static Analysis (SAST)

- **Tool:** Semgrep
- **Scope:** Python source code
- **Output:** SARIF (`semgrep-report.sarif`)

Semgrep scans the codebase for insecure coding patterns (e.g., use of `eval` or `exec`). The rules are customizable and fast to run, making them suitable for CI pipelines.

**Trade-off:**
- Fast feedback
- Limited to patterns detectable statically

---

### 3.3 Build-Time Security: Container Image Scanning

- **Tool:** Trivy
- **Scope:** Built Docker image
- **Output:** JSON (`trivy-report.json`)

Trivy scans the application container for known vulnerabilities in:
- OS packages
- Python dependencies

The scan reports known CVEs based on public vulnerability databases.

**Important Note:**
A relatively high number of findings is expected for base images and dependencies. In real projects, findings are triaged by severity and exploitability.

---

### 3.4 Runtime Security: Dynamic Application Security Testing (DAST)

- **Tool:** OWASP ZAP (baseline scan)
- **Target:** Running application via Docker Compose
- **Output:** HTML report (`reports/zap-report.html`)

ZAP performs a dynamic scan against the live application, identifying runtime misconfigurations and common web vulnerabilities.

**Observed Results:**
- No high-risk findings
- Several warnings (e.g., missing headers, Spectre-related isolation warnings)

These findings are expected for a minimal demo application and demonstrate realistic runtime security feedback.

---

## 4. Automation and Orchestration

### Local Execution

All security steps can be executed locally using a single script:

```powershell
.\run_all_local.ps1
```

This script:
1. Builds and starts the application with Docker Compose
2. Runs Semgrep (SAST)
3. Runs detect-secrets (baseline comparison)
4. Runs Trivy (container scan)
5. Runs OWASP ZAP (runtime scan)
6. Aggregates results into the `reports/` directory
7. Tears down the running containers

---

### CI/CD Integration

- **Platform:** GitHub Actions
- **Workflows:**
  - Static analysis and secret scanning on push / pull request
  - Container image scanning
  - Automated artifact generation

The same tools used locally are executed in CI on Linux runners, ensuring consistency between developer machines and CI environments.

---

## 5. Reporting and Artifacts

Generated artifacts include:

- `semgrep-report.sarif` – Static analysis findings
- `trivy-report.json` – Container vulnerability scan
- `reports/zap-report.html` – Runtime security scan
- `reports/security-summary.md` – Human-readable summary
- `reports/summary.json` – Aggregated metrics

This separation allows both **technical analysis** and **high-level reporting**.

---

## 6. Build-Time vs Runtime Security Considerations

This project demonstrates key DevSecOps trade-offs:

- **Early scans (SAST, secrets)** are fast and prevent issues early
- **Image scanning** provides broad coverage but may produce noise
- **Runtime scans** detect real deployment issues but increase pipeline execution time

A balanced pipeline combines all of these, rather than relying on a single security stage.

---

## 7. How to Run the Project

### Prerequisites
- Python 3.x
- Docker Desktop
- PowerShell (Windows)

### Run Everything Locally

```powershell
.\run_all_local.ps1
```

### Run Application Only

```powershell
docker-compose up --build
```

---

## 8. Conclusion

This project demonstrates a complete, practical DevSecOps pipeline for a Python application. By integrating security at multiple stages—commit-time, build-time, and runtime—it shows how security can be treated as a continuous process rather than a final gate.

The design mirrors real-world DevSecOps practices while remaining simple enough for academic evaluation and demonstration.

