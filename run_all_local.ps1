<#
run_all_local.ps1
Local DevSecOps pipeline runner.

Prerequisites:
 - Docker Desktop running
 - Python venv active with requirements installed
 - Run from repo root
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Try-Run {
    param($Action, $ContinueOnError = $true)
    try {
        & $Action
        return $true
    } catch {
        Write-Warning $_.Exception.Message
        if (-not $ContinueOnError) { throw }
        return $false
    }
}

Write-Host "=== DevSecOps local pipeline runner ===`n"

# Activate venv if present
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & .\.venv\Scripts\Activate.ps1
}

# Ensure reports dir
if (-not (Test-Path reports)) {
    New-Item -ItemType Directory reports | Out-Null
}

# 1) Build Docker image
Write-Host "`n1) Building Docker image..."
Try-Run { docker build -t demo-app:latest . }

# 2) Start docker-compose
Write-Host "`n2) Starting docker-compose..."
Try-Run { docker-compose up -d }

# 3) Wait for app
Write-Host "`n3) Waiting for app on http://localhost:8080 ..."
$timeout = 60
while ($timeout-- -gt 0) {
    try {
        $r = Invoke-WebRequest http://localhost:8080 -TimeoutSec 3 -UseBasicParsing
        if ($r.StatusCode -eq 200) { break }
    } catch {}
    Start-Sleep 1
}

# 4) Semgrep (Docker)
Write-Host "`n4) Running Semgrep..."
Try-Run {
    docker run --rm `
        -v "${PWD}:/src" `
        returntocorp/semgrep `
        semgrep --config /src/.semgrep/rules /src `
        --sarif-output /src/semgrep-report.sarif
}

# 5) detect-secrets
Write-Host "`n5) Running detect-secrets..."
Try-Run {
    python run_detect_secrets_tracked_filtered.py detect-secrets-current.json
}

# 6) Clean detect-secrets
Write-Host "`n6) Cleaning detect-secrets output..."
Try-Run {
    python clean_detect_secrets.py `
        detect-secrets-current.json `
        detect-secrets-current-cleaned.json
}
Copy-Item -Force detect-secrets-current-cleaned.json .detect-secrets.baseline.cleaned

# 7) Compare baseline
Write-Host "`n7) Comparing detect-secrets baseline..."
Try-Run {
    python compare_and_summarize.py `
        .detect-secrets.baseline.cleaned `
        detect-secrets-current.json `
        --limit 50 --topfiles 30
}

# 8) Trivy
Write-Host "`n8) Running Trivy image scan..."
Try-Run {
    docker run --rm `
      -v /var/run/docker.sock:/var/run/docker.sock `
      -v "${PWD}:/workdir" `
      -w /workdir `
      aquasec/trivy:latest `
      image demo-app:latest `
      --format json `
      --output trivy-report.json
}

# 9) OWASP ZAP (BASELINE – CORRECT)
Write-Host "`n9) Running OWASP ZAP baseline scan..."
Try-Run {
    docker run --rm `
      -v "${PWD}:/zap/wrk:rw" `
      -t zaproxy/zap2docker-stable `
      zap-baseline.py `
      -t http://host.docker.internal:8080 `
      -r zap-report.html
}

# 10) Aggregate reports
Write-Host "`n10) Aggregating reports..."
Try-Run {
    python .github/scripts/report-aggregate.py `
      --trivy trivy-report.json `
      --zapprobe zap-report.html `
      --output reports/security-summary.md
}

# 11) Tear down
Write-Host "`n11) Tearing down docker-compose..."
Try-Run { docker-compose down }

# 12) Summary
Write-Host "`n=== Run complete. Artifacts: ==="
Get-ChildItem semgrep-report.sarif, trivy-report.json, zap-report.html, reports\* `
  -ErrorAction SilentlyContinue |
  ForEach-Object {
      Write-Host " - $($_.Name) ($($_.Length) bytes)"
  }
