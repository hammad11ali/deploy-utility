#!/usr/bin/env python3
"""
Angular Build and Deploy Utility - Python Version
Automated Angular build and deployment utility that builds your
project and deploys it directly to remote servers via network shares.
"""

import os
import sys
import subprocess
import zipfile
import shutil
import argparse
import json
from datetime import datetime
from pathlib import Path
import getpass
from dataclasses import dataclass, asdict
from typing import Optional, Tuple, Dict, Any


@dataclass
class DeploymentConfig:
    """Configuration for deployment"""
    remote_server: str = "172.20.3.119"
    remote_share: str = "e$"
    target_dir_pattern: str = "IISDeployments/{SITE_NAME}/{APP_NAME}"
    username: str = ""
    password: str = ""
    

class ConfigManager:
    """Handle configuration storage and retrieval"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".deploy-utility"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> DeploymentConfig:
        """Load configuration from file, return defaults if file doesn't exist"""
        if not self.config_file.exists():
            return DeploymentConfig()
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Create config with loaded data, falling back to defaults for missing keys
            return DeploymentConfig(
                remote_server=config_data.get('remote_server', "172.20.3.119"),
                remote_share=config_data.get('remote_share', "e$"),
                target_dir_pattern=config_data.get('target_dir_pattern', "IISDeployments/{SITE_NAME}/{APP_NAME}"),
                username=config_data.get('username', ""),
                password=config_data.get('password', "")
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Warning: Could not load config file ({e}). Using defaults.")
            return DeploymentConfig()
    
    def save_config(self, config: DeploymentConfig) -> None:
        """Save configuration to file"""
        try:
            config_dict = asdict(config)
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            print(f"Configuration saved to: {self.config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def show_config(self) -> None:
        """Display current configuration"""
        config = self.load_config()
        print("\nCurrent Configuration:")
        print("=" * 40)
        print(f"Remote Server:    {config.remote_server}")
        print(f"Remote Share:     {config.remote_share}")
        print(f"Target Pattern:   {config.target_dir_pattern}")
        print(f"Username:         {config.username or '(not set)'}")
        print(f"Password:         {'*' * len(config.password) if config.password else '(not set)'}")
        print(f"Config Location:  {self.config_file}")
        print("=" * 40)
    
    def set_config_value(self, key: str, value: str) -> None:
        """Set a specific configuration value"""
        config = self.load_config()
        
        # Validate key
        valid_keys = ['remote_server', 'remote_share', 'target_dir_pattern', 'username', 'password']
        if key not in valid_keys:
            raise ValueError(f"Invalid config key '{key}'. Valid keys are: {', '.join(valid_keys)}")
        
        # Update the configuration
        setattr(config, key, value)
        self.save_config(config)
        print(f"Updated {key} = {value if key != 'password' else '*' * len(value)}")
    
    def reset_config(self) -> None:
        """Reset configuration to defaults"""
        if self.config_file.exists():
            self.config_file.unlink()
            print("Configuration reset to defaults.")
        else:
            print("No configuration file found. Already at defaults.")


class ArgumentParser:
    """Handle command line argument parsing"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _get_script_name(self) -> str:
        """Get the appropriate script name based on how it's being executed"""
        import sys
        import os
        
        # Get the script path from sys.argv[0]
        script_path = sys.argv[0]
        
        # If running as an executable (frozen with PyInstaller, cx_Freeze, etc.)
        if getattr(sys, 'frozen', False):
            # Running as executable
            return os.path.basename(script_path)
        else:
            # Running as Python script
            script_name = os.path.basename(script_path)
            if script_name.endswith('.py'):
                return f"python {script_name}"
            else:
                # Fallback - shouldn't normally happen
                return f"python {script_name}"
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        script_name = self._get_script_name()
        
        parser = argparse.ArgumentParser(
            prog=script_name,
            description='Angular Build and Deploy Utility',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_help_text()
        )
        
        # Create subparsers for different commands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Deploy command (default)
        deploy_parser = subparsers.add_parser('deploy', help='Deploy application (default)')
        
        # Positional arguments for deploy
        deploy_parser.add_argument('deployment_path', nargs='?', 
                          help='Deployment path as SITE_NAME\\APP_NAME or SITE_NAME/APP_NAME')
        deploy_parser.add_argument('app_name', nargs='?',
                          help='Application name (if site_name provided separately)')
        
        # Optional arguments for deploy
        deploy_parser.add_argument('-s', '--server',
                          help='Remote server IP/hostname (default from config)')
        deploy_parser.add_argument('-r', '--share',
                          help='Network share name (default from config)')
        deploy_parser.add_argument('-t', '--target-dir',
                          help='Target directory pattern (default from config)')
        deploy_parser.add_argument('-u', '--username',
                          help='Username for network authentication (default from config)')
        deploy_parser.add_argument('-p', '--password',
                          help='Password for network authentication (default from config)')
        deploy_parser.add_argument('--no-backup', action='store_true',
                          help='Skip backup creation')
        deploy_parser.add_argument('--no-build', action='store_true',
                          help='Skip ng build (use existing build)')
        deploy_parser.add_argument('--build-folder',
                          help='Specify build folder (default: auto-detect www/dist)')
        deploy_parser.add_argument('--dry-run', action='store_true',
                          help='Show what would be deployed without actual deployment')
        deploy_parser.add_argument('--force', action='store_true',
                          help='Skip confirmation prompts')
        deploy_parser.add_argument('-v', '--verbose', action='store_true',
                          help='Verbose output')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Manage configuration')
        config_subparsers = config_parser.add_subparsers(dest='config_action', help='Configuration actions')
        
        # Config show
        config_subparsers.add_parser('show', help='Show current configuration')
        
        # Config set
        set_parser = config_subparsers.add_parser('set', help='Set configuration value')
        set_parser.add_argument('key', help='Configuration key to set')
        set_parser.add_argument('value', help='Configuration value to set')
        
        # Config reset
        config_subparsers.add_parser('reset', help='Reset configuration to defaults')
        
        # For backward compatibility, if no subcommand is provided, treat as deploy
        # Add the same arguments to the main parser
        parser.add_argument('deployment_path', nargs='?', 
                          help='Deployment path as SITE_NAME\\APP_NAME or SITE_NAME/APP_NAME')
        parser.add_argument('app_name', nargs='?',
                          help='Application name (if site_name provided separately)')
        parser.add_argument('-s', '--server',
                          help='Remote server IP/hostname (default from config)')
        parser.add_argument('-r', '--share',
                          help='Network share name (default from config)')
        parser.add_argument('-t', '--target-dir',
                          help='Target directory pattern (default from config)')
        parser.add_argument('-u', '--username',
                          help='Username for network authentication (default from config)')
        parser.add_argument('-p', '--password',
                          help='Password for network authentication (default from config)')
        parser.add_argument('--no-backup', action='store_true',
                          help='Skip backup creation')
        parser.add_argument('--no-build', action='store_true',
                          help='Skip ng build (use existing build)')
        parser.add_argument('--build-folder',
                          help='Specify build folder (default: auto-detect www/dist)')
        parser.add_argument('--dry-run', action='store_true',
                          help='Show what would be deployed without actual deployment')
        parser.add_argument('--force', action='store_true',
                          help='Skip confirmation prompts')
        parser.add_argument('-v', '--verbose', action='store_true',
                          help='Verbose output')
        
        return parser
    
    def _get_help_text(self) -> str:
        """Get detailed help text"""
        # Determine the command name based on how the script is being run
        script_name = self._get_script_name()
        
        return f"""
Deployment Examples:
  {script_name} akbl\\mobile                    # Deploy to akbl\\mobile
  {script_name} akbl mobile                     # Deploy to akbl\\mobile  
  {script_name} akbl\\mobile --no-backup        # Deploy without backup
  {script_name} production webapp               # Deploy to production\\webapp
  {script_name} akbl\\mobile --dry-run          # Preview deployment
  {script_name} akbl\\mobile --force            # Skip confirmations

Configuration Examples:
  {script_name} config show                     # Show current configuration
  {script_name} config set remote_server 192.168.1.100  # Set server IP
  {script_name} config set username myuser      # Set default username
  {script_name} config reset                    # Reset to defaults

Path Structure:
  Target: \\\\server\\share\\IISDeployments\\SITE_NAME\\APP_NAME
  Backup: \\\\server\\share\\IISDeployments\\SITE_NAME\\APP_NAME_bkp_YYYYMMDD_HHMMSS.zip

Configuration Keys:
  remote_server      - Remote server IP/hostname
  remote_share       - Network share name (e.g., 'e$')
  target_dir_pattern - Target directory pattern with placeholders
  username           - Default username for authentication
  password           - Default password for authentication
"""
    
    def parse(self) -> argparse.Namespace:
        """Parse command line arguments"""
        return self.parser.parse_args()
    
    def parse_site_and_app(self, args: argparse.Namespace) -> Tuple[str, str]:
        """Parse site name and app name from arguments"""
        if args.deployment_path:
            # Check if it contains path separators
            if '\\' in args.deployment_path or '/' in args.deployment_path:
                # Split on either separator
                parts = args.deployment_path.replace('/', '\\').split('\\')
                if len(parts) == 2:
                    return parts[0], parts[1]
                else:
                    raise ValueError(f"Invalid deployment path format: {args.deployment_path}")
            else:
                # Single argument - treat as site name, app name should be second arg
                if args.app_name:
                    return args.deployment_path, args.app_name
                else:
                    # Use current directory as app name
                    app_name = os.path.basename(os.getcwd())
                    return args.deployment_path, app_name
        else:
            # No deployment path - auto-detect from current directory
            current_dir = os.path.basename(os.getcwd())
            # Try to split if it contains separators
            if '\\' in current_dir or '/' in current_dir:
                parts = current_dir.replace('/', '\\').split('\\')
                if len(parts) >= 2:
                    return parts[-2], parts[-1]
            
            # Prompt for site name
            site_name = input("Enter site name: ").strip()
            if not site_name:
                raise ValueError("Site name is required")
            return site_name, current_dir


class BuildManager:
    """Handle Angular build operations"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def validate_angular_project(self) -> None:
        """Validate that we're in an Angular project"""
        if not os.path.exists("angular.json"):
            raise FileNotFoundError("angular.json not found. Please run this script from an Angular project root.")
    
    def run_build(self) -> None:
        """Run Angular build"""
        if self.verbose:
            print("Building Angular project...")
        
        try:
            result = subprocess.run(
                ["ng", "build"], 
                check=True, 
                capture_output=True, 
                text=True
            )
            if self.verbose:
                print("Build completed successfully!")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ng build failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Angular CLI (ng) not found. Please install Angular CLI.")
    
    def find_build_folder(self, custom_folder: Optional[str] = None) -> str:
        """Find the build output folder"""
        if custom_folder:
            if os.path.exists(custom_folder):
                return custom_folder
            else:
                raise FileNotFoundError(f"Specified build folder '{custom_folder}' not found")
        
        # Auto-detect
        for folder in ["www", "dist"]:
            if os.path.exists(folder):
                return folder
        
        raise FileNotFoundError("Neither 'www' nor 'dist' folder found after build!")
    
    def create_zip_file(self, build_folder: str, site_name: str, app_name: str) -> str:
        """Create zip file from build folder"""
        if self.verbose:
            print(f"Creating zip file from {build_folder} folder...")
        
        # Create timestamp
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        zip_name = f"{site_name}_{app_name}_build_{timestamp}.zip"
        
        try:
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                build_path = Path(build_folder)
                for file_path in build_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(build_path)
                        zipf.write(file_path, arcname)
            
            if self.verbose:
                print(f"Successfully created: {zip_name}")
            return zip_name
            
        except Exception as e:
            raise RuntimeError(f"Failed to create zip file: {e}")


class NetworkManager:
    """Handle network operations"""
    
    def __init__(self, config: DeploymentConfig, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.connected_drive: Optional[str] = None
        self.remote_path = f"\\\\{config.remote_server}\\{config.remote_share}"
    
    def test_server_connection(self) -> None:
        """Test connection to remote server"""
        if self.verbose:
            print(f"Testing connection to: {self.config.remote_server}")
        
        try:
            result = subprocess.run(
                ["ping", "-n", "1", self.config.remote_server], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode != 0:
                raise ConnectionError(f"Cannot reach server {self.config.remote_server}")
        except subprocess.TimeoutExpired:
            raise ConnectionError(f"Timeout reaching server {self.config.remote_server}")
    
    def connect_to_share(self) -> str:
        """Connect to network share and return the accessible path"""
        if self.verbose:
            print("Testing network share access...")
        
        # Test if we can access the share without authentication
        try:
            os.listdir(self.remote_path)
            if self.verbose:
                print("Network share accessible without authentication.")
            return self.remote_path
        except (OSError, PermissionError):
            if self.verbose:
                print("Network share requires authentication...")
            return self._authenticate_and_map()
    
    def _authenticate_and_map(self) -> str:
        """Authenticate and map network drive"""
        username = self.config.username or input(f"Enter username for {self.config.remote_server}: ")
        password = self.config.password or getpass.getpass("Enter password: ")
        
        # Find available drive letter
        drive_letter = self._find_available_drive()
        
        cmd = f'net use {drive_letter} "{self.remote_path}" {password} /user:{username}'
        
        try:
            subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            self.connected_drive = drive_letter
            if self.verbose:
                print(f"Connected to network share using drive {drive_letter}")
            return drive_letter
        except subprocess.CalledProcessError:
            raise ConnectionError("Failed to connect to network share. Please check credentials.")
    
    def _find_available_drive(self) -> str:
        """Find an available drive letter"""
        for letter in "ZYXWVUTSRQPONMLKJIHGFEDCBA":
            drive = f"{letter}:"
            if not os.path.exists(drive):
                return drive
        raise RuntimeError("No available drive letters")
    
    def disconnect(self) -> None:
        """Disconnect network drive"""
        if self.connected_drive:
            if self.verbose:
                print("Disconnecting network drive...")
            try:
                subprocess.run(
                    f"net use {self.connected_drive} /delete", 
                    shell=True, 
                    capture_output=True, 
                    check=True
                )
            except subprocess.CalledProcessError:
                pass


class BackupManager:
    """Handle backup operations"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def create_backup(self, target_path: str, backup_dir: str, app_name: str) -> Optional[str]:
        """Create backup of existing files"""
        if self.verbose:
            print("Creating backup of existing files...")
        
        if not os.path.exists(target_path):
            if self.verbose:
                print("Target directory doesn't exist - no backup needed.")
            return None
        
        try:
            files = os.listdir(target_path)
            if not files:
                if self.verbose:
                    print("No files to backup in target directory.")
                return None
            
            # Create backup
            now = datetime.now()
            backup_name = f"{app_name}_bkp_{now.strftime('%Y%m%d_%H%M%S')}.zip"
            backup_path = os.path.join(backup_dir, backup_name)
            
            if self.verbose:
                print(f"Creating backup: {backup_name}")
            
            # Ensure backup directory exists
            os.makedirs(backup_dir, exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(target_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, target_path)
                        zipf.write(file_path, arcname)
            
            if self.verbose:
                print(f"Backup created successfully: {backup_name}")
            return backup_path
            
        except Exception as e:
            if self.verbose:
                print(f"Warning: Failed to create backup: {e}, but continuing...")
            return None


class DeploymentExecutor:
    """Handle file deployment operations"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def clear_target_directory(self, target_path: str) -> None:
        """Clear target directory"""
        if self.verbose:
            print("Clearing target directory...")
        
        if not os.path.exists(target_path):
            os.makedirs(target_path, exist_ok=True)
            return
        
        try:
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not clear some files: {e}")
    
    def deploy_files(self, zip_path: str, target_path: str) -> None:
        """Deploy files from zip to target directory"""
        if self.verbose:
            print("Extracting files to remote location...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(target_path)
            
            if self.verbose:
                print("Files deployed successfully!")
                
        except Exception as e:
            raise RuntimeError(f"Failed to extract files to remote server: {e}")


class UserInterface:
    """Handle user interactions and display"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def show_header(self) -> None:
        """Show application header"""
        print("Starting deploy utility (deploy.py)...")
        print("==========================================")
        print("    Angular Build and Deploy Utility")
        print("==========================================")
    
    def show_deployment_info(self, site_name: str, app_name: str, config: DeploymentConfig, 
                           target_path: str, backup_enabled: bool, backup_path: Optional[str] = None) -> None:
        """Show deployment information"""
        print(f"\nSite Name: {site_name}")
        print(f"App Name: {app_name}")
        print(f"Remote Server: {config.remote_server}")
        print(f"Target Path: {target_path}")
        print(f"Backup Enabled: {'Yes' if backup_enabled else 'No'}")
        if backup_enabled and backup_path:
            print(f"Backup Directory: {backup_path}")
    
    def confirm_deployment(self, target_path: str, backup_enabled: bool, 
                          backup_path: Optional[str] = None, force: bool = False) -> bool:
        """Show deployment confirmation"""
        if force:
            return True
            
        print("\n==========================================")
        print("    DEPLOYMENT CONFIRMATION")
        print("==========================================")
        print(f"Target Path: {target_path}")
        print(f"Backup Enabled: {'Yes' if backup_enabled else 'No'}")
        if backup_enabled and backup_path:
            print(f"Backup Path: {backup_path}")
        print()
        
        confirm = input("Continue with deployment? (y/N): ").strip().lower()
        return confirm == 'y'
    
    def show_success(self, zip_name: str, target_path: str, server: str) -> None:
        """Show successful deployment message"""
        print("\n==========================================")
        print("    DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("==========================================")
        print(f"Local build: {zip_name}")
        print(f"Remote location: {target_path}")
        print(f"Server: {server}")
        print()
    
    def show_manual_instructions(self, zip_name: str, remote_path: str, target_dir: str) -> None:
        """Show manual deployment instructions"""
        print("\n==========================================")
        print("    MANUAL DEPLOYMENT REQUIRED")
        print("==========================================")
        print("Automatic deployment failed. Please deploy manually:")
        print()
        print(f"1. Copy the file '{zip_name}' to {remote_path}")
        print("2. Connect to the server via RDP or network share")
        print("3. Extract the zip file to your target directory")
        print()
        print(f"Network path: {remote_path}")
        print(f"Target directory: {target_dir}")
        print()


class DeploymentManager:
    """Main deployment orchestrator"""
    
    def __init__(self):
        self.arg_parser = ArgumentParser()
        self.config_manager = ConfigManager()
        self.ui = None
        self.build_manager = None
        self.network_manager = None
        self.backup_manager = None
        self.deployment_executor = None
        
    def run(self) -> None:
        """Main execution method"""
        try:
            # Parse arguments
            args = self.arg_parser.parse()
            
            # Handle configuration commands first
            if hasattr(args, 'command') and args.command == 'config':
                self._handle_config_command(args)
                return
            
            # If no command specified, treat as deploy (backward compatibility)
            if not hasattr(args, 'command') or args.command is None:
                args.command = 'deploy'
            
            if args.command == 'deploy':
                self._handle_deploy_command(args)
            
        except KeyboardInterrupt:
            print("\nOperation interrupted by user.")
        except Exception as e:
            print(f"Operation failed: {e}")
    
    def _handle_config_command(self, args) -> None:
        """Handle configuration commands"""
        if args.config_action == 'show':
            self.config_manager.show_config()
        elif args.config_action == 'set':
            try:
                self.config_manager.set_config_value(args.key, args.value)
            except ValueError as e:
                print(f"Error: {e}")
        elif args.config_action == 'reset':
            confirm = input("Are you sure you want to reset configuration to defaults? (y/N): ").strip().lower()
            if confirm == 'y':
                self.config_manager.reset_config()
            else:
                print("Configuration reset cancelled.")
        else:
            print("Error: No configuration action specified. Use 'show', 'set', or 'reset'.")
    
    def _handle_deploy_command(self, args) -> None:
        """Handle deployment command"""
        config = None
        target_dir = ""
        zip_name = ""
        
        try:
            # Load configuration defaults
            config_defaults = self.config_manager.load_config()
            
            # Initialize components
            self.ui = UserInterface(verbose=getattr(args, 'verbose', False))
            self.build_manager = BuildManager(verbose=getattr(args, 'verbose', False))
            self.backup_manager = BackupManager(verbose=getattr(args, 'verbose', False))
            self.deployment_executor = DeploymentExecutor(verbose=getattr(args, 'verbose', False))
            
            # Show header
            self.ui.show_header()
            
            # Parse site and app names
            site_name, app_name = self.arg_parser.parse_site_and_app(args)
            
            # Create configuration, using CLI args or config defaults
            config = DeploymentConfig(
                remote_server=getattr(args, 'server') or config_defaults.remote_server,
                remote_share=getattr(args, 'share') or config_defaults.remote_share,
                target_dir_pattern=getattr(args, 'target_dir') or config_defaults.target_dir_pattern,
                username=getattr(args, 'username') or config_defaults.username,
                password=getattr(args, 'password') or config_defaults.password
            )
            
            # Initialize network manager
            self.network_manager = NetworkManager(config, verbose=getattr(args, 'verbose', False))
            
            # Setup paths
            target_dir = config.target_dir_pattern.replace("{SITE_NAME}", site_name).replace("{APP_NAME}", app_name)
            
            # Show deployment info
            self.ui.show_deployment_info(site_name, app_name, config, target_dir, 
                                       not getattr(args, 'no_backup', False))
            
            if getattr(args, 'dry_run', False):
                print("\n[DRY RUN] Would perform the following actions:")
                print(f"1. {'Skip' if getattr(args, 'no_build', False) else 'Run'} ng build")
                print(f"2. Create zip file: {site_name}_{app_name}_build_TIMESTAMP.zip")
                print(f"3. Connect to: \\\\{config.remote_server}\\{config.remote_share}")
                print(f"4. {'Skip' if getattr(args, 'no_backup', False) else 'Create'} backup")
                print(f"5. Deploy to: {target_dir}")
                return
            
            # Validate Angular project
            self.build_manager.validate_angular_project()
            
            # Build process
            if not getattr(args, 'no_build', False):
                self.build_manager.run_build()
            
            build_folder = self.build_manager.find_build_folder(getattr(args, 'build_folder', None))
            zip_name = self.build_manager.create_zip_file(build_folder, site_name, app_name)
            
            # Test connection and connect to share
            self.network_manager.test_server_connection()
            accessible_path = self.network_manager.connect_to_share()
            
            # Setup full paths
            if accessible_path.endswith(':'):  # Mapped drive
                target_path = os.path.join(accessible_path, target_dir)
                backup_dir = os.path.join(accessible_path, f"IISDeployments\\{site_name}")
            else:  # UNC path
                target_path = os.path.join(accessible_path, target_dir)
                backup_dir = os.path.join(accessible_path, f"IISDeployments\\{site_name}")
            
            # Confirm deployment
            if not self.ui.confirm_deployment(target_path, not getattr(args, 'no_backup', False), 
                                            backup_dir, getattr(args, 'force', False)):
                print("Deployment cancelled by user.")
                return
            
            print("\nProceeding with deployment...")
            
            # Create backup if enabled
            backup_file = None
            if not getattr(args, 'no_backup', False):
                backup_file = self.backup_manager.create_backup(target_path, backup_dir, app_name)
            
            # Ensure target directory exists
            os.makedirs(target_path, exist_ok=True)
            
            # Deploy files
            self.deployment_executor.clear_target_directory(target_path)
            self.deployment_executor.deploy_files(zip_name, target_path)
            
            # Show success
            self.ui.show_success(zip_name, target_path, config.remote_server)
            
        except KeyboardInterrupt:
            print("\nDeployment interrupted by user.")
        except Exception as e:
            print(f"Deployment failed: {e}")
            if hasattr(self, 'ui') and self.ui and config:
                self.ui.show_manual_instructions(
                    zip_name or 'build.zip',
                    f"\\\\{config.remote_server}\\{config.remote_share}",
                    target_dir
                )
        finally:
            # Cleanup
            if self.network_manager:
                self.network_manager.disconnect()
            input("Press Enter to continue...")


def main():
    """Main entry point"""
    deploy_manager = DeploymentManager()
    deploy_manager.run()


if __name__ == "__main__":
    main()
