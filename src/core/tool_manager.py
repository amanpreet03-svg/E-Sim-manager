"""
Core Tool Manager - Windows Compatible
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .installer import Installer
from .updater import Updater
from .config_handler import ConfigHandler
from .dependency_checker import DependencyChecker
from utils.logger import get_logger, setup_logger
from utils.platform_utils import PlatformUtils
from tools.tool_registry import ToolRegistry


class ToolStatus(Enum):
    """Tool installation status."""
    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    UPDATE_AVAILABLE = "update_available"
    INSTALLING = "installing"
    ERROR = "error"


@dataclass
class ToolInfo:
    """Tool information."""
    name: str
    version: str = ""
    status: ToolStatus = ToolStatus.NOT_INSTALLED
    install_path: str = ""
    install_date: str = ""
    latest_version: str = ""
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'status': self.status.value,
            'install_path': self.install_path,
            'install_date': self.install_date,
            'latest_version': self.latest_version,
            'description': self.description,
            'dependencies': self.dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ToolInfo':
        return cls(
            name=data.get('name', ''),
            version=data.get('version', ''),
            status=ToolStatus(data.get('status', 'not_installed')),
            install_path=data.get('install_path', ''),
            install_date=data.get('install_date', ''),
            latest_version=data.get('latest_version', ''),
            description=data.get('description', ''),
            dependencies=data.get('dependencies', [])
        )


class ToolManager:
    """Main Tool Manager class."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the Tool Manager."""
        # Setup logging first
        setup_logger()
        self.logger = get_logger(__name__)
        
        self.platform = PlatformUtils.get_platform()
        
        # Set up directories
        self.base_dir = Path(__file__).parent.parent.parent
        self.config_dir = Path(config_dir) if config_dir else self.base_dir / "config"
        self.logs_dir = self.base_dir / "logs"
        self.tools_dir = self._get_tools_directory()
        
        # Create directories
        self._create_directories()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize components
        self.registry = ToolRegistry()
        self.installer = Installer(self)
        self.updater = Updater(self)
        self.config_handler = ConfigHandler(self)
        self.dependency_checker = DependencyChecker(self)
        
        # Load installed tools
        self.installed_tools: Dict[str, ToolInfo] = {}
        self._load_installed_tools()
        
        self.logger.info(f"Tool Manager initialized on {self.platform}")
    
    def _get_tools_directory(self) -> Path:
        """Get tools installation directory."""
        if self.platform == "windows":
            return Path(os.environ.get('LOCALAPPDATA', '')) / "eSim" / "tools"
        elif self.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "eSim" / "tools"
        else:
            return Path.home() / ".local" / "share" / "esim" / "tools"
    
    def _create_directories(self):
        """Create necessary directories."""
        for directory in [self.config_dir, self.logs_dir, self.tools_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict:
        """Load configuration from files."""
        config = {}
        config_files = ['tools.json', 'settings.json', 'paths.json']
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config[config_file.replace('.json', '')] = json.load(f)
                except Exception as e:
                    self.logger.error(f"Error loading {config_file}: {e}")
                    config[config_file.replace('.json', '')] = {}
            else:
                config[config_file.replace('.json', '')] = {}
        
        return config
    
    def _load_installed_tools(self):
        """Load information about installed tools."""
        installed_file = self.config_dir / "installed.json"
        if installed_file.exists():
            try:
                with open(installed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, info in data.items():
                        self.installed_tools[name] = ToolInfo.from_dict(info)
            except Exception as e:
                self.logger.error(f"Error loading installed tools: {e}")
    
    def _save_installed_tools(self):
        """Save installed tools information."""
        installed_file = self.config_dir / "installed.json"
        data = {name: info.to_dict() for name, info in self.installed_tools.items()}
        with open(installed_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    
    # ==================== Public API ====================
    
    def install_tool(self, tool_name: str, version: Optional[str] = None,
                     force: bool = False) -> bool:
        """Install a tool."""
        # Check if already installed
        if tool_name in self.installed_tools and not force:
            if self.installed_tools[tool_name].status == ToolStatus.INSTALLED:
                print(f"⚠️  {tool_name} is already installed. Use --force to reinstall.")
                return False
        
        # Perform installation
        success = self.installer.install(tool_name, version)
        
        if success:
            # Update registry
            tool_config = self.registry.get_tool_config(tool_name)
            self.installed_tools[tool_name] = ToolInfo(
                name=tool_name,
                version=version or tool_config.get('versions', {}).get('latest', 'unknown'),
                status=ToolStatus.INSTALLED,
                install_path=str(self.tools_dir / tool_name),
                install_date=datetime.now().isoformat(),
                description=tool_config.get('description', '')
            )
            self._save_installed_tools()
            
            # Configure
            self.config_handler.configure_tool(tool_name)
        
        return success
    
    def uninstall_tool(self, tool_name: str) -> bool:
        """Uninstall a tool."""
        if tool_name not in self.installed_tools:
            print(f"❌ {tool_name} is not installed")
            return False
        
        success = self.installer.uninstall(tool_name)
        
        if success:
            del self.installed_tools[tool_name]
            self._save_installed_tools()
            self.config_handler.remove_tool_config(tool_name)
        
        return success
    
    def update_tool(self, tool_name: str) -> bool:
        """Update a tool."""
        return self.updater.update(tool_name)
    
    def update_all_tools(self) -> Dict[str, bool]:
        """Update all installed tools."""
        results = {}
        for tool_name in self.installed_tools:
            results[tool_name] = self.update_tool(tool_name)
        return results
    
    def check_updates(self) -> Dict[str, Optional[str]]:
        """Check for available updates."""
        return self.updater.check_all_updates()
    
    def get_tool_info(self, tool_name: str) -> Optional[ToolInfo]:
        """Get information about a tool."""
        if tool_name in self.installed_tools:
            return self.installed_tools[tool_name]
        
        tool_config = self.registry.get_tool_config(tool_name)
        if tool_config:
            return ToolInfo(
                name=tool_name,
                latest_version=tool_config.get('versions', {}).get('latest', ''),
                description=tool_config.get('description', ''),
                dependencies=tool_config.get('dependencies', [])
            )
        
        return None
    
    def list_installed_tools(self) -> List[ToolInfo]:
        """Get list of installed tools."""
        return list(self.installed_tools.values())
    
    def list_available_tools(self) -> List[Dict]:
        """Get list of available tools."""
        return self.registry.get_all_tools()
    
    def check_all_dependencies(self) -> Dict[str, List[str]]:
        """Check all system dependencies."""
        return self.dependency_checker.check_system_dependencies()
    
    def configure_tool(self, tool_name: str, settings: Optional[Dict] = None) -> bool:
        """Configure a tool."""
        return self.config_handler.configure_tool(tool_name, settings)
    
    def get_logs(self, lines: int = 50) -> List[str]:
        """Get recent log entries."""
        log_files = sorted(self.logs_dir.glob("tool_manager_*.log"), reverse=True)
        if not log_files:
            return []
        
        try:
            with open(log_files[0], 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except Exception:
            return []