"""
KiCad Tool Module
Implementation for KiCad EDA suite.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from .base_tool import BaseTool, ToolMetadata, VersionInfo, InstallMethod
from utils.platform_utils import PlatformUtils


class KiCadTool(BaseTool):
    """
    KiCad tool implementation.
    
    KiCad is an open-source EDA suite for schematic capture and PCB design.
    It integrates with eSim for complete circuit design workflow.
    """
    
    # Version download URLs
    DOWNLOAD_URLS = {
        'windows': {
            '9.0': 'https://github.com/KiCad/kicad-source-mirror/releases/download/9.0.0/kicad-9.0.0-x86_64.exe',
            '8.0': 'https://github.com/KiCad/kicad-source-mirror/releases/download/8.0.0/kicad-8.0.0-x86_64.exe',
            '7.0': 'https://github.com/KiCad/kicad-source-mirror/releases/download/7.0.0/kicad-7.0.0-x86_64.exe'
        },
        'linux': None,  # Use package manager or PPA
        'darwin': None  # Use Homebrew cask
    }
    
    # Package manager commands
    PACKAGE_COMMANDS = {
        'linux': {
            'apt': 'sudo add-apt-repository -y ppa:kicad/kicad-9.0-releases && sudo apt-get update && sudo apt-get install -y kicad',
            'dnf': 'sudo dnf install -y kicad',
            'pacman': 'sudo pacman -S --noconfirm kicad',
            'flatpak': 'flatpak install -y flathub org.kicad.KiCad'
        },
        'darwin': {
            'homebrew': 'brew install --cask kicad'
        },
        'windows': {
            'chocolatey': 'choco install kicad -y',
            'winget': 'winget install KiCad.KiCad'
        }
    }
    
    def __init__(self):
        """Initialize KiCad tool."""
        super().__init__()
        
        self._metadata = ToolMetadata(
            name='kicad',
            display_name='KiCad',
            description='Open-source EDA suite for schematic capture and PCB design',
            homepage='https://www.kicad.org/',
            license='GPL-3.0',
            category='EDA',
            maintainer='KiCad Team',
            tags=['eda', 'pcb', 'schematic', 'electronics', 'cad']
        )
        
        self._version_info = VersionInfo(
            latest='9.0',
            stable='8.0',
            available=['9.0', '8.0', '7.0', '6.0', '5.1'],
            min_supported='6.0'
        )
    
    @property
    def tool_id(self) -> str:
        """Get tool ID."""
        return 'kicad'
    
    @property
    def metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return self._metadata
    
    @property
    def version_info(self) -> VersionInfo:
        """Get version information."""
        return self._version_info
    
    @property
    def dependencies(self) -> List[str]:
        """Get list of dependencies."""
        deps = {
            'linux': ['python3', 'wxwidgets', 'opencascade', 'ngspice'],
            'darwin': ['python3', 'wxwidgets'],
            'windows': ['python3']
        }
        return deps.get(self.platform, [])
    
    def get_download_url(self, version: str) -> Optional[str]:
        """Get download URL for specific version."""
        platform_urls = self.DOWNLOAD_URLS.get(self.platform)
        if platform_urls and isinstance(platform_urls, dict):
            # Find closest version
            for v in [version, f"{version}.0", version.split('.')[0] + '.0']:
                if v in platform_urls:
                    return platform_urls[v]
        return None
    
    def get_install_method(self) -> InstallMethod:
        """Get preferred installation method."""
        if self.platform == 'darwin':
            return InstallMethod.PACKAGE_MANAGER
        elif self.platform == 'linux':
            return InstallMethod.PACKAGE_MANAGER
        else:  # Windows
            pkg_manager = PlatformUtils.get_package_manager()
            if pkg_manager:
                return InstallMethod.PACKAGE_MANAGER
            return InstallMethod.DOWNLOAD_INSTALLER
    
    def get_package_manager_command(self) -> Optional[str]:
        """Get package manager installation command."""
        pkg_manager = PlatformUtils.get_package_manager()
        platform_commands = self.PACKAGE_COMMANDS.get(self.platform, {})
        return platform_commands.get(pkg_manager)
    
    def _get_main_command(self) -> str:
        """Get main executable command."""
        if self.platform == 'darwin':
            return '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad'
        return 'kicad'
    
    def _get_version_command(self) -> List[str]:
        """Get version check command."""
        return ['kicad-cli', 'version']
    
    def _parse_version_output(self, output: str) -> Optional[str]:
        """Parse version from KiCad output."""
        # KiCad version output varies by version
        # Try multiple patterns
        patterns = [
            r'KiCad\s+(\d+\.\d+\.\d+)',
            r'(\d+\.\d+\.\d+)',
            r'Version:\s*(\d+\.\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for KiCad."""
        env_vars = {}
        
        if self._install_path:
            env_vars.update({
                'KICAD_INSTALL_PATH': str(self._install_path),
                'KICAD_SYMBOL_DIR': str(self._get_library_path('symbols')),
                'KICAD_FOOTPRINT_DIR': str(self._get_library_path('footprints')),
                'KICAD_3DMODEL_DIR': str(self._get_library_path('3dmodels')),
                'KICAD_TEMPLATE_DIR': str(self._get_library_path('template'))
            })
        else:
            # Default paths based on platform
            if self.platform == 'linux':
                env_vars.update({
                    'KICAD_SYMBOL_DIR': '/usr/share/kicad/symbols',
                    'KICAD_FOOTPRINT_DIR': '/usr/share/kicad/footprints',
                    'KICAD_3DMODEL_DIR': '/usr/share/kicad/3dmodels'
                })
            elif self.platform == 'darwin':
                kicad_app = '/Applications/KiCad'
                env_vars.update({
                    'KICAD_SYMBOL_DIR': f'{kicad_app}/KiCad.app/Contents/SharedSupport/symbols',
                    'KICAD_FOOTPRINT_DIR': f'{kicad_app}/KiCad.app/Contents/SharedSupport/footprints'
                })
        
        return env_vars
    
    def _get_library_path(self, lib_type: str) -> Path:
        """Get path to a specific library type."""
        if self._install_path:
            return self._install_path / 'share' / 'kicad' / lib_type
        
        # Default paths
        if self.platform == 'linux':
            return Path('/usr/share/kicad') / lib_type
        elif self.platform == 'darwin':
            return Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport') / lib_type
        else:
            return Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'KiCad' / lib_type
    
    def get_config_files(self) -> Dict[str, str]:
        """Get KiCad configuration files."""
        # KiCad uses its own config system, return minimal config
        kicad_common = """
# KiCad common configuration
# Generated by eSim Tool Manager

[system]
# Enable eSim integration
esim_integration=true

[environment]
# Custom environment variables can be added here
"""
        return {
            'kicad_common.json': self._generate_kicad_json_config(),
            'kicad_common': kicad_common
        }
    
    def _generate_kicad_json_config(self) -> str:
        """Generate KiCad JSON configuration."""
        import json
        
        config = {
            "meta": {
                "filename": "kicad_common.json",
                "version": 1
            },
            "environment": {
                "vars": {}
            },
            "system": {
                "esim_integration": True
            }
        }
        
        return json.dumps(config, indent=2)
    
    def post_install_hook(self) -> bool:
        """Post-installation hook for KiCad."""
        self.logger.info("Running KiCad post-install configuration...")
        
        # Verify installation
        if not self.verify_installation():
            self.logger.warning("KiCad installation verification failed, continuing anyway")
        
        # Setup Python scripting environment if available
        self._setup_python_scripting()
        
        # Create eSim integration symlinks if needed
        self._setup_esim_integration()
        
        self.logger.info("KiCad post-install completed")
        return True
    
    def _setup_python_scripting(self):
        """Setup Python scripting for KiCad."""
        try:
            # Check if kicad python is available
            if self.platform == 'linux':
                scripting_path = Path('/usr/share/kicad/scripting')
            elif self.platform == 'darwin':
                scripting_path = Path('/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework')
            else:
                scripting_path = None
            
            if scripting_path and scripting_path.exists():
                self.logger.info(f"KiCad Python scripting available at {scripting_path}")
        except Exception as e:
            self.logger.debug(f"Python scripting setup: {e}")
    
    def _setup_esim_integration(self):
        """Setup integration with eSim."""
        try:
            # Create plugin directory for eSim
            plugin_dir = self._get_plugin_directory()
            if plugin_dir:
                esim_plugin_dir = plugin_dir / 'esim'
                esim_plugin_dir.mkdir(parents=True, exist_ok=True)
                
                # Create __init__.py
                init_file = esim_plugin_dir / '__init__.py'
                if not init_file.exists():
                    init_file.write_text('# eSim KiCad Plugin\n')
                
                self.logger.info(f"Created eSim plugin directory: {esim_plugin_dir}")
        except Exception as e:
            self.logger.debug(f"eSim integration setup: {e}")
    
    def _get_plugin_directory(self) -> Optional[Path]:
        """Get KiCad plugin directory."""
        if self.platform == 'linux':
            return Path.home() / '.local' / 'share' / 'kicad' / '9.0' / 'scripting' / 'plugins'
        elif self.platform == 'darwin':
            return Path.home() / 'Documents' / 'KiCad' / '9.0' / 'scripting' / 'plugins'
        elif self.platform == 'windows':
            return Path(os.environ.get('APPDATA', '')) / 'kicad' / '9.0' / 'scripting' / 'plugins'
        return None
    
    def get_binary_paths(self) -> List[Path]:
        """Get paths containing KiCad binaries."""
        paths = []
        
        if self.platform == 'linux':
            paths.append(Path('/usr/bin'))
            paths.append(Path('/usr/local/bin'))
        elif self.platform == 'darwin':
            paths.append(Path('/Applications/KiCad/KiCad.app/Contents/MacOS'))
        elif self.platform == 'windows':
            # Common Windows installation paths
            program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
            paths.append(Path(program_files) / 'KiCad' / 'bin')
            paths.append(Path(program_files) / 'KiCad' / '9.0' / 'bin')
        
        if self._install_path:
            paths.append(self._install_path / 'bin')
        
        return [p for p in paths if p.exists()]
    
    def get_applications(self) -> Dict[str, str]:
        """
        Get KiCad applications and their commands.
        
        Returns:
            Dictionary mapping application names to commands
        """
        base_cmd = 'kicad' if self.platform != 'darwin' else str(self._get_main_command())
        
        return {
            'KiCad': 'kicad',
            'Eeschema': 'eeschema',
            'PCB Editor': 'pcbnew',
            'Symbol Editor': 'kicad-sym-editor',
            'Footprint Editor': 'kicad-fp-editor',
            'Gerber Viewer': 'gerbview',
            'Image Converter': 'bitmap2component',
            'Calculator': 'pcb_calculator',
            'Drawing Sheet Editor': 'pl_editor'
        }


class KiCadConfig:
    """
    KiCad-specific configuration helper.
    """
    
    @staticmethod
    def get_default_libraries() -> Dict[str, List[str]]:
        """
        Get default KiCad libraries.
        
        Returns:
            Dictionary with library types and their default libraries
        """
        return {
            'symbols': [
                'Device', 'Connector', 'Power', 'MCU', 'Analog', 'Logic',
                'Transistor', 'Diode', 'Regulator', 'Interface'
            ],
            'footprints': [
                'Package_DIP', 'Package_SO', 'Package_QFP', 'Connector_PinHeader',
                'Resistor_SMD', 'Capacitor_SMD', 'LED_SMD'
            ]
        }
    
    @staticmethod
    def generate_project_file(project_name: str, 
                               schematic_file: str = None,
                               pcb_file: str = None) -> str:
        """
        Generate a KiCad project file.
        
        Args:
            project_name: Name of the project
            schematic_file: Schematic filename
            pcb_file: PCB filename
            
        Returns:
            Project file content as JSON string
        """
        import json
        
        project = {
            "meta": {
                "filename": f"{project_name}.kicad_pro",
                "version": 1
            },
            "project": {
                "name": project_name
            },
            "schematic": {
                "file": schematic_file or f"{project_name}.kicad_sch"
            },
            "pcb": {
                "file": pcb_file or f"{project_name}.kicad_pcb"
            }
        }
        
        return json.dumps(project, indent=2)