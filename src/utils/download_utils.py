"""
Download Utilities - Fixed for Windows
Uses PowerShell for reliable downloads
"""

import os
import sys
import hashlib
import time
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Callable
import tempfile

from .logger import get_logger


class DownloadManager:
    """Manages file downloads with multiple fallback methods."""
    
    # CORRECT download URLs
    DOWNLOAD_URLS = {
        'ngspice': {
            '43': {
                'url': 'https://sourceforge.net/projects/ngspice/files/ng-spice-rework/43/ngspice-43_64.zip/download',
                'filename': 'ngspice-43_64.zip',
                'direct': 'https://downloads.sourceforge.net/project/ngspice/ng-spice-rework/43/ngspice-43_64.zip'
            },
            '42': {
                'url': 'https://sourceforge.net/projects/ngspice/files/ng-spice-rework/42/ngspice-42_64.zip/download',
                'filename': 'ngspice-42_64.zip',
                'direct': 'https://downloads.sourceforge.net/project/ngspice/ng-spice-rework/42/ngspice-42_64.zip'
            },
        },
        'gtkwave': {
            '3.3.118': {
                'url': 'https://sourceforge.net/projects/gtkwave/files/gtkwave-3.3.118-bin-win64/gtkwave-3.3.118-bin-win64.zip/download',
                'filename': 'gtkwave-3.3.118-bin-win64.zip',
            }
        }
    }
    
    def __init__(self):
        """Initialize the Download Manager."""
        self.logger = get_logger(__name__)
    
    def get_download_info(self, tool_name: str, version: str) -> Optional[dict]:
        """Get download information for a tool."""
        tool_downloads = self.DOWNLOAD_URLS.get(tool_name.lower(), {})
        return tool_downloads.get(version)
    
    def download(self, url: str, destination: Path,
                 tool_name: str = None, version: str = None,
                 show_progress: bool = True) -> bool:
        """Download a file using multiple methods."""
        
        # Get correct URL if available
        if tool_name and version:
            download_info = self.get_download_info(tool_name, version)
            if download_info:
                url = download_info.get('direct', download_info.get('url', url))
                self.logger.info(f"Using verified URL for {tool_name} {version}")
        
        self.logger.info(f"Downloading: {url}")
        print(f"   URL: {url[:70]}...")
        
        # Ensure parent directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Method 1: Try PowerShell (best for Windows)
        print(f"   Trying PowerShell download...")
        if self._download_with_powershell(url, destination):
            return True
        
        # Method 2: Try curl if available
        print(f"   Trying curl...")
        if self._download_with_curl(url, destination):
            return True
        
        # Method 3: Try Python requests
        print(f"   Trying Python requests...")
        if self._download_with_requests(url, destination, show_progress):
            return True
        
        # Method 4: Try urllib with special handling
        print(f"   Trying urllib...")
        if self._download_with_urllib(url, destination, show_progress):
            return True
        
        # All methods failed
        print(f"\n   ❌ All automatic download methods failed")
        return False
    
    def _download_with_powershell(self, url: str, destination: Path) -> bool:
        """Download using PowerShell (most reliable on Windows)."""
        try:
            # PowerShell command with progress
            ps_command = f'''
            $ProgressPreference = 'SilentlyContinue'
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $webClient = New-Object System.Net.WebClient
            $webClient.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            $webClient.DownloadFile("{url}", "{destination}")
            '''
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if destination.exists() and destination.stat().st_size > 0:
                print(f"   ✅ PowerShell download successful!")
                return True
            
            return False
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ PowerShell download timed out")
            return False
        except Exception as e:
            self.logger.debug(f"PowerShell download failed: {e}")
            return False
    
    def _download_with_curl(self, url: str, destination: Path) -> bool:
        """Download using curl (if available)."""
        if not shutil.which('curl'):
            return False
        
        try:
            result = subprocess.run(
                [
                    'curl', '-L', '-o', str(destination),
                    '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    '--connect-timeout', '30',
                    '--max-time', '300',
                    '-#',  # Progress bar
                    url
                ],
                capture_output=True,
                timeout=300
            )
            
            if destination.exists() and destination.stat().st_size > 0:
                print(f"   ✅ curl download successful!")
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"curl download failed: {e}")
            return False
    
    def _download_with_requests(self, url: str, destination: Path, 
                                 show_progress: bool) -> bool:
        """Download using requests library."""
        try:
            import requests
        except ImportError:
            return False
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            session = requests.Session()
            response = session.get(url, headers=headers, stream=True, 
                                   allow_redirects=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            start_time = time.time()
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if show_progress and total_size > 0:
                            self._print_progress(downloaded, total_size, start_time)
            
            if show_progress and total_size > 0:
                print()
            
            if destination.exists() and destination.stat().st_size > 0:
                print(f"   ✅ requests download successful!")
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"requests download failed: {e}")
            return False
    
    def _download_with_urllib(self, url: str, destination: Path,
                               show_progress: bool) -> bool:
        """Download using urllib."""
        try:
            import urllib.request
            import ssl
            
            # Create context
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # Create request
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*',
                }
            )
            
            with urllib.request.urlopen(request, context=ctx, timeout=60) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                
                with open(destination, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if show_progress and total_size > 0:
                            self._print_progress(downloaded, total_size, start_time)
            
            if show_progress and total_size > 0:
                print()
            
            if destination.exists() and destination.stat().st_size > 0:
                print(f"   ✅ urllib download successful!")
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"urllib download failed: {e}")
            return False
    
    def _print_progress(self, downloaded: int, total: int, start_time: float):
        """Print download progress bar."""
        percent = (downloaded / total) * 100
        bar_length = 40
        filled = int(bar_length * downloaded / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        elapsed = time.time() - start_time
        speed = downloaded / elapsed if elapsed > 0 else 0
        
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        speed_mb = speed / (1024 * 1024)
        
        sys.stdout.write(f'\r   [{bar}] {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB) {speed_mb:.1f} MB/s')
        sys.stdout.flush()
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum."""
        if len(expected_checksum) == 32:
            hash_func = hashlib.md5()
        elif len(expected_checksum) == 64:
            hash_func = hashlib.sha256()
        else:
            return True
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest().lower() == expected_checksum.lower()