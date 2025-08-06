#!/usr/bin/env pwsh
# VS Code Safe Closure - KISS Version
# Purpose: Detect git corruption and file resurrection before closing VS Code
# Usage: Run before manually closing VS Code

Write-Host "🛡️ VS Code KISS Protection Check..." -ForegroundColor Green
Write-Host "⏰ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

$issuesFound = 0

# 1. Git Corruption Check
Write-Host "`n📁 Checking git repository integrity..." -ForegroundColor Yellow

# Check git repository health and get status
try {
    $status = git status --porcelain 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "🚨 Git repository corrupted!" -ForegroundColor Red
        $issuesFound++
        $status = $null
    } else {
        Write-Host "✅ Git repository healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "🚨 Git command failed - possible corruption!" -ForegroundColor Red
    $issuesFound++
    $status = $null
}

# Check for uncommitted changes
if ($status) {
    Write-Host "📝 Uncommitted changes:" -ForegroundColor Yellow
    $status | ForEach-Object { Write-Host "   $_" -ForegroundColor Cyan }
    Write-Host "💡 Commit before closing!" -ForegroundColor Yellow
}

# 2. File Resurrection Detection
Write-Host "`n👻 Checking for file resurrection..." -ForegroundColor Yellow

# Check for git conflicts (resurrection indicator)
if ($status) {
    $gitConflicts = $status | Where-Object { $_ -match '^UU|^AA|^DD' }
    if ($gitConflicts) {
        Write-Host "🚨 Git conflicts detected - possible resurrection!" -ForegroundColor Red
        $gitConflicts | ForEach-Object { Write-Host "   $_" -ForegroundColor Cyan }
        $issuesFound++
    } else {
        Write-Host "✅ No git conflicts" -ForegroundColor Green
    }
} else {
    Write-Host "✅ No git conflicts (clean repository)" -ForegroundColor Green
}

# Check for recently modified files (resurrection pattern)
try {
    $recentFiles = Get-ChildItem -Recurse -File -Include "*.md", "*.ps1", "*.txt", "*.json" | Where-Object {
        $_.LastWriteTime -gt (Get-Date).AddMinutes(-5)
    }

    if ($recentFiles.Count -gt 5) {
        Write-Host "⚠️ Many files modified recently ($($recentFiles.Count)) - check for resurrection" -ForegroundColor Red
        $recentFiles | Select-Object -First 10 | ForEach-Object {
            Write-Host "   $($_.Name) - $($_.LastWriteTime.ToString('HH:mm:ss'))" -ForegroundColor Cyan
        }
        if ($recentFiles.Count -gt 10) {
            Write-Host "   ... and $($recentFiles.Count - 10) more files" -ForegroundColor Cyan
        }
        $issuesFound++
    } else {
        Write-Host "✅ Normal file modification pattern ($($recentFiles.Count) recent files)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Could not check file modification times" -ForegroundColor Yellow
}

# 3. Quick Assessment
Write-Host "`n🎯 ASSESSMENT:" -ForegroundColor Cyan

if ($issuesFound -eq 0) {
    Write-Host "✅ SAFE TO CLOSE VS CODE" -ForegroundColor Green
} else {
    Write-Host "⚠️ $issuesFound ISSUES FOUND - CHECK ABOVE" -ForegroundColor Red
}

Write-Host "`n📋 Git Status:" -ForegroundColor Gray
if ($status) {
    $status | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "   Working tree clean" -ForegroundColor Green
}
