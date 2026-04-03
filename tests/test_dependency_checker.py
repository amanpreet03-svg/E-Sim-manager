"""
Tests for the Dependency Checker module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.dependency_checker import DependencyChecker


class TestDependencyChecker:
    """Test cases for DependencyChecker class."""
    
    @pytest.fixture
    def mock_tool_manager(self):
        """Create a mock tool manager."""
        manager = Mock()
        manager.registry = Mock()
        return manager
    
    @pytest.fixture
    def checker(self, mock_tool_manager):
        """Create a DependencyChecker instance."""
        return DependencyChecker(mock_tool_manager)
    
    def test_check_dependency_known(self, checker):
        """Test checking a known dependency."""
        with patch.object(checker, '_run_check_command', return_value=True):
            result = checker.check_dependency('python3')
        
        assert isinstance(result, bool)
    
    def test_check_dependency_unknown(self, checker):
        """Test checking an unknown dependency."""
        with patch.object(checker, '_check_command_exists', return_value=False):
            result = checker.check_dependency('unknown_dependency_xyz')
        
        assert result is False
    
    @patch('shutil.which')
    def test_check_command_exists_true(self, mock_which, checker):
        """Test command existence check - command exists."""
        mock_which.return_value = '/usr/bin/python3'
        
        result = checker._check_command_exists('python3')
        
        assert result is True
    
    @patch('shutil.which')
    def test_check_command_exists_false(self, mock_which, checker):
        """Test command existence check - command doesn't exist."""
        mock_which.return_value = None
        
        result = checker._check_command_exists('nonexistent')
        
        assert result is False
    
    @patch('subprocess.run')
    def test_run_check_command_success(self, mock_run, checker):
        """Test running check command successfully."""
        mock_run.return_value = Mock(returncode=0)
        
        result = checker._run_check_command(['python3', '--version'])
        
        assert result is True
    
    @patch('subprocess.run')
    def test_run_check_command_failure(self, mock_run, checker):
        """Test running check command with failure."""
        mock_run.return_value = Mock(returncode=1)
        
        result = checker._run_check_command(['nonexistent', '--version'])
        
        assert result is False
    
    @patch('subprocess.run')
    def test_run_check_command_exception(self, mock_run, checker):
        """Test running check command with exception."""
        mock_run.side_effect = FileNotFoundError()
        
        result = checker._run_check_command(['nonexistent'])
        
        assert result is False
    
    def test_check_tool_dependencies(self, checker, mock_tool_manager):
        """Test checking dependencies for a tool."""
        mock_tool_manager.registry.get_tool_config.return_value = {
            'dependencies': ['python3', 'gcc']
        }
        
        with patch.object(checker, 'check_dependency', side_effect=[True, True]):
            all_ok, missing = checker.check_tool_dependencies('testtool')
        
        assert all_ok is True
        assert missing == []
    
    def test_check_tool_dependencies_missing(self, checker, mock_tool_manager):
        """Test checking dependencies with missing deps."""
        mock_tool_manager.registry.get_tool_config.return_value = {
            'dependencies': ['python3', 'missing_dep']
        }
        
        with patch.object(checker, 'check_dependency', side_effect=[True, False]):
            all_ok, missing = checker.check_tool_dependencies('testtool')
        
        assert all_ok is False
        assert 'missing_dep' in missing
    
    def test_check_system_dependencies(self, checker):
        """Test checking all system dependencies."""
        with patch.object(checker, 'check_dependency', return_value=True):
            result = checker.check_system_dependencies()
        
        assert 'installed' in result
        assert 'missing' in result
    
    def test_get_dependency_info(self, checker):
        """Test getting dependency information."""
        with patch.object(checker, 'check_dependency', return_value=True):
            info = checker.get_dependency_info('python3')
        
        assert info['name'] == 'python3'
        assert 'installed' in info
        assert 'install_command' in info
    
    @patch('subprocess.run')
    def test_install_dependency_success(self, mock_run, checker):
        """Test successful dependency installation."""
        mock_run.return_value = Mock(returncode=0)
        
        with patch.object(checker, 'platform', 'linux'):
            result = checker.install_dependency('git')
        
        assert result is True
    
    @patch('subprocess.run')
    def test_install_dependency_failure(self, mock_run, checker):
        """Test failed dependency installation."""
        mock_run.return_value = Mock(returncode=1, stderr='Error')
        
        with patch.object(checker, 'platform', 'linux'):
            result = checker.install_dependency('git')
        
        assert result is False
    
    def test_install_unknown_dependency(self, checker):
        """Test installing unknown dependency."""
        result = checker.install_dependency('unknown_dep_xyz_123')
        
        assert result is False
    
    @patch('subprocess.run')
    def test_get_version(self, mock_run, checker):
        """Test getting dependency version."""
        mock_run.return_value = Mock(
            returncode=0, 
            stdout='Python 3.10.0'
        )
        
        version = checker.get_version('python3')
        
        assert version == '3.10.0'
    
    def test_get_version_unknown_dep(self, checker):
        """Test getting version for unknown dependency."""
        version = checker.get_version('unknown_dep')
        
        assert version is None


class TestDependencyCheckerPlatformSpecific:
    """Platform-specific tests for DependencyChecker."""
    
    @pytest.fixture
    def checker(self):
        """Create checker with minimal mocking."""
        manager = Mock()
        manager.registry = Mock()
        return DependencyChecker(manager)
    
    @patch('subprocess.run')
    def test_check_library_linux(self, mock_run, checker):
        """Test library checking on Linux."""
        mock_run.return_value = Mock(returncode=0)
        
        with patch.object(checker, 'platform', 'linux'):
            result = checker._check_library_exists('readline')
        
        assert isinstance(result, bool)
    
    @patch('subprocess.run')
    def test_check_library_darwin(self, mock_run, checker):
        """Test library checking on macOS."""
        mock_run.return_value = Mock(returncode=0)
        
        with patch.object(checker, 'platform', 'darwin'):
            result = checker._check_library_exists('readline')
        
        assert isinstance(result, bool)