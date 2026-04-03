"""
Configuration Handler - Windows Compatible
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional

from utils.logger import get_logger
from utils.platform_utils import PlatformUtils


class ConfigHandler:
    """Handles configuration management for installed tools."""
    
    def __init__(self, tool_manager):
        """Initialize the Configuration Handler."""
        self.tool_manager = tool_manager
        self.logger = get_logger(__name__)
        self.platform = PlatformUtils.get_platform()
    
    def configure_tool(self, tool_name: str, settings: Optional[Dict] = None) -> bool:
        """Configure a tool after installation."""
        print(f"\n⚙️  Configuring {tool_name}...")
        
        tool_info = self.tool_manager.installed_tools.get(tool_name)
        if not tool_info:
            print(f"❌ {tool_name} is not installed")
            return False
        
        try:
            # Add to PATH
            self._add_to_path(tool_name, tool_info.install_path)
            
            # Update eSim configuration
            self._update_esim_config(tool_name, tool_info.install_path)
            
            print(f"✅ {tool_name} configured successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Configuration failed: {e}")
            return False
    
    def _add_to_path(self, tool_name: str, install_path: str):
        """Add tool to system PATH."""
        install_path = Path(install_path)
        
        # Find binary directory
        bin_dirs = ['bin', 'Spice64/bin', 'scripts', '']
        for bin_dir in bin_dirs:
            bin_path = install_path / bin_dir if bin_dir else install_path
            if bin_path.exists():
                break
        else:
            bin_path = install_path
        
        bin_path_str = str(bin_path)
        
        # Add to current session
        if bin_path_str not in os.environ.get('PATH', ''):
            os.environ['PATH'] = bin_path_str + os.pathsep + os.environ.get('PATH', '')
            print(f"   Added to PATH: {bin_path_str}")
        
        if self.platform == 'windows':
            self._add_to_windows_path(bin_path_str)
    
    def _add_to_windows_path(self, path: str):
        """Add path to Windows user PATH."""
        try:
            import winreg
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Environment',
                0,
                winreg.KEY_ALL_ACCESS
            )
            
            try:
                current_path, _ = winreg.QueryValueEx(key, 'Path')
            except WindowsError:
                current_path = ''
            
            if path not in current_path:
                new_path = f"{path};{current_path}" if current_path else path
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                print(f"   Added to Windows PATH (restart terminal to apply)")
            
            winreg.CloseKey(key)
            
        except Exception as e:
            self.logger.warning(f"Could not update Windows PATH: {e}")
    
    def _update_esim_config(self, tool_name: str, install_path: str):
        """Update eSim's configuration."""
        esim_config_path = self._get_esim_config_path()
        
        try:
            if esim_config_path.exists():
                with open(esim_config_path, 'r', encoding='utf-8') as f:
                    esim_config = json.load(f)
            else:
                esim_config = {}
            
            if 'tools' not in esim_config:
                esim_config['tools'] = {}
            
            esim_config['tools'][tool_name] = {
                'path': install_path,
                'version': self.tool_manager.installed_tools[tool_name].version
            }
            
            esim_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(esim_config_path, 'w', encoding='utf-8') as f:
                json.dump(esim_config, f, indent=4)
                
        except Exception as e:
            self.logger.warning(f"Could not update eSim config: {e}")
    
    def _get_esim_config_path(self) -> Path:
        """Get the path to eSim's configuration file."""
        if self.platform == 'windows':
            return Path(os.environ.get('APPDATA', '')) / 'eSim' / 'esim_config.json'
        elif self.platform == 'darwin':
            return Path.home() / 'Library' / 'Preferences' / 'eSim' / 'esim_config.json'
        else:
            return Path.home() / '.config' / 'esim' / 'esim_config.json'
    
    def remove_tool_config(self, tool_name: str) -> bool:
        """Remove tool configuration after uninstallation."""
        try:
            esim_config_path = self._get_esim_config_path()
            if esim_config_path.exists():
                with open(esim_config_path, 'r', encoding='utf-8') as f:
                    esim_config = json.load(f)
                
                if 'tools' in esim_config and tool_name in esim_config['tools']:
                    del esim_config['tools'][tool_name]
                    
                    with open(esim_config_path, 'w', encoding='utf-8') as f:
                        json.dump(esim_config, f, indent=4)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove config: {e}")
            return False