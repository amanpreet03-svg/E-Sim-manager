#!/usr/bin/env python3
"""
eSim Automated Tool Manager - Main Entry Point
Windows Compatible Version
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize colorama for Windows console colors
try:
    import colorama
    colorama.init()
except ImportError:
    pass

from ui.cli import CLI
from core.tool_manager import ToolManager
from utils.logger import setup_logger
import argparse


def main():
    """Main entry point for eSim Tool Manager."""
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="eSim Automated Tool Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                      # Start interactive CLI
  python main.py install ngspice      # Install Ngspice
  python main.py list --available     # List available tools
  python main.py check-deps           # Check dependencies
        """
    )
    
    parser.add_argument('--version', '-v', action='version', version='eSim Tool Manager v1.1.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install a tool')
    install_parser.add_argument('tool', help='Tool name')
    install_parser.add_argument('--version', dest='tool_version', help='Specific version')
    install_parser.add_argument('--force', '-f', action='store_true', help='Force reinstall')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a tool')
    uninstall_parser.add_argument('tool', help='Tool name')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update tools')
    update_parser.add_argument('tool', nargs='?', help='Tool name (optional)')
    update_parser.add_argument('--all', '-a', action='store_true', help='Update all')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tools')
    list_parser.add_argument('--installed', '-i', action='store_true')
    list_parser.add_argument('--available', '-a', action='store_true')
    
    # Check deps command
    subparsers.add_parser('check-deps', help='Check dependencies')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show tool info')
    info_parser.add_argument('tool', help='Tool name')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger()
    
    # Initialize tool manager
    try:
        tool_manager = ToolManager()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return 1
    
    # Create CLI
    cli = CLI(tool_manager)
    
    # If no command, start interactive mode
    if not args.command:
        cli.run()
        return 0
    
    # Execute command
    return cli.execute_command(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)