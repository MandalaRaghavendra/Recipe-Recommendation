param(
    [string]$Message = ""
)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Tastio 2.0 - Automated Git Commit & Push         " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($Message)) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Message = "auto-sync: $timestamp"
}

Write-Host "`n[1/3] Staging all project changes..." -ForegroundColor Yellow
git add -A

Write-Host "[2/3] Creating commit: '$Message'..." -ForegroundColor Yellow
$commitResult = git commit -m $Message 2>&1
Write-Host $commitResult

Write-Host "[3/3] Pushing to GitHub repository (origin main)..." -ForegroundColor Yellow
git push origin main

Write-Host "`n✨ Auto-push workflow finished!" -ForegroundColor Green
