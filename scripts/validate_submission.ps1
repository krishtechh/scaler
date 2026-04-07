# validate_submission.ps1 — Pre-submission validation for OpenEnv LLM Safeguard Environment
# Run from repository root: .\scripts\validate_submission.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent

Write-Host "`n=== Step 1: Run pytest ===" -ForegroundColor Cyan
python -m pytest $root\tests -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
Write-Host "Tests PASSED" -ForegroundColor Green

Write-Host "`n=== Step 2: Start server and run smoke tests ===" -ForegroundColor Cyan
$server = Start-Process -FilePath "python" -ArgumentList "-m uvicorn api.main:app --host 127.0.0.1 --port 8080" `
    -WorkingDirectory $root -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 4

try {
    $reset = Invoke-RestMethod -Uri "http://localhost:8080/reset" -Method POST `
        -ContentType "application/json" -Body '{"task":"easy","seed":42}'
    Write-Host "POST /reset OK  prompt='$($reset.prompt.Substring(0,[Math]::Min(40,$reset.prompt.Length)))...'" -ForegroundColor Green

    $step = Invoke-RestMethod -Uri "http://localhost:8080/step" -Method POST `
        -ContentType "application/json" -Body '{"decision":"block"}'
    Write-Host "POST /step  OK  reward=$($step.reward.reward)  done=$($step.done)" -ForegroundColor Green

    $state = Invoke-RestMethod -Uri "http://localhost:8080/state" -Method GET
    Write-Host "GET  /state OK  index=$($state.index)  task=$($state.task_id)" -ForegroundColor Green

    $tasks = Invoke-RestMethod -Uri "http://localhost:8080/tasks" -Method GET
    Write-Host "GET  /tasks OK  count=$($tasks.Count)" -ForegroundColor Green

    $grader = Invoke-RestMethod -Uri "http://localhost:8080/grader" -Method GET
    Write-Host "GET  /grader OK score=$($grader.score)" -ForegroundColor Green

    Write-Host "`n=== All smoke tests PASSED ===" -ForegroundColor Green
} finally {
    Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Green
