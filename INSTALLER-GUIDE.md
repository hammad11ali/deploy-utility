# WiX Installer Build Guide

This guide explains how to build the Windows Installer (.msi) for ng-deploy.

## Prerequisites

### Install WiX Toolset
1. Download WiX Toolset v3.11+ from: https://wixtoolset.org/releases/
2. Install `wix311.exe` (or latest version)
3. Ensure WiX tools are in your PATH (usually automatic)

## Building the Installer

### Option 1: Batch Script (Recommended)
```cmd
build-installer.bat
```
- ✅ Clean output formatting
- ✅ Reliable error handling
- ✅ Works on all Windows versions

### Option 2: PowerShell Script
```powershell
powershell -ExecutionPolicy Bypass -File build-installer.ps1
```
- ✅ Colored output
- ✅ Better automation support
- ⚠️ Minor Unicode encoding issues

### Option 3: Manual Build
```cmd
candle.exe ng-deploy-installer.wxs
light.exe -ext WixUIExtension ng-deploy-installer.wixobj -out ng-deploy-installer.msi
```

## Build Output

**Generated File**: `ng-deploy-installer.msi` (~12.7 MB)

## Installer Features

### Core Installation (Required)
- ng-deploy.exe executable
- README.md documentation  
- Start Menu shortcuts

### Optional Features (User Choice)
- **Add to System PATH**: Run `ng-deploy` from any directory
- **Desktop Shortcut**: Quick access icon

## Installation Process

1. Double-click `ng-deploy-installer.msi`
2. Accept license agreement
3. Choose features to install
4. Select installation directory
5. Complete installation

## Post-Installation

### With PATH added:
```cmd
ng-deploy config show
ng-deploy akbl mobile
```

### Without PATH:
```cmd
cd "C:\Program Files\ng-deploy"
ng-deploy config show
```

## Troubleshooting

### "WiX Toolset not found"
- Install WiX from https://wixtoolset.org/releases/
- Add WiX bin directory to PATH if needed

### "Permission denied"
- Run as Administrator
- Or install to user directory instead

### Build succeeds but no MSI
- Check for error messages in build output
- Ensure all source files are present

## File Structure

```
deploy-utility/
├── ng-deploy-installer.wxs     # WiX source definition
├── build-installer.bat         # Windows batch build script  
├── build-installer.ps1         # PowerShell build script
├── license.rtf                 # License for installer
├── dist/ng-deploy.exe          # Executable to package
├── README.md                   # Documentation to include
└── ng-deploy-installer.msi     # Generated installer (after build)
```

## Customization

Edit `ng-deploy-installer.wxs` to modify:
- Installation directory
- Product information
- Features and components
- Registry entries
- Shortcuts and icons

The installer provides professional Windows integration with proper Add/Remove Programs support, upgrade handling, and clean uninstallation.
