#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick Refresh - All Alex Method DJ Spotify Playlists

.DESCRIPTION
    Simple, fast script to refresh all Spotify playlists with minimal output.
    Perfect for scheduled tasks or quick updates.

.EXAMPLE
    .\quick-refresh.ps1
#>

param()

$ErrorActionPreference = "Stop"

try {
    # Get script directory and config files
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $ConfigDir = Join-Path $ScriptDir "playlist-configs"
    $PythonScript = Join-Path $ScriptDir "spotify_playlist_creator.py"
    
    # Get all playlist configs (exclude templates and examples)
    $ConfigFiles = Get-ChildItem -Path $ConfigDir -Filter "*.md" -File | 
        Where-Object { $_.Name -notlike "TEMPLATE-*" -and $_.Name -ne "README.md" -and $_.FullName -notlike "*\examples\*" } |
        Sort-Object Name
    
    Write-Host "🎵 Alex Method DJ - Quick Refresh (Spotify)" -ForegroundColor Cyan
    Write-Host "📁 Found $($ConfigFiles.Count) playlists to refresh" -ForegroundColor Yellow
    
    $SuccessCount = 0
    $FailureCount = 0
    $StartTime = Get-Date
    
    foreach ($configFile in $ConfigFiles) {
        $ConfigName = [System.IO.Path]::GetFileNameWithoutExtension($configFile.Name)
        Write-Host "🔄 $ConfigName..." -NoNewline
        
        try {
            # Run playlist creator with force-ascii for consistent output
            $Process = Start-Process -FilePath "python" -ArgumentList @($PythonScript, $configFile.FullName, "--force", "--force-ascii") -Wait -PassThru -WindowStyle Hidden
            
            if ($Process.ExitCode -eq 0) {
                Write-Host " ✅" -ForegroundColor Green
                $SuccessCount++
            } else {
                Write-Host " ❌" -ForegroundColor Red
                $FailureCount++
            }
        }
        catch {
            Write-Host " ❌ (Exception)" -ForegroundColor Red
            $FailureCount++
        }
        
        # Brief pause between requests
        Start-Sleep -Seconds 1
    }
    
    # Summary
    $Duration = (Get-Date) - $StartTime
    Write-Host ""
    Write-Host "🎉 Completed in $($Duration.ToString('mm\:ss'))" -ForegroundColor Cyan
    Write-Host "✅ Success: $SuccessCount | ❌ Failed: $FailureCount" -ForegroundColor $(if ($FailureCount -eq 0) { "Green" } else { "Yellow" })
    
    if ($FailureCount -gt 0) {
        Write-Host "💡 Check individual playlist configs for issues" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "❌ Quick refresh failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Check your Python environment and API credentials" -ForegroundColor Yellow
    exit 1
}
