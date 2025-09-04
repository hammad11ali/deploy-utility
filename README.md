# Angular Build and Deploy Utility (ng-deploy)

A comprehensive command-line utility for automating Angular project builds and direct network deployment to remote servers via UNC paths. Features persistent configuration management, automatic backups, and robust error handling.

## 🚀 Features

- ✅ **Automated Angular builds** using `ng build`
- ✅ **Direct network deployment** via UNC paths (no manual file copying)
- ✅ **Intelligent path parsing** - supports `site\app` or `site app` formats
- ✅ **Automatic backup creation** with timestamp naming
- ✅ **Persistent configuration** - store defaults to avoid repetitive inputs
- ✅ **Network authentication** with automatic drive mapping
- ✅ **Dry-run mode** for testing deployments
- ✅ **Comprehensive error handling** with fallback instructions
- ✅ **Cross-platform support** (Windows, Linux, macOS)
- ✅ **Both Python script and standalone executable** available

## 📦 Installation

### Option 1: Windows Installer (Recommended)
1. Download the latest `ng-deploy-installer.msi` from [Releases](../../releases)
2. Double-click to run the installer
3. Follow the installation wizard
4. **Optional**: Choose "Add to System PATH" for global access
5. **Optional**: Choose "Desktop Shortcut" for quick access

### Option 2: Standalone Executable
1. Download the latest `ng-deploy.exe` from [Releases](../../releases)
2. Place it anywhere in your system
3. Optionally add to PATH for global access

### Option 3: Python Script
1. Ensure Python 3.6+ is installed
2. Clone or download this repository
3. No additional dependencies required (uses standard library only)

## 🏗️ Requirements

- **For deployment**: Angular CLI (`ng` command)
- **For Python version**: Python 3.6+
- **Network access** to target server
- **Windows**: For network drive mapping functionality

## ⚡ Quick Start

### 1. Set up default configuration (one-time)
```bash
# Using executable
ng-deploy config set remote_server 172.20.3.119
ng-deploy config set username myuser
ng-deploy config set remote_share e$

# Using Python script
python deploy.py config set remote_server 172.20.3.119
python deploy.py config set username myuser
python deploy.py config set remote_share e$
```

### 2. Deploy your Angular project
```bash
# Navigate to your Angular project directory
cd my-angular-project

# Deploy with site and app names
ng-deploy akbl mobile

# Or using Python script
python deploy.py akbl mobile
```

## 📖 Usage

### Basic Deployment Commands

```bash
# Deploy to akbl\mobile (auto-detects from path)
ng-deploy akbl\mobile
ng-deploy akbl mobile                     # Alternative syntax

# Deploy without backup
ng-deploy akbl mobile --no-backup

# Preview deployment (dry-run)
ng-deploy akbl mobile --dry-run

# Force deployment (skip confirmations)
ng-deploy akbl mobile --force

# Deploy with custom server
ng-deploy akbl mobile -s 192.168.1.100

# Skip Angular build (use existing)
ng-deploy akbl mobile --no-build

# Verbose output for debugging
ng-deploy akbl mobile -v
```

### Configuration Management

```bash
# Show current configuration
ng-deploy config show

# Set configuration values
ng-deploy config set remote_server 192.168.1.100
ng-deploy config set username admin
ng-deploy config set password mypassword
ng-deploy config set remote_share e$
ng-deploy config set target_dir_pattern "IISDeployments/{SITE_NAME}/{APP_NAME}"

# Reset to defaults
ng-deploy config reset
```

### Available Configuration Keys

| Key | Description | Example |
|-----|-------------|---------|
| `remote_server` | Target server IP/hostname | `172.20.3.119` |
| `remote_share` | Network share name | `e$` |
| `target_dir_pattern` | Deployment path template | `IISDeployments/{SITE_NAME}/{APP_NAME}` |
| `username` | Default authentication username | `myuser` |
| `password` | Default authentication password | `mypassword` |

## 🛠️ Command Line Options

### Deployment Options
```
positional arguments:
  deployment_path       SITE_NAME\APP_NAME or SITE_NAME/APP_NAME
  app_name             Application name (if provided separately)

optional arguments:
  -s, --server         Remote server IP/hostname
  -r, --share          Network share name
  -t, --target-dir     Target directory pattern
  -u, --username       Username for authentication
  -p, --password       Password for authentication
  --no-backup          Skip backup creation
  --no-build           Skip ng build (use existing build)
  --build-folder       Specify build folder (default: auto-detect)
  --dry-run            Preview deployment without executing
  --force              Skip confirmation prompts
  -v, --verbose        Enable verbose output
  -h, --help           Show help message
```

## 📁 Directory Structure

### Deployment Paths
```
Target:  \\server\share\IISDeployments\SITE_NAME\APP_NAME
Backup:  \\server\share\IISDeployments\SITE_NAME\APP_NAME_bkp_YYYYMMDD_HHMMSS.zip
Config:  ~/.deploy-utility/config.json
```

### Example for `deploy akbl mobile`:
```
Target:  \\172.20.3.119\e$\IISDeployments\akbl\mobile
Backup:  \\172.20.3.119\e$\IISDeployments\akbl\mobile_bkp_20250904_143022.zip
Build:   akbl_mobile_build_20250904_143022.zip (local)
```

## 🔧 Workflow

1. **Validation**: Checks for `angular.json` in current directory
2. **Build**: Runs `ng build` (unless `--no-build`)
3. **Package**: Creates timestamped zip from build output
4. **Connect**: Tests server connectivity and establishes network connection
5. **Authenticate**: Prompts for credentials if needed (or uses config defaults)
6. **Backup**: Creates backup of existing files (unless `--no-backup`)
7. **Deploy**: Clears target directory and extracts new files
8. **Cleanup**: Disconnects network drives and shows results

## 🛡️ Safety Features

- **Automatic backups** before deployment (with timestamps)
- **Confirmation prompts** before destructive operations
- **Dry-run mode** to preview actions
- **Graceful error handling** with manual fallback instructions
- **Network drive cleanup** on exit
- **Input validation** for configuration keys

## 🔍 Troubleshooting

### Common Issues

**"angular.json not found"**
- Ensure you're running from an Angular project root directory

**"ng build failed"**
- Check that Angular CLI is installed: `ng --version`
- Verify your project builds manually: `ng build`

**"Cannot reach server"**
- Test connectivity: `ping your-server-ip`
- Verify server IP in configuration

**"Failed to connect to network share"**
- Check network share permissions
- Verify username/password
- Try accessing share manually: `\\server\share`

**"Permission denied"**
- Run as Administrator on Windows
- Check file permissions on target directory

### Debug Mode
Use `-v` or `--verbose` for detailed output:
```bash
deploy akbl mobile -v
```

### Manual Deployment
If automatic deployment fails, the tool provides manual instructions:
1. Copy the generated zip file to the network share
2. Connect via RDP or network share
3. Extract files to target directory

## 🔄 Configuration File

Configuration is stored in JSON format at:
- **Windows**: `C:\Users\[Username]\.deploy-utility\config.json`
- **Linux/macOS**: `~/.deploy-utility/config.json`

Example configuration:
```json
{
  "remote_server": "172.20.3.119",
  "remote_share": "e$",
  "target_dir_pattern": "IISDeployments/{SITE_NAME}/{APP_NAME}",
  "username": "myuser",
  "password": "mypassword"
}
```

## 🏗️ Building from Source

### Requirements
- Python 3.6+
- PyInstaller (for creating executable)

### Create Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --name ng-deploy deploy.py

# Executable will be in dist/ng-deploy.exe
```

### Building Windows Installer (Optional)
```bash
# Install WiX Toolset from https://wixtoolset.org/releases/
# Then build the installer using either:

# Option 1: Batch script (Recommended)
build-installer.bat

# Option 2: PowerShell script
powershell -ExecutionPolicy Bypass -File build-installer.ps1

# Option 3: Manual build
candle.exe ng-deploy-installer.wxs
light.exe -ext WixUIExtension ng-deploy-installer.wixobj -out ng-deploy-installer.msi

# Result: ng-deploy-installer.msi (Windows Installer package)
```

## 📦 Release Management

The project uses GitHub Actions for automated releases. When you push a tag or trigger the workflow:

1. Version is automatically calculated from version files
2. Executable is built with PyInstaller  
3. MSI installer is created with WiX
4. GitHub release is published with both artifacts

### Skipping CI/CD

To skip the automated build and release process, include `--skip-ci` in:
- Commit messages: `git commit -m "Update docs --skip-ci"`
- Workflow dispatch version input: Use `--skip-ci` as the version value

### Version Management

Use the version management script to control releases:

```cmd
# Show current versions
powershell -ExecutionPolicy Bypass -File version-manager.ps1 show

# Set specific version
powershell -ExecutionPolicy Bypass -File version-manager.ps1 set 2.1.0

# Increment version
powershell -ExecutionPolicy Bypass -File version-manager.ps1 increment patch
powershell -ExecutionPolicy Bypass -File version-manager.ps1 increment minor
powershell -ExecutionPolicy Bypass -File version-manager.ps1 increment major

# Reset to 0.0.0
powershell -ExecutionPolicy Bypass -File version-manager.ps1 reset
```

### Local Building

Build the installer locally for testing:

```cmd
# Build with specific version
build-installer.bat 1.0.0

# Build with current version from version-new.txt
build-installer.ps1
```

**Download the latest release:** [Releases](../../releases)

## 📝 Examples

### Basic Usage
```bash
# Set up configuration once
deploy config set remote_server 172.20.3.119
deploy config set username admin

# Deploy different applications
deploy akbl mobile
deploy akbl web
deploy production api
deploy staging frontend
```

### Advanced Usage
```bash
# Deploy to custom server with verbose output
deploy akbl mobile -s 192.168.1.200 -v

# Deploy without backup and skip build
deploy akbl mobile --no-backup --no-build

# Test deployment without executing
deploy akbl mobile --dry-run

# Deploy with custom build folder
deploy akbl mobile --build-folder custom-dist
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## 🆘 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review existing issues in the repository
3. Create a new issue with detailed information

---

**Happy Deploying! 🚀**
