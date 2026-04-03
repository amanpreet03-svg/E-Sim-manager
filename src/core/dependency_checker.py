"""
Dependency Checker - Windows Compatible
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

from utils.logger import get_logger
from utils.platform_utils import PlatformUtils


class DependencyChecker:
    """Manages system dependencies required by external tools."""
    
    # Windows-focused dependency definitions
    DEPENDENCY_CHECKS = {
        'python3': {
            'check': ['python', '--version'],
            'verify': lambda: sys.version_info >= (3, 8),
            'install': {
                'windows': 'Download from https://www.python.org/downloads/',
                'linux': 'sudo apt-get install -y python3',
                'darwin': 'brew install python3'
            }
        },
        'pip': {
            'check': ['pip', '--version'],
            'install': {
                'windows': 'python -m ensurepip --upgrade',
                'linux': 'sudo apt-get install -y python3-pip',
                'darwin': 'python3 -m ensurepip'
            }
        },
        'git': {
            'check': ['git', '--version'],
            'install': {
                'windows': 'winget install Git.Git',
                'windows_alt': 'Download from https://git-scm.com/download/win',
                'linux': 'sudo apt-get install -y git',
                'darwin': 'brew install git'
            }
        },
        'chocolatey': {
            'check': ['choco', '--version'],
            'optional': True,
            'install': {
                'windows': 'See https://chocolatey.org/install'
            }
        },
        'winget': {
            'check': ['winget', '--version'],
            'optional': True,
            'windows_only': True
        }
    }
    
    def __init__(self, tool_manager):
        """Initialize the Dependency Checker."""
        self.tool_manager = tool_manager
        self.logger = get_logger(__name__)
        self.platform = PlatformUtils.get_platform()
    
    def check_dependency(self, dependency: str) -> bool:
        """Check if a single dependency is installed."""
        dep_info = self.DEPENDENCY_CHECKS.get(dependency)
        
        if not dep_info:
            return self._check_command_exists(dependency)
        
        # Skip non-Windows dependencies on Windows
        if dep_info.get('windows_only') and self.platform != 'windows':
            return True
        
        # Use custom verify function if available
        if 'verify' in dep_info:
            try:
                return dep_info['verify']()
            except Exception:
                pass
        
        # Check command
        if 'check' in dep_info:
            return self._run_check_command(dep_info['check'])
        
        return False
    
    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        return shutil.which(command) is not None
    
    def _run_check_command(self, command: List[str]) -> bool:
        """Run a command to check for dependency."""
        try:
            # Use shell=True on Windows for better compatibility
            if self.platform == 'windows':
                result = subprocess.run(
                    ' '.join(command),
                    shell=True,
                    capture_output=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    timeout=10
                )
            return result.returncode == 0
        except Exception:
            return False
    
    def check_tool_dependencies(self, tool_name: str) -> Tuple[bool, List[str]]:
        """Check all dependencies for a specific tool."""
        tool_config = self.tool_manager.registry.get_tool_config(tool_name)
        if not tool_config:
            return True, []
        
        # On Windows, most tools are self-contained
        if self.platform == 'windows':
            return True, []
        
        dependencies = tool_config.get('dependencies', [])
        missing = []
        
        for dep in dependencies:
            if not self.check_dependency(dep):
                missing.append(dep)
        
        return len(missing) == 0, missing
    
    def check_system_dependencies(self) -> Dict[str, List[str]]:
        """Check all common system dependencies."""
        result = {
            'installed': [],
            'missing': [],
            'optional_missing': []
        }
        
        # Core dependencies
        core_deps = ['python3', 'pip', 'git']
        
        for dep in core_deps:
            if self.check_dependency(dep):
                result['installed'].append(dep)
            else:
                result['missing'].append(dep)
        
        # Optional Windows package managers
        if self.platform == 'windows':
            for pm in ['chocolatey', 'winget']:
                if self.check_dependency(pm):
                    result['installed'].append(pm)
                else:
                    result['optional_missing'].append(pm)
        
        return result
    
    def get_dependency_info(self, dependency: str) -> Dict:
        """Get information about a dependency."""
        dep_info = self.DEPENDENCY_CHECKS.get(dependency, {})
        
        return {
            'name': dependency,
            'installed': self.check_dependency(dependency),
            'install_command': dep_info.get('install', {}).get(self.platform, 'Unknown'),
            'optional': dep_info.get('optional', False)
        }
    
    def install_dependency(self, dependency: str) -> bool:
        """Attempt to install a missing dependency."""
        dep_info = self.DEPENDENCY_CHECKS.get(dependency)
        
        if not dep_info:
            self.logger.error(f"Unknown dependency: {dependency}")
            return False
        
        install_cmd = dep_info.get('install', {}).get(self.platform)
        
        if not install_cmd:
            self.logger.warning(f"No automatic installation for {dependency}")
            return False
        
        # Check if it's a URL/manual instruction
        if install_cmd.startswith('http') or install_cmd.startswith('Download') or install_cmd.startswith('See'):
            self.logger.info(f"Manual installation required for {dependency}:")
            self.logger.info(f"  {install_cmd}")
            print(f"\n📥 Please install {dependency} manually:")
            print(f"   {install_cmd}\n")
            return False
        
        self.logger.info(f"Installing {dependency}...")
        
        try:
            if self.platform == 'windows':
                result = subprocess.run(
                    install_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            else:
                result = subprocess.run(
                    install_cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            return False
    
    def fix_all_dependencies(self) -> Dict[str, bool]:
        """Attempt to fix all missing dependencies."""
        result = {}
        deps_status = self.check_system_dependencies()
        
        if not deps_status['missing']:
            print("✅ No missing dependencies!")
            return result
        
        print(f"\n🔧 Attempting to fix {len(deps_status['missing'])} missing dependencies...\n")
        
        for dep in deps_status['missing']:
            result[dep] = self.install_dependency(dep)
        
        return result
    
    def get_version(self, dependency: str) -> Optional[str]:
        """Get the version of an installed dependency."""
        dep_info = self.DEPENDENCY_CHECKS.get(dependency)
        
        if not dep_info or 'check' not in dep_info:
            return None
        
        try:
            if self.platform == 'windows':
                result = subprocess.run(
                    ' '.join(dep_info['check']),
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    dep_info['check'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode == 0:
                import re
                output = result.stdout + result.stderr
                match = re.search(r'(\d+\.\d+(?:\.\d+)?)', output)
                if match:
                    return match.group(1)
        except Exception:
            pass
        
        return None
    
    def print_status(self):
        """Print a formatted dependency status report."""
        status = self.check_system_dependencies()
        
        print("\n" + "="*50)
        print("📋 SYSTEM DEPENDENCY STATUS")
        print("="*50)
        
        if status['installed']:
            print("\n✅ Installed:")
            for dep in status['installed']:
                version = self.get_version(dep)
                version_str = f" (v{version})" if version else ""
                print(f"   • {dep}{version_str}")
        
        if status['missing']:
            print("\n❌ Missing:")
            for dep in status['missing']:
                info = self.get_dependency_info(dep)
                print(f"   • {dep}")
                if info.get('install_command'):
                    print(f"     Install: {info['install_command']}")
        
        if status.get('optional_missing'):
            print("\n⚠️  Optional (not installed):")
            for dep in status['optional_missing']:
                print(f"   • {dep}")
        
        print("\n" + "="*50 + "\n")