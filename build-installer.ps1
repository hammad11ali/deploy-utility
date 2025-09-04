# Angular Deploy Utility (ng-deploy) - WiX Installer Build Script
param(
    [string]$Version = "1.0.0.0"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Angular Deploy Utility (ng-deploy)" -ForegroundColor Yellow
Write-Host "WiX Installer Build Script" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Version: $Version" -ForegroundColor Yellow
Write-Host ""

# Check if WiX is available
try {
    $null = Get-Command "candle.exe" -ErrorAction Stop
    Write-Host "WiX Toolset found. Building installer..." -ForegroundColor Green
} catch {
    Write-Host "ERROR: WiX Toolset not found!" -ForegroundColor Red
    Write-Host "Please install from: https://wixtoolset.org/releases/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    return
}

Write-Host ""

# Clean previous builds
@("ng-deploy-installer.wixobj", "ng-deploy-installer.msi") | ForEach-Object {
    if (Test-Path $_) {
        Remove-Item $_ -Force
        Write-Host "Cleaned: $_" -ForegroundColor Gray
    }
}

try {
    # Step 1: Compile
    Write-Host "Step 1: Compiling WiX source..." -ForegroundColor Yellow
    & candle.exe ng-deploy-installer.wxs -dProductVersion=$Version
    if ($LASTEXITCODE -ne 0) { throw "Compilation failed" }
    Write-Host "✓ Compilation successful" -ForegroundColor Green

    # Step 2: Link
    Write-Host "Step 2: Linking to create MSI..." -ForegroundColor Yellow
    & light.exe -ext WixUIExtension ng-deploy-installer.wixobj -out ng-deploy-installer.msi
    if ($LASTEXITCODE -ne 0) { throw "Linking failed" }
    Write-Host "✓ Linking successful" -ForegroundColor Green

    # Cleanup
    if (Test-Path "ng-deploy-installer.wixobj") {
        Remove-Item "ng-deploy-installer.wixobj" -Force
    }

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "SUCCESS! Installer created successfully!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path "ng-deploy-installer.msi") {
        $fileInfo = Get-Item "ng-deploy-installer.msi"
        Write-Host "Installer: ng-deploy-installer.msi" -ForegroundColor Yellow
        $sizeInMB = [math]::Round($fileInfo.Length / 1MB, 2)
        Write-Host "Size: $sizeInMB MB" -ForegroundColor Gray
        Write-Host "Created: $($fileInfo.CreationTime)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Ready for distribution!" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Build failed - $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Read-Host "Press Enter to exit"
