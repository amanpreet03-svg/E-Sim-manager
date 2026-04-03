"""
Installer Module - Windows Compatible with Better Error Handling
"""

import os
import sys
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
import webbrowser

from utils.logger import get_logger
from utils.platform_utils import PlatformUtils
from utils.download_utils import DownloadManager


class Installer:
    """Handles the installation of external tools."""
    
    def __init__(self, tool_manager):
        """Initialize the Installer."""
        self.tool_manager = tool_manager
        self.logger = get_logger(__name__)
        self.platform = PlatformUtils.get_platform()
        self.download_manager = DownloadManager()
        
        # Temp directory for downloads
        self.temp_dir = Path(tempfile.gettempdir()) / "esim_tool_manager"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def install(self, tool_name: str, version: Optional[str] = None) -> bool:
        """Install a tool."""
        print(f"\n📦 Installing {tool_name}...")
        
        # Get tool configuration
        tool_config = self.tool_manager.registry.get_tool_config(tool_name)
        if not tool_config:
            print(f"❌ Unknown tool: {tool_name}")
            print(f"   Use 'available' to see available tools")
            return False
        
        # Determine version
        if not version:
            version = tool_config.get('versions', {}).get('latest', 'latest')
        
        print(f"   Version: {version}")
        
        # Check if we have a verified download URL
        download_info = self.download_manager.get_download_info(tool_name, version)
        
        if download_info:
            # Use verified download
            return self._install_with_verified_download(tool_name, version, download_info, tool_config)
        else:
            # Fallback to configured URLs
            urls = tool_config.get('urls', {})
            url = urls.get(self.platform)
            
            if not url:
                print(f"❌ No download available for {self.platform}")
                self._show_manual_install(tool_name, tool_config)
                return False
            
            if url.startswith(('sudo', 'brew', 'apt', 'choco', 'winget')):
                return self._install_via_package_manager(tool_name, url)
            
            url = url.replace('{version}', version)
            return self._install_via_download(tool_name, url, version, tool_config)
    
    def _install_with_verified_download(self, tool_name: str, version: str,
                                         download_info: dict, tool_config: dict) -> bool:
        """Install using verified download information."""
        url = download_info.get('direct', download_info.get('url'))
        filename = download_info.get('filename', f'{tool_name}-{version}.zip')
        
        download_path = self.temp_dir / filename
        install_path = self.tool_manager.tools_dir / tool_name
        
        try:
            # Download
            success = self.download_manager.download(
                url, 
                download_path,
                tool_name=tool_name,
                version=version,
                show_progress=True
            )
            
            if not success:
                # Offer manual download
                return self._manual_download_flow(tool_name, version, tool_config, download_path, install_path)
            
            # Extract
            return self._extract_and_install(download_path, install_path, tool_name)
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
        finally:
            # Cleanup
            if download_path.exists():
                try:
                    download_path.unlink()
                except:
                    pass
    
    def _manual_download_flow(self, tool_name: str, version: str, 
                               tool_config: dict, download_path: Path,
                               install_path: Path) -> bool:
        """Handle manual download flow."""
        download_urls = {
            'ngspice': f'https://sourceforge.net/projects/ngspice/files/ng-spice-rework/{version}/',
            'kicad': 'https://www.kicad.org/download/',
            'gtkwave': 'https://sourceforge.net/projects/gtkwave/files/',
            'iverilog': 'https://bleyer.org/icarus/',
        }
        
        download_page = download_urls.get(tool_name.lower(), tool_config.get('homepage', ''))
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  📥 MANUAL DOWNLOAD REQUIRED                                 ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Please download {tool_name} manually:                       
║                                                              ║
║  1. Download from: {download_page[:40]}
║                                                              ║
║  2. Look for Windows 64-bit version (usually .zip)          ║
║                                                              ║
║  3. After download, save the file here:                     ║
║     {str(download_path)[:50]}
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
        
        # Open browser
        user_input = input("   Open download page in browser? [Y/n]: ").strip().lower()
        if user_input != 'n':
            webbrowser.open(download_page)
        
        # Wait for download
        print(f"\n   ⏳ After downloading, press Enter to continue...")
        print(f"   (or type 'q' to cancel): ", end='')
        
        user_input = input().strip().lower()
        if user_input == 'q':
            print("   Cancelled")
            return False
        
        # Check for downloaded file
        if download_path.exists():
            print(f"   ✅ File found!")
            return self._extract_and_install(download_path, install_path, tool_name)
        
        # Check in Downloads folder
        downloads_folder = Path.home() / 'Downloads'
        possible_files = list(downloads_folder.glob(f'*{tool_name}*{version}*.zip')) + \
                        list(downloads_folder.glob(f'*{tool_name}*.zip'))
        
        if possible_files:
            print(f"\n   Found these files in Downloads:")
            for i, f in enumerate(possible_files[:5], 1):
                print(f"   {i}. {f.name}")
            
            choice = input(f"\n   Enter number to use (or Enter to cancel): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(possible_files):
                selected_file = possible_files[int(choice) - 1]
                shutil.copy(selected_file, download_path)
                return self._extract_and_install(download_path, install_path, tool_name)
        
        print(f"   ❌ Could not find downloaded file")
        print(f"   Please download to: {download_path}")
        return False
    
    def _extract_and_install(self, archive_path: Path, install_path: Path, 
                              tool_name: str) -> bool:
        """Extract archive and install."""
        try:
            print(f"   📂 Extracting...")
            
            install_path.mkdir(parents=True, exist_ok=True)
            
            if str(archive_path).endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(install_path)
            elif str(archive_path).endswith(('.tar.gz', '.tgz')):
                import tarfile
                with tarfile.open(archive_path, 'r:*') as tf:
                    tf.extractall(install_path)
            
            # Flatten if needed (single nested folder)
            self._flatten_directory(install_path)
            
            # Find and report executable
            exe_path = self._find_executable(install_path, tool_name)
            
            print(f"\n   ✅ {tool_name} installed successfully!")
            print(f"   📁 Location: {install_path}")
            if exe_path:
                print(f"   🔧 Executable: {exe_path}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Extraction failed: {e}")
            return False
    
    def _flatten_directory(self, path: Path):
        """Flatten single nested directory."""
        try:
            contents = list(path.iterdir())
            if len(contents) == 1 and contents[0].is_dir():
                nested_dir = contents[0]
                for item in nested_dir.iterdir():
                    target = path / item.name
                    if not target.exists():
                        shutil.move(str(item), str(target))
                # Remove empty nested directory
                if not any(nested_dir.iterdir()):
                    nested_dir.rmdir()
        except Exception as e:
            self.logger.debug(f"Flatten failed: {e}")
    
    def _find_executable(self, install_path: Path, tool_name: str) -> Optional[Path]:
        """Find the main executable."""
        exe_names = [
            f'{tool_name}.exe',
            f'{tool_name}64.exe',
            'bin/ngspice.exe',
            'Spice64/bin/ngspice.exe',
        ]
        
        for exe_name in exe_names:
            exe_path = install_path / exe_name
            if exe_path.exists():
                return exe_path
        
        # Search for any .exe
        for exe in install_path.rglob('*.exe'):
            if tool_name.lower() in exe.name.lower():
                return exe
        
        return None
    
    def _install_via_package_manager(self, tool_name: str, command: str) -> bool:
        """Install using package manager."""
        print(f"   Using package manager: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"   ✅ {tool_name} installed successfully!")
                return True
            else:
                print(f"   ❌ Installation failed: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def _install_via_download(self, tool_name: str, url: str, version: str,
                               tool_config: dict) -> bool:
        """Install by downloading."""
        # Determine filename
        if '.zip' in url:
            ext = '.zip'
        elif '.tar.gz' in url:
            ext = '.tar.gz'
        elif '.exe' in url:
            ext = '.exe'
        else:
            ext = '.zip'
        
        download_path = self.temp_dir / f"{tool_name}-{version}{ext}"
        install_path = self.tool_manager.tools_dir / tool_name
        
        try:
            success = self.download_manager.download(
                url, download_path,
                tool_name=tool_name, version=version,
                show_progress=True
            )
            
            if not success:
                return self._manual_download_flow(tool_name, version, tool_config, 
                                                   download_path, install_path)
            
            if ext in ['.zip', '.tar.gz']:
                return self._extract_and_install(download_path, install_path, tool_name)
            elif ext == '.exe':
                print(f"   Running installer...")
                os.startfile(str(download_path))
                input("   Press Enter after installation completes: ")
                return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        finally:
            if download_path.exists():
                try:
                    download_path.unlink()
                except:
                    pass
        
        return False
    
    def _show_manual_install(self, tool_name: str, tool_config: dict):
        """Show manual installation instructions."""
        homepage = tool_config.get('homepage', '')
        print(f"\n   💡 Visit {homepage} for manual installation")
    
    def uninstall(self, tool_name: str) -> bool:
        """Uninstall a tool."""
        print(f"\n🗑️  Uninstalling {tool_name}...")
        
        tool_info = self.tool_manager.installed_tools.get(tool_name)
        if not tool_info:
            print(f"❌ {tool_name} is not installed")
            return False
        
        install_path = Path(tool_info.install_path)
        
        try:
            if install_path.exists():
                shutil.rmtree(install_path)
            print(f"✅ {tool_name} uninstalled!")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def verify_installation(self, tool_name: str) -> bool:
        """Verify tool installation."""
        install_path = self.tool_manager.tools_dir / tool_name
        if not install_path.exists():
            return False
        
        exe_path = self._find_executable(install_path, tool_name)
        return exe_path is not None and exe_path.exists()