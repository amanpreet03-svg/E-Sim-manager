import os
import sys
import platform
import subprocess
import shutil
from typing import Optional, Dict
from pathlib import Path


class PlatformUtils:
    """Utility class for platform-specific operations."""
    
    @staticmethod
    def get_platform() -> str:
        """Get the current platform."""
        system = platform.system().lower()
        if system == 'windows':
            return 'windows'
        elif system == 'darwin':
            return 'darwin'
        else:
            return 'linux'
    
    @staticmethod
    def get_platform_info() -> Dict:
        """Get detailed platform information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'platform': PlatformUtils.get_platform()
        }
    
    @staticmethod
    def get_package_manager() -> Optional[str]:
        """Detect the system's package manager."""
        plat = PlatformUtils.get_platform()
        
        if plat == 'windows':
            # Check for Windows package managers
            if PlatformUtils._command_exists('winget'):
                return 'winget'
            elif PlatformUtils._command_exists('choco'):
                return 'chocolatey'
            elif PlatformUtils._command_exists('scoop'):
                return 'scoop'
            return None
            
        elif plat == 'darwin':
            if PlatformUtils._command_exists('brew'):
                return 'homebrew'
            return None
            
        else:  # Linux
            package_managers = [
                ('apt-get', 'apt'),
                ('dnf', 'dnf'),
                ('yum', 'yum'),
                ('pacman', 'pacman'),
            ]
            for cmd, name in package_managers:
                if PlatformUtils._command_exists(cmd):
                    return name
            return None
    
    @staticmethod
    def _command_exists(command: str) -> bool:
        """Check if a command exists in PATH."""
        return shutil.which(command) is not None
    
    @staticmethod
    def get_home_directory() -> Path:
        """Get the user's home directory."""
        return Path.home()
    
    @staticmethod
    def get_appdata_directory() -> Path:
        """Get the appropriate app data directory for the platform."""
        plat = PlatformUtils.get_platform()
        
        if plat == 'windows':
            return Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        elif plat == 'darwin':
            return Path.home() / 'Library' / 'Application Support'
        else:
            return Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
    
    @staticmethod
    def get_config_directory() -> Path:
        """Get the appropriate config directory for the platform."""
        plat = PlatformUtils.get_platform()
        
        if plat == 'windows':
            return Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        elif plat == 'darwin':
            return Path.home() / 'Library' / 'Preferences'
        else:
            return Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    
    @staticmethod
    def is_admin() -> bool:
        """Check if running with administrator privileges."""
        try:
            if PlatformUtils.get_platform() == 'windows':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    @staticmethod
    def open_url(url: str) -> bool:
        """Open a URL in the default browser."""
        import webbrowser
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_downloads_directory() -> Path:
        """Get the user's Downloads directory."""
        plat = PlatformUtils.get_platform()
        
        if plat == 'windows':
            # Try to get from registry or use default
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
                    downloads = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
                    return Path(downloads)
            except Exception:
                return Path.home() / 'Downloads'
        else:
            return Path.home() / 'Downloads'