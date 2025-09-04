# Version Management Script for ng-deploy
# This script helps manage version numbers for releases

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "show",
    
    [Parameter(Mandatory=$false)]
    [string]$Version,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("patch", "minor", "major")]
    [string]$Increment = "patch"
)

function Get-Versions {
    $newVersion = "1.0.0"
    $currentVersion = "0.0.0"
    
    if (Test-Path "version-new.txt") {
        $newVersion = (Get-Content "version-new.txt" -Raw).Trim()
    }
    
    if (Test-Path "version-current.txt") {
        $currentVersion = (Get-Content "version-current.txt" -Raw).Trim()
    }
    
    return @{
        New = $newVersion
        Current = $currentVersion
    }
}

function Set-Version {
    param([string]$VersionString, [string]$File)
    
    if ($VersionString -notmatch '^\d+\.\d+\.\d+$') {
        throw "Invalid version format. Use MAJOR.MINOR.PATCH (e.g., 1.2.3)"
    }
    
    $VersionString | Out-File -FilePath $File -Encoding UTF8 -NoNewline
    Write-Host "Updated $File to: $VersionString" -ForegroundColor Green
}

function Get-NextVersion {
    param([string]$CurrentVersion, [string]$IncrementType)
    
    $parts = $CurrentVersion -split '\.'
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]
    
    switch ($IncrementType) {
        "major" { $major++; $minor = 0; $patch = 0 }
        "minor" { $minor++; $patch = 0 }
        "patch" { $patch++ }
    }
    
    return "$major.$minor.$patch"
}

# Main logic
try {
    switch ($Action.ToLower()) {
        "show" {
            $versions = Get-Versions
            Write-Host "Current Versions:" -ForegroundColor Cyan
            Write-Host "  New Version:     $($versions.New)" -ForegroundColor Yellow
            Write-Host "  Current Version: $($versions.Current)" -ForegroundColor Yellow
            
            if ($versions.New -eq $versions.Current) {
                $nextPatch = Get-NextVersion $versions.Current "patch"
                $nextMinor = Get-NextVersion $versions.Current "minor"
                $nextMajor = Get-NextVersion $versions.Current "major"
                
                Write-Host ""
                Write-Host "Next release will be auto-incremented:" -ForegroundColor Cyan
                Write-Host "  Patch: $nextPatch" -ForegroundColor Gray
                Write-Host "  Minor: $nextMinor" -ForegroundColor Gray
                Write-Host "  Major: $nextMajor" -ForegroundColor Gray
            } else {
                Write-Host ""
                Write-Host "Next release will use new version: $($versions.New)" -ForegroundColor Green
            }
        }
        
        "set" {
            if (-not $Version) {
                throw "Version parameter is required for 'set' action"
            }
            Set-Version $Version "version-new.txt"
        }
        
        "increment" {
            $versions = Get-Versions
            $nextVersion = Get-NextVersion $versions.Current $Increment
            Set-Version $nextVersion "version-new.txt"
            Write-Host "Incremented version ($Increment): $nextVersion" -ForegroundColor Green
        }
        
        "reset" {
            Set-Version "1.0.0" "version-new.txt"
            Set-Version "0.0.0" "version-current.txt"
            Write-Host "Reset versions to defaults" -ForegroundColor Green
        }
        
        default {
            Write-Host "Invalid action: $Action" -ForegroundColor Red
            Write-Host ""
            Write-Host "Usage examples:" -ForegroundColor Yellow
            Write-Host "  .\version-manager.ps1 show" -ForegroundColor White
            Write-Host "  .\version-manager.ps1 set -Version 1.2.3" -ForegroundColor White
            Write-Host "  .\version-manager.ps1 increment -Increment patch" -ForegroundColor White
            Write-Host "  .\version-manager.ps1 increment -Increment minor" -ForegroundColor White
            Write-Host "  .\version-manager.ps1 increment -Increment major" -ForegroundColor White
            Write-Host "  .\version-manager.ps1 reset" -ForegroundColor White
            Write-Host ""
            Write-Host "Note: To skip CI/CD pipeline, use '--skip-ci' in commit messages or workflow inputs" -ForegroundColor Cyan
            exit 1
        }
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
