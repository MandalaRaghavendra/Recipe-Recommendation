param(
    [string]$Message = ""
)

$ErrorActionPreference = "Continue"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Tastio 2.0 - Automated Git Commit & Push         " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Check if working tree has any changes
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "`nℹ️ No local changes detected to commit." -ForegroundColor Cyan
    Write-Host "Checking if local commits are ahead of remote..." -ForegroundColor Yellow
    $ahead = git status -sb | Select-String "ahead"
    if ($ahead) {
        Write-Host "Local commits are ahead. Pushing to GitHub (origin main)..." -ForegroundColor Yellow
        git push origin main
    } else {
        Write-Host "Everything is up to date with GitHub." -ForegroundColor Green
    }
    exit 0
}

if ([string]::IsNullOrWhiteSpace($Message)) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Message = "auto-sync: $timestamp"
}

Write-Host "`n[1/3] Staging project changes..." -ForegroundColor Yellow
git add -A

Write-Host "[2/3] Creating commit: '$Message'..." -ForegroundColor Yellow
$commitOutput = git commit -m $Message 2>&1
Write-Host $commitOutput

# Note: The post-commit hook automatically executes git push.
# Verify if still ahead; if so, attempt push:
$aheadCheck = git status -sb | Select-String "ahead"
if ($aheadCheck) {
    Write-Host "[3/3] Pushing to GitHub repository (origin main)..." -ForegroundColor Yellow
    git push origin main
} else {
    Write-Host "`n✅ Changes successfully pushed and synced with GitHub!" -ForegroundColor Green
}

Write-Host "`n✨ Auto-push workflow finished!" -ForegroundColor Green
