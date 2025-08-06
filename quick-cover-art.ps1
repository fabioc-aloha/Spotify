#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick Cover Art Generation - All Alex Method DJ Playlists

.DESCRIPTION
    Simple, fast script to generate cover art for all playlists with minimal output.
    Uses the existing generate_cover_art.py with batch processing capabilities.

.PARAMETER Force
    Force regeneration of cover art even if files exist

.PARAMETER OnlyMissing
    Only generate cover art for playlists that don't have existing cover art files

.EXAMPLE
    .\quick-cover-art.ps1
    .\quick-cover-art.ps1 -Force
    .\quick-cover-art.ps1 -OnlyMissing
#>

param(
    [Parameter()]
    [switch]$Force,
    
    [Parameter()]
    [switch]$OnlyMissing
)

$ErrorActionPreference = "Stop"

# Set console encoding to UTF-8 for better emoji support
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
} catch {
    # Ignore encoding errors
}

try {
    # Get script directory and config files
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $ConfigDir = Join-Path $ScriptDir "playlist-configs"
    $CoverArtScript = Join-Path $ScriptDir "generate_cover_art.py"
    $CoverArtDir = Join-Path $ScriptDir "cover-art"
    
    # Check if cover art script exists
    if (-not (Test-Path $CoverArtScript)) {
        Write-Host "❌ Error: generate_cover_art.py not found" -ForegroundColor Red
        exit 1
    }
    
    # Check if OpenAI API key is available
    if (-not $env:OPENAI_API_KEY -and -not (Test-Path ".env")) {
        Write-Host "❌ Error: OPENAI_API_KEY not found in environment or .env file" -ForegroundColor Red
        Write-Host "Create a .env file with your OpenAI API key: OPENAI_API_KEY=your-api-key" -ForegroundColor Yellow
        exit 1
    }
    
    # Get all playlist configs (exclude templates and examples)
    $ConfigFiles = Get-ChildItem -Path $ConfigDir -Filter "*.md" -File | 
        Where-Object { $_.Name -notlike "TEMPLATE-*" -and $_.Name -ne "README.md" -and $_.FullName -notlike "*\examples\*" } |
        Sort-Object Name
    
    if ($ConfigFiles.Count -eq 0) {
        Write-Host "❌ No playlist configuration files found in $ConfigDir" -ForegroundColor Red
        exit 1
    }
    
    # Filter for missing cover art if OnlyMissing is specified
    if ($OnlyMissing) {
        $FilteredFiles = @()
        foreach ($configFile in $ConfigFiles) {
            $ConfigName = [System.IO.Path]::GetFileNameWithoutExtension($configFile.Name)
            $CoverArtJpg = Join-Path $CoverArtDir "$ConfigName.jpg"
            $CoverArtPng = Join-Path $CoverArtDir "$ConfigName.png"
            
            # Check if neither JPG nor PNG exists
            if (-not (Test-Path $CoverArtJpg) -and -not (Test-Path $CoverArtPng)) {
                $FilteredFiles += $configFile
            }
        }
        $ConfigFiles = $FilteredFiles
        
        if ($ConfigFiles.Count -eq 0) {
            Write-Host "✅ All playlists already have cover art!" -ForegroundColor Green
            exit 0
        }
    }
    
    $ModeText = if ($Force) { "Force Regeneration" } elseif ($OnlyMissing) { "Missing Only" } else { "Standard" }
    Write-Host "🎨 Alex Method DJ - Quick Cover Art Generation ($ModeText)" -ForegroundColor Cyan
    Write-Host "📁 Found $($ConfigFiles.Count) playlists to process" -ForegroundColor Yellow
    
    if ($OnlyMissing) {
        Write-Host "🔍 Processing only playlists without existing cover art" -ForegroundColor Blue
    }
    
    if ($Force) {
        Write-Host "⚡ Force mode: Will regenerate existing cover art" -ForegroundColor Magenta
    }
    
    $SuccessCount = 0
    $FailureCount = 0
    $SkippedCount = 0
    $StartTime = Get-Date
    
    foreach ($configFile in $ConfigFiles) {
        $ConfigName = [System.IO.Path]::GetFileNameWithoutExtension($configFile.Name)
        Write-Host "🎨 $ConfigName..." -NoNewline
        
        try {
            # Build arguments for cover art generator
            $Arguments = @($CoverArtScript, $configFile.FullName)
            if ($Force) {
                $Arguments += "--force"
            }
            
            # Check if cover art already exists (unless Force is specified)
            $CoverArtJpg = Join-Path $CoverArtDir "$ConfigName.jpg"
            $CoverArtPng = Join-Path $CoverArtDir "$ConfigName.png"
            
            if (-not $Force -and ((Test-Path $CoverArtJpg) -or (Test-Path $CoverArtPng))) {
                Write-Host " ⏭️ exists" -ForegroundColor Yellow
                $SkippedCount++
                continue
            }
            
            # Run cover art generator with error capture and UTF-8 encoding
            $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
            $ProcessInfo.FileName = "python"
            $ProcessInfo.Arguments = ($Arguments -join " ")
            $ProcessInfo.UseShellExecute = $false
            $ProcessInfo.RedirectStandardOutput = $true
            $ProcessInfo.RedirectStandardError = $true
            $ProcessInfo.WindowStyle = "Hidden"
            # Set UTF-8 encoding for Python process
            $ProcessInfo.Environment["PYTHONIOENCODING"] = "utf-8"
            
            $Process = New-Object System.Diagnostics.Process
            $Process.StartInfo = $ProcessInfo
            $Process.Start() | Out-Null
            $StdOut = $Process.StandardOutput.ReadToEnd()
            $StdErr = $Process.StandardError.ReadToEnd()
            $Process.WaitForExit()
            
            # Check if cover art was actually created (verify success)
            $CoverArtCreated = $false
            if ($Process.ExitCode -eq 0) {
                # Check if either JPG or PNG was created
                if ((Test-Path $CoverArtJpg) -or (Test-Path $CoverArtPng)) {
                    $CoverArtCreated = $true
                }
            }
            
            if ($CoverArtCreated) {
                Write-Host " ✅" -ForegroundColor Green
                $SuccessCount++
            } else {
                Write-Host " ❌" -ForegroundColor Red
                # Show error details for debugging
                if ($StdErr) {
                    Write-Host "   Error: $($StdErr.Trim())" -ForegroundColor DarkRed
                } elseif ($StdOut -and $StdOut.Contains("Error")) {
                    Write-Host "   Error: $($StdOut.Trim())" -ForegroundColor DarkRed
                } else {
                    Write-Host "   Error: Cover art file not created (Exit code: $($Process.ExitCode))" -ForegroundColor DarkRed
                }
                $FailureCount++
            }
        }
        catch {
            Write-Host " ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
            $FailureCount++
        }
        
        # Small delay to avoid API rate limits
        Start-Sleep -Milliseconds 500
    }
    
    $EndTime = Get-Date
    $Duration = $EndTime - $StartTime
    
    Write-Host "`n🏁 Cover Art Generation Complete!" -ForegroundColor Cyan
    Write-Host "⏱️  Duration: $($Duration.ToString('mm\:ss'))" -ForegroundColor White
    Write-Host "✅ Success: $SuccessCount" -ForegroundColor Green
    if ($SkippedCount -gt 0) {
        Write-Host "⏭️  Skipped: $SkippedCount (already exist)" -ForegroundColor Yellow
    }
    if ($FailureCount -gt 0) {
        Write-Host "❌ Failed: $FailureCount" -ForegroundColor Red
    }
    
    if ($FailureCount -gt 0) {
        Write-Host "`n💡 Tip: For playlists that consistently fail, try generate_problem_covers.py" -ForegroundColor Blue
    }
}
catch {
    Write-Host "`n❌ Script Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
