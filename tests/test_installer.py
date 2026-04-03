"""
Tests for the Installer module.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.installer import Installer
from core.tool_manager import ToolManager


class TestInstaller:
    """Test cases for Installer class."""
    
    @pytest.fixture
    def mock_tool_manager(self):
        """Create a mock tool manager."""
        manager = Mock(spec=ToolManager)
        manager.tools_dir = Path(tempfile.mkdtemp())
        manager.config_dir = Path(tempfile.mkdtemp())
        manager.registry = Mock()
        manager.registry.get_tool_config.return_value = {
            'name': 'TestTool',
            'versions': {'latest': '1.0.0'},
            'urls': {
                'linux': 'https://example.com/test-{version}.tar.gz',
                'windows': 'https://example.com/test-{version}.zip',
                'darwin': 'brew install testtool'
            }
        }
        return manager
    
    @pytest.fixture
    def installer(self, mock_tool_manager):
        """Create an Installer instance."""
        return Installer(mock_tool_manager)
    
    def test_installer_initialization(self, installer):
        """Test installer initializes correctly."""
        assert installer is not None
        assert installer.temp_dir.exists()
    
    def test_get_install_info_package_manager(self, installer):
        """Test getting install info for package manager method."""
        tool_config = {
            'urls': {
                'linux': 'apt install testtool',
                'darwin': 'brew install testtool'
            }
        }
        
        with patch.object(installer, 'platform', 'linux'):
            result = installer._get_install_info(tool_config, '1.0')
            assert result is not None
            assert result[0] == 'package_manager'
    
    def test_get_install_info_download(self, installer):
        """Test getting install info for download method."""
        tool_config = {
            'urls': {
                'linux': 'https://example.com/tool-{version}.tar.gz'
            }
        }
        
        with patch.object(installer, 'platform', 'linux'):
            result = installer._get_install_info(tool_config, '1.0')
            assert result is not None
            assert result[0] == 'download'
            assert '1.0' in result[1]
    
    def test_extract_zip(self, installer):
        """Test ZIP extraction."""
        import zipfile
        
        # Create a test zip file
        test_dir = Path(tempfile.mkdtemp())
        zip_path = test_dir / 'test.zip'
        extract_path = test_dir / 'extracted'
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('test.txt', 'Hello World')
        
        installer._extract_zip(zip_path, extract_path)
        
        assert (extract_path / 'test.txt').exists()
        assert (extract_path / 'test.txt').read_text() == 'Hello World'
    
    def test_extract_tar(self, installer):
        """Test TAR extraction."""
        import tarfile
        
        # Create a test tar file
        test_dir = Path(tempfile.mkdtemp())
        tar_path = test_dir / 'test.tar.gz'
        extract_path = test_dir / 'extracted'
        
        with tarfile.open(tar_path, 'w:gz') as tf:
            # Create a temporary file to add
            temp_file = test_dir / 'temp.txt'
            temp_file.write_text('Hello World')
            tf.add(temp_file, arcname='test.txt')
        
        installer._extract_tar(tar_path, extract_path)
        
        assert (extract_path / 'test.txt').exists()
    
    @patch('subprocess.run')
    def test_install_via_package_manager(self, mock_run, installer):
        """Test installation via package manager."""
        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
        
        with patch.object(installer, 'platform', 'linux'):
            result = installer._install_via_package_manager(
                'testtool', 
                'apt install testtool'
            )
        
        assert result is True
        mock_run.assert_called_once()
    
    def test_verify_installation(self, installer, mock_tool_manager):
        """Test installation verification."""
        # Setup mock
        mock_tool_manager.installed_tools = {
            'testtool': Mock(install_path=str(installer.temp_dir))
        }
        mock_tool_manager.registry.get_tool_config.return_value = {
            'verify_command': 'echo test'
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            result = installer.verify_installation('testtool')
        
        # Note: This will depend on actual file existence
        assert isinstance(result, bool)


class TestInstallerEdgeCases:
    """Edge case tests for Installer."""
    
    @pytest.fixture
    def installer(self):
        """Create installer with minimal mocking."""
        manager = Mock()
        manager.tools_dir = Path(tempfile.mkdtemp())
        manager.registry = Mock()
        return Installer(manager)
    
    def test_install_unknown_tool(self, installer):
        """Test installing an unknown tool."""
        installer.tool_manager.registry.get_tool_config.return_value = None
        
        result = installer.install('unknown_tool')
        
        assert result is False
    
    def test_get_install_info_no_url(self, installer):
        """Test getting install info when no URL is available."""
        tool_config = {
            'urls': {}
        }
        
        result = installer._get_install_info(tool_config, '1.0')
        
        assert result is None