"""
Updater Module - Windows Compatible
"""

import subprocess
import shutil
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

from utils.logger import get_logger
from utils.platform_utils import PlatformUtils


class Updater:
    """Handles update checking and application for installed tools."""
    
    def __init__(self, tool_manager):
        """Initialize the Updater."""
        self.tool_manager = tool_manager
        self.logger = get_logger(__name__)
        self.platform = PlatformUtils.get_platform()
    
    def check_update(self, tool_name: str) -> Optional[str]:
        """Check if an update is available for a tool."""
        if tool_name not in self.tool_manager.installed_tools:
            return None
        
        installed_info = self.tool_manager.installed_tools[tool_name]
        current_version = installed_info.version
        
        tool_config = self.tool_manager.registry.get_tool_config(tool_name)
        if not tool_config:
            return None
        
        latest_version = tool_config.get('versions', {}).get('latest')
        
        if latest_version and self._is_newer(latest_version, current_version):
            return latest_version
        
        return None
    
    def check_all_updates(self) -> Dict[str, Optional[str]]:
        """Check for updates for all installed tools."""
        updates = {}
        for tool_name in self.tool_manager.installed_tools:
            updates[tool_name] = self.check_update(tool_name)
        return updates
    
    def update(self, tool_name: str) -> bool:
        """Update a tool to the latest version."""
        if tool_name not in self.tool_manager.installed_tools:
            print(f"❌ {tool_name} is not installed")
            return False
        
        new_version = self.check_update(tool_name)
        if not new_version:
            print(f"✅ {tool_name} is already up to date")
            return True
        
        current = self.tool_manager.installed_tools[tool_name].version
        print(f"\n🔄 Updating {tool_name}: {current} → {new_version}")
        
        # Create backup
        self._create_backup(tool_name)
        
        try:
            # Reinstall with new version
            self.tool_manager.installer.uninstall(tool_name)
            success = self.tool_manager.installer.install(tool_name, new_version)
            
            if success:
                print(f"✅ {tool_name} updated to {new_version}")
                return True
            else:
                print(f"❌ Update failed, restoring backup...")
                self._restore_backup(tool_name)
                return False
                
        except Exception as e:
            print(f"❌ Update error: {e}")
            self._restore_backup(tool_name)
            return False
    
    def _is_newer(self, new_version: str, current_version: str) -> bool:
        """Compare version strings."""
        try:
            from packaging import version
            return version.parse(new_version) > version.parse(current_version)
        except Exception:
            return new_version > current_version
    
    def _create_backup(self, tool_name: str) -> bool:
        """Create a backup of the current installation."""
        tool_info = self.tool_manager.installed_tools.get(tool_name)
        if not tool_info:
            return False
        
        install_path = Path(tool_info.install_path)
        if not install_path.exists():
            return False
        
        backup_dir = self.tool_manager.tools_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{tool_name}_{timestamp}"
        
        try:
            shutil.copytree(install_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def _restore_backup(self, tool_name: str) -> bool:
        """Restore from the most recent backup."""
        backup_dir = self.tool_manager.tools_dir / "backups"
        
        backups = sorted(backup_dir.glob(f"{tool_name}_*"), reverse=True)
        if not backups:
            return False
        
        latest_backup = backups[0]
        install_path = self.tool_manager.tools_dir / tool_name
        
        try:
            if install_path.exists():
                shutil.rmtree(install_path)
            shutil.copytree(latest_backup, install_path)
            self.logger.info(f"Restored from backup: {latest_backup}")
            return True
        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            return False