"""
Ngspice Tool Module
Implementation for Ngspice circuit simulator.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from .base_tool import BaseTool, ToolMetadata, VersionInfo, InstallMethod
from utils.platform_utils import PlatformUtils


class NgspiceTool(BaseTool):
    """
    Ngspice tool implementation.
    
    Ngspice is an open-source spice simulator for electronic circuits.
    It is the primary simulation engine used by eSim.
    """
    
    # Version download URLs
    DOWNLOAD_URLS = {
        'windows': 'https://sourceforge.net/projects/ngspice/files/ng-spice-rework/{version}/ngspice-{version}_64.zip/download',
        'linux': 'https://sourceforge.net/projects/ngspice/files/ng-spice-rework/{version}/ngspice-{version}.tar.gz/download',
        'darwin': None  # Use Homebrew
    }
    
    # Package manager commands
    PACKAGE_COMMANDS = {
        'linux': {
            'apt': 'sudo apt-get install -y ngspice',
            'dnf': 'sudo dnf install -y ngspice',
            'yum': 'sudo yum install -y ngspice',
            'pacman': 'sudo pacman -S --noconfirm ngspice',
            'zypper': 'sudo zypper install -y ngspice'
        },
        'darwin': {
            'homebrew': 'brew install ngspice'
        },
        'windows': {
            'chocolatey': 'choco install ngspice -y',
            'scoop': 'scoop install ngspice'
        }
    }
    
    def __init__(self):
        """Initialize Ngspice tool."""
        super().__init__()
        
        self._metadata = ToolMetadata(
            name='ngspice',
            display_name='Ngspice',
            description='Open source spice simulator for electronic circuit simulation',
            homepage='http://ngspice.sourceforge.net/',
            license='BSD-3-Clause',
            category='Simulation',
            maintainer='Ngspice Team',
            tags=['spice', 'simulation', 'circuit', 'analog', 'mixed-signal']
        )
        
        self._version_info = VersionInfo(
            latest='43',
            stable='42',
            available=['43', '42', '41', '40', '39', '38', '37'],
            min_supported='37'
        )
    
    @property
    def tool_id(self) -> str:
        """Get tool ID."""
        return 'ngspice'
    
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
            'linux': ['libreadline', 'libpthread', 'libfftw3', 'libxaw'],
            'darwin': ['readline', 'fftw'],
            'windows': []
        }
        return deps.get(self.platform, [])
    
    def get_download_url(self, version: str) -> Optional[str]:
        """Get download URL for specific version."""
        url_template = self.DOWNLOAD_URLS.get(self.platform)
        if url_template:
            return url_template.format(version=version)
        return None
    
    def get_install_method(self) -> InstallMethod:
        """Get preferred installation method."""
        if self.platform == 'darwin':
            return InstallMethod.PACKAGE_MANAGER
        elif self.platform == 'linux':
            # Prefer package manager if available
            pkg_manager = PlatformUtils.get_package_manager()
            if pkg_manager in self.PACKAGE_COMMANDS.get('linux', {}):
                return InstallMethod.PACKAGE_MANAGER
            return InstallMethod.SOURCE_BUILD
        else:  # Windows
            return InstallMethod.DOWNLOAD_EXTRACT
    
    def get_package_manager_command(self) -> Optional[str]:
        """Get package manager installation command."""
        pkg_manager = PlatformUtils.get_package_manager()
        platform_commands = self.PACKAGE_COMMANDS.get(self.platform, {})
        return platform_commands.get(pkg_manager)
    
    def _get_main_command(self) -> str:
        """Get main executable command."""
        return 'ngspice'
    
    def _get_version_command(self) -> List[str]:
        """Get version check command."""
        return ['ngspice', '--version']
    
    def _parse_version_output(self, output: str) -> Optional[str]:
        """Parse version from ngspice output."""
        # Ngspice version output: "ngspice-43" or "ngspice 43"
        match = re.search(r'ngspice[- ](\d+)', output, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for Ngspice."""
        if not self._install_path:
            return {}
        
        return {
            'SPICE_LIB_DIR': str(self._install_path / 'share' / 'ngspice'),
            'SPICE_SCRIPTS': str(self._install_path / 'share' / 'ngspice' / 'scripts'),
            'NGSPICE_HOME': str(self._install_path)
        }
    
    def get_config_files(self) -> Dict[str, str]:
        """Get Ngspice configuration files."""
        spinit_content = """* Ngspice initialization file
* Created by eSim Tool Manager

* Set output format to ASCII
set filetype=ascii

* Enable PS output behavior
set ngbehavior=ps

* Set default options
set numdgt=7
set rndseed=1

* Include device libraries if available
* .include {SPICE_LIB_DIR}/spinit
"""
        
        return {
            'spinit': spinit_content,
            '.spiceinit': spinit_content
        }
    
    def post_install_hook(self) -> bool:
        """Post-installation hook for Ngspice."""
        self.logger.info("Running Ngspice post-install configuration...")
        
        # Verify installation
        if not self.verify_installation():
            self.logger.error("Ngspice installation verification failed")
            return False
        
        # Create spice library directories if needed
        if self._install_path:
            lib_dirs = [
                self._install_path / 'share' / 'ngspice' / 'scripts',
                self._install_path / 'share' / 'ngspice' / 'lib'
            ]
            for lib_dir in lib_dirs:
                lib_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Ngspice post-install completed successfully")
        return True
    
    def get_source_build_commands(self) -> List[str]:
        """Get commands to build Ngspice from source."""
        return [
            './configure --with-x --enable-xspice --enable-cider --with-readline=yes',
            'make -j$(nproc)',
            'sudo make install'
        ]
    
    def get_binary_paths(self) -> List[Path]:
        """Get paths containing Ngspice binaries."""
        paths = []
        
        if self._install_path:
            # Check common locations
            candidates = [
                self._install_path / 'bin',
                self._install_path / 'Spice64' / 'bin',  # Windows
                self._install_path
            ]
            for candidate in candidates:
                if candidate.exists():
                    paths.append(candidate)
        
        return paths


class NgspiceConfig:
    """
    Ngspice-specific configuration helper.
    """
    
    DEFAULT_OPTIONS = {
        'filetype': 'ascii',
        'ngbehavior': 'ps',
        'numdgt': '7',
        'rndseed': '1'
    }
    
    @staticmethod
    def generate_spinit(options: Optional[Dict] = None, 
                        include_libs: Optional[List[str]] = None) -> str:
        """
        Generate spinit configuration content.
        
        Args:
            options: Custom options to set
            include_libs: List of library files to include
            
        Returns:
            Configuration file content
        """
        opts = {**NgspiceConfig.DEFAULT_OPTIONS, **(options or {})}
        
        lines = [
            "* Ngspice initialization file",
            "* Generated by eSim Tool Manager",
            ""
        ]
        
        # Add set commands
        for key, value in opts.items():
            lines.append(f"set {key}={value}")
        
        lines.append("")
        
        # Add includes
        if include_libs:
            lines.append("* Library includes")
            for lib in include_libs:
                lines.append(f".include {lib}")
        
        return "\n".join(lines)
    
    @staticmethod
    def get_model_libraries() -> Dict[str, str]:
        """
        Get standard model library paths.
        
        Returns:
            Dictionary mapping library names to paths
        """
        return {
            'cmos': 'cmos.lib',
            'bipolar': 'bipolar.lib',
            'diode': 'diode.lib',
            'jfet': 'jfet.lib',
            'mosfet': 'mosfet.lib'
        }