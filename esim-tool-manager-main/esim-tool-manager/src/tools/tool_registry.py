import json
from pathlib import Path
from typing import Dict, List, Optional

from utils.logger import get_logger


class ToolRegistry:
    """Central registry containing information about all supported tools."""
    
    # Built-in tool definitions with Windows support
    BUILTIN_TOOLS = {
        "ngspice": {
            "name": "Ngspice",
            "description": "Open source spice simulator for electronic circuit simulation",
            "homepage": "http://ngspice.sourceforge.net/",
            "category": "Simulation",
            "versions": {
                "latest": "43",
                "stable": "42",
                "available": ["43", "42", "41", "40"]
            },
            "urls": {
                "windows": "https://sourceforge.net/projects/ngspice/files/ng-spice-rework/{version}/ngspice-{version}_64.zip/download",
                "linux": "https://sourceforge.net/projects/ngspice/files/ng-spice-rework/{version}/ngspice-{version}.tar.gz/download",
                "darwin": "brew install ngspice"
            },
            "windows_installer": "https://sourceforge.net/projects/ngspice/files/ng-spice-rework/{version}/ngspice-{version}_64.zip/download",
            "dependencies": [],  # No dependencies on Windows - self-contained
            "dependencies_linux": ["libreadline", "libpthread"],
            "verify_command": "ngspice --version",
            "windows_executable": "ngspice.exe",
            "install_type": "zip_extract"
        },
        "kicad": {
            "name": "KiCad",
            "description": "Electronic Design Automation suite for schematic and PCB design",
            "homepage": "https://www.kicad.org/",
            "category": "EDA",
            "versions": {
                "latest": "8.0.5",
                "stable": "8.0.5",
                "available": ["8.0.5", "8.0.4", "7.0.11"]
            },
            "urls": {
                "windows": "https://downloads.kicad.org/kicad/windows/explore/stable/download/kicad-{version}-x86_64.exe",
                "linux": "sudo apt install kicad",
                "darwin": "brew install --cask kicad"
            },
            "dependencies": [],
            "verify_command": "kicad-cli --version",
            "windows_executable": "kicad.exe",
            "install_type": "installer"
        },
        "verilator": {
            "name": "Verilator",
            "description": "Fast Verilog/SystemVerilog simulator",
            "homepage": "https://www.veripool.org/verilator/",
            "category": "Simulation",
            "versions": {
                "latest": "5.024",
                "stable": "5.022",
                "available": ["5.024", "5.022", "5.020"]
            },
            "urls": {
                "windows": "https://github.com/verilator/verilator/releases/download/v{version}/verilator-{version}-win64.zip",
                "linux": "sudo apt-get install -y verilator",
                "darwin": "brew install verilator"
            },
            "dependencies": [],
            "verify_command": "verilator --version",
            "install_type": "zip_extract"
        },
        "gtkwave": {
            "name": "GTKWave",
            "description": "Waveform viewer for simulation results",
            "homepage": "http://gtkwave.sourceforge.net/",
            "category": "Visualization",
            "versions": {
                "latest": "3.3.118",
                "stable": "3.3.118",
                "available": ["3.3.118", "3.3.115"]
            },
            "urls": {
                "windows": "https://sourceforge.net/projects/gtkwave/files/gtkwave-{version}-bin-win64/gtkwave-{version}-bin-win64.zip/download",
                "linux": "sudo apt-get install -y gtkwave",
                "darwin": "brew install gtkwave"
            },
            "dependencies": [],
            "verify_command": "gtkwave --version",
            "install_type": "zip_extract"
        },
        "iverilog": {
            "name": "Icarus Verilog",
            "description": "Verilog simulation and synthesis tool",
            "homepage": "http://iverilog.icarus.com/",
            "category": "Simulation",
            "versions": {
                "latest": "12.0",
                "stable": "12.0",
                "available": ["12.0", "11.0"]
            },
            "urls": {
                "windows": "https://bleyer.org/icarus/iverilog-v{version}-x64-setup.exe",
                "linux": "sudo apt-get install -y iverilog",
                "darwin": "brew install icarus-verilog"
            },
            "dependencies": [],
            "verify_command": "iverilog -V",
            "install_type": "installer"
        }
    }
    
    def __init__(self, custom_registry_path: Optional[Path] = None):
        """Initialize the Tool Registry."""
        self.logger = get_logger(__name__)
        self.tools = dict(self.BUILTIN_TOOLS)
        
        if custom_registry_path and custom_registry_path.exists():
            self._load_custom_registry(custom_registry_path)
    
    def _load_custom_registry(self, path: Path):
        """Load custom tool definitions from file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                custom_tools = json.load(f)
                self.tools.update(custom_tools)
                self.logger.info(f"Loaded {len(custom_tools)} custom tool definitions")
        except Exception as e:
            self.logger.error(f"Failed to load custom registry: {e}")
    
    def get_tool_config(self, tool_name: str) -> Optional[Dict]:
        """Get configuration for a specific tool."""
        return self.tools.get(tool_name.lower())
    
    def get_all_tools(self) -> List[Dict]:
        """Get list of all available tools."""
        result = []
        for tool_id, config in self.tools.items():
            result.append({
                'id': tool_id,
                'name': config.get('name', tool_id),
                'description': config.get('description', ''),
                'category': config.get('category', 'General'),
                'latest_version': config.get('versions', {}).get('latest', 'unknown'),
                'homepage': config.get('homepage', '')
            })
        return result
    
    def get_tools_by_category(self, category: str) -> List[Dict]:
        """Get tools filtered by category."""
        return [
            tool for tool in self.get_all_tools()
            if tool.get('category', '').lower() == category.lower()
        ]
    
    def tool_exists(self, tool_name: str) -> bool:
        """Check if a tool is in the registry."""
        return tool_name.lower() in self.tools
    
    def get_tool_versions(self, tool_name: str) -> List[str]:
        """Get available versions for a tool."""
        config = self.get_tool_config(tool_name)
        if not config:
            return []
        versions = config.get('versions', {})
        return versions.get('available', [versions.get('latest', 'unknown')])
    
    def search_tools(self, query: str) -> List[Dict]:
        """Search tools by name or description."""
        query_lower = query.lower()
        return [
            tool for tool in self.get_all_tools()
            if query_lower in tool['name'].lower() or query_lower in tool['description'].lower()
        ]