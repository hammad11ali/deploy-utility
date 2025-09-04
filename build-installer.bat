@echo off
REM Angular Deploy Utility (ng-deploy) - WiX Installer Build Script
REM Usage: build-installer.bat [version]
REM Example: build-installer.bat 1.2.3.0

REM Set default version if not provided
set VERSION=%1
if "%VERSION%"=="" set VERSION=1.0.0.0

echo ==========================================
echo Angular Deploy Utility (ng-deploy)
echo WiX Installer Build Script
echo ==========================================
echo Version: %VERSION%
echo.

REM Check if WiX is installed
where candle.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WiX Toolset not found!
    echo.
    echo Please install WiX Toolset v3.11 or later from:
    echo https://wixtoolset.org/releases/
    echo.
    echo After installation, make sure the WiX bin directory is in your PATH
    echo Example: C:\Program Files ^(x86^)\WiX Toolset v3.11\bin
    echo.
    pause
    exit /b 1
)

echo WiX Toolset found. Building installer...
echo.

REM Clean previous builds
if exist ng-deploy-installer.wixobj del ng-deploy-installer.wixobj
if exist ng-deploy-installer.msi del ng-deploy-installer.msi

REM Compile WiX source
echo Step 1: Compiling WiX source...
candle.exe ng-deploy-installer.wxs -dProductVersion=%VERSION%
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to compile WiX source
    pause
    exit /b 1
)

REM Link to create MSI
echo Step 2: Linking to create MSI...
light.exe -ext WixUIExtension ng-deploy-installer.wixobj -out ng-deploy-installer.msi
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create MSI
    pause
    exit /b 1
)

REM Clean intermediate files
del ng-deploy-installer.wixobj

echo.
echo ==========================================
echo SUCCESS! Installer created successfully!
echo ==========================================
echo.
echo Installer: ng-deploy-installer.msi
echo Size: 
for %%I in (ng-deploy-installer.msi) do echo %%~zI bytes
echo.
echo To test the installer:
echo 1. Right-click ng-deploy-installer.msi
echo 2. Select "Install"
echo 3. Follow the installation wizard
echo 4. Choose whether to add to PATH
echo.
echo To uninstall:
echo 1. Go to Control Panel - Programs and Features
echo 2. Find "Angular Deploy Utility (ng-deploy)"
echo 3. Click "Uninstall"
echo.
pause
