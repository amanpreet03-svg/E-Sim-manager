"""
CLI Module - Windows Compatible
"""

import sys
import cmd
from typing import Optional

from core.tool_manager import ToolManager, ToolStatus
from utils.logger import get_logger
from utils.platform_utils import PlatformUtils

# Try to import tabulate, fall back to simple formatting
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def format_table(data, headers):
    """Format data as a table."""
    if HAS_TABULATE:
        return tabulate(data, headers=headers, tablefmt="simple")
    else:
        # Simple fallback
        result = "  ".join(headers) + "\n"
        result += "-" * 60 + "\n"
        for row in data:
            result += "  ".join(str(cell) for cell in row) + "\n"
        return result


class CLI(cmd.Cmd):
    """Interactive CLI for eSim Tool Manager."""
    
    intro = """
╔═══════════════════════════════════════════════════════════════╗
║           eSim Automated Tool Manager v1.1.0                  ║
║                     Windows Compatible                        ║
║                                                               ║
║  Type 'help' for available commands or 'quit' to exit.       ║
╚═══════════════════════════════════════════════════════════════╝
    """
    prompt = "(esim-tools) "
    
    def __init__(self, tool_manager: ToolManager):
        """Initialize CLI."""
        super().__init__()
        self.tool_manager = tool_manager
        self.logger = get_logger(__name__)
    
    def run(self):
        """Start the interactive CLI."""
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
    
    def execute_command(self, args) -> int:
        """Execute a command from parsed arguments."""
        if args.command == 'install':
            success = self.tool_manager.install_tool(
                args.tool, 
                version=getattr(args, 'version', None),
                force=getattr(args, 'force', False)
            )
            return 0 if success else 1
        elif args.command == 'uninstall':
            success = self.tool_manager.uninstall_tool(args.tool)
            return 0 if success else 1
        elif args.command == 'update':
            if getattr(args, 'all', False):
                self.tool_manager.update_all_tools()
            elif hasattr(args, 'tool') and args.tool:
                self.tool_manager.update_tool(args.tool)
            return 0
        elif args.command == 'list':
            if getattr(args, 'installed', False):
                self.do_installed('')
            else:
                self.do_available('')
            return 0
        elif args.command == 'check-deps':
            self.do_check_deps('')
            return 0
        elif args.command == 'info':
            self.do_info(args.tool)
            return 0
        return 0
    
    # ==================== Commands ====================
    
    def do_help(self, arg: str):
        """Show help information."""
        if arg:
            # Show help for specific command
            super().do_help(arg)
        else:
            print("""
📖 AVAILABLE COMMANDS:
═══════════════════════════════════════════════════════════════

  TOOL MANAGEMENT:
  ─────────────────
  available           - List all available tools
  installed           - List installed tools
  install <tool>      - Install a tool (e.g., install ngspice)
  uninstall <tool>    - Uninstall a tool
  update <tool>       - Update a specific tool
  update all          - Update all installed tools
  info <tool>         - Show detailed tool information

  SYSTEM:
  ───────
  check_deps          - Check system dependencies
  fix_deps            - Attempt to fix missing dependencies
  check_updates       - Check for available updates
  platform            - Show platform information
  logs                - View recent activity logs

  OTHER:
  ──────
  help                - Show this help message
  quit / exit         - Exit the tool manager

═══════════════════════════════════════════════════════════════
""")
    
    def do_install(self, arg: str):
        """Install a tool: install <tool_name> [version]"""
        parts = arg.split()
        if not parts:
            print("❌ Usage: install <tool_name> [version]")
            print("   Example: install ngspice")
            print("   Example: install ngspice 42")
            return
        
        tool_name = parts[0].lower()
        version = parts[1] if len(parts) > 1 else None
        
        self.tool_manager.install_tool(tool_name, version)
    
    def do_uninstall(self, arg: str):
        """Uninstall a tool: uninstall <tool_name>"""
        if not arg:
            print("❌ Usage: uninstall <tool_name>")
            return
        
        tool_name = arg.strip().lower()
        
        confirm = input(f"⚠️  Uninstall {tool_name}? [y/N]: ")
        if confirm.lower() == 'y':
            self.tool_manager.uninstall_tool(tool_name)
        else:
            print("   Cancelled")
    
    def do_update(self, arg: str):
        """Update tools: update [tool_name] or update all"""
        if not arg or arg.lower() == 'all':
            print("\n🔄 Updating all tools...")
            results = self.tool_manager.update_all_tools()
            for tool, success in results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {tool}")
        else:
            self.tool_manager.update_tool(arg.strip().lower())
    
    def do_check_updates(self, arg: str):
        """Check for available updates."""
        print("\n🔍 Checking for updates...")
        updates = self.tool_manager.check_updates()
        
        has_updates = False
        for tool, new_version in updates.items():
            if new_version:
                has_updates = True
                current = self.tool_manager.installed_tools[tool].version
                print(f"   📦 {tool}: {current} → {new_version}")
        
        if not has_updates:
            print("   ✅ All tools are up to date!")
    
    def do_installed(self, arg: str):
        """List installed tools."""
        tools = self.tool_manager.list_installed_tools()
        
        if not tools:
            print("\n📭 No tools installed yet.")
            print("   Use 'available' to see tools you can install.")
            return
        
        print("\n📦 INSTALLED TOOLS:")
        print("─" * 60)
        
        table_data = []
        for tool in tools:
            status_icon = "✅" if tool.status == ToolStatus.INSTALLED else "⚠️"
            table_data.append([
                status_icon,
                tool.name,
                tool.version,
                tool.install_date[:10] if tool.install_date else "N/A"
            ])
        
        print(format_table(table_data, ["", "Tool", "Version", "Installed"]))
        print()
    
    def do_available(self, arg: str):
        """List available tools."""
        tools = self.tool_manager.list_available_tools()
        
        print("\n📋 AVAILABLE TOOLS:")
        print("─" * 70)
        
        table_data = []
        for tool in tools:
            installed = "✅" if tool['id'] in self.tool_manager.installed_tools else ""
            desc = tool['description'][:40] + "..." if len(tool['description']) > 40 else tool['description']
            table_data.append([
                installed,
                tool['name'],
                tool['latest_version'],
                desc
            ])
        
        print(format_table(table_data, ["", "Tool", "Version", "Description"]))
        print("\n💡 Use 'install <tool_name>' to install a tool\n")
    
    def do_info(self, arg: str):
        """Show tool information: info <tool_name>"""
        if not arg:
            print("❌ Usage: info <tool_name>")
            return
        
        tool_name = arg.strip().lower()
        info = self.tool_manager.get_tool_info(tool_name)
        
        if not info:
            print(f"❌ Tool not found: {tool_name}")
            return
        
        tool_config = self.tool_manager.registry.get_tool_config(tool_name)
        
        print(f"""
╔{'═'*58}╗
║  📦 {info.name.upper():<53}║
╠{'═'*58}╣
║  Description: {(info.description or 'N/A')[:42]:<43}║
║  Status: {info.status.value:<48}║
║  Installed Version: {info.version or 'Not installed':<37}║
║  Latest Version: {(info.latest_version or tool_config.get('versions', {}).get('latest', 'N/A')):<40}║
║  Install Path: {(info.install_path[:40] + '...' if len(info.install_path) > 40 else info.install_path) or 'N/A':<43}║
║  Homepage: {tool_config.get('homepage', 'N/A')[:46]:<47}║
╚{'═'*58}╝
""")
    
    def do_check_deps(self, arg: str):
        """Check system dependencies."""
        print("\n🔍 Checking system dependencies...")
        self.tool_manager.dependency_checker.print_status()
    
    def do_fix_deps(self, arg: str):
        """Attempt to fix missing dependencies."""
        self.tool_manager.dependency_checker.fix_all_dependencies()
    
    def do_logs(self, arg: str):
        """View recent logs: logs [lines]"""
        lines = int(arg) if arg and arg.isdigit() else 20
        log_lines = self.tool_manager.get_logs(lines)
        
        if not log_lines:
            print("📜 No log entries found")
            return
        
        print(f"\n📜 RECENT LOGS (last {len(log_lines)} entries):")
        print("─" * 60)
        for line in log_lines:
            print(line.rstrip())
        print()
    
    def do_platform(self, arg: str):
        """Show platform information."""
        info = PlatformUtils.get_platform_info()
        pkg_manager = PlatformUtils.get_package_manager()
        
        print(f"""
╔{'═'*58}╗
║  💻 PLATFORM INFORMATION                                  ║
╠{'═'*58}╣
║  System: {info['system']:<48}║
║  Release: {info['release'][:47]:<47}║
║  Machine: {info['machine']:<47}║
║  Python: {info['python_version']:<48}║
║  Package Manager: {(pkg_manager or 'Not detected'):<39}║
║  Tools Directory: {str(self.tool_manager.tools_dir)[:39]:<39}║
╚{'═'*58}╝
""")
    
    def do_clear(self, arg: str):
        """Clear the screen."""
        import os
        os.system('cls' if PlatformUtils.get_platform() == 'windows' else 'clear')
    
    def do_quit(self, arg: str):
        """Exit the tool manager."""
        print("👋 Goodbye!")
        return True
    
    def do_exit(self, arg: str):
        """Exit the tool manager."""
        return self.do_quit(arg)
    
    # Aliases
    do_q = do_quit
    do_ls = do_installed
    do_list = do_available
    
    def default(self, line: str):
        """Handle unknown commands."""
        print(f"❌ Unknown command: {line}")
        print("   Type 'help' for available commands")
    
    def emptyline(self):
        """Do nothing on empty line."""
        pass