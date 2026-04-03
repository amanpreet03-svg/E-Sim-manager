"""
GUI Module
Graphical user interface for the Tool Manager.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Optional

from core.tool_manager import ToolManager, ToolStatus
from utils.logger import get_logger


class GUI:
    """
    Graphical user interface for eSim Tool Manager.
    """
    
    def __init__(self, tool_manager: ToolManager):
        """
        Initialize GUI.
        
        Args:
            tool_manager: ToolManager instance
        """
        self.tool_manager = tool_manager
        self.logger = get_logger(__name__)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("eSim Tool Manager")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Build UI
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()
        
        # Populate initial data
        self._refresh_tool_list()
    
    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh", command=self._refresh_tool_list)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Install Tool...", command=self._show_install_dialog)
        tools_menu.add_command(label="Check Updates", command=self._check_updates)
        tools_menu.add_command(label="Update All", command=self._update_all)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self):
        """Create the main layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Installed tools tab
        self.installed_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.installed_frame, text="Installed Tools")
        self._create_installed_tab()
        
        # Available tools tab
        self.available_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.available_frame, text="Available Tools")
        self._create_available_tab()
        
        # Dependencies tab
        self.deps_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.deps_frame, text="Dependencies")
        self._create_dependencies_tab()
        
        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.logs_frame, text="Logs")
        self._create_logs_tab()
    
    def _create_installed_tab(self):
        """Create the installed tools tab."""
        # Toolbar
        toolbar = ttk.Frame(self.installed_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Refresh", 
                   command=self._refresh_tool_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Update Selected",
                   command=self._update_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Uninstall Selected",
                   command=self._uninstall_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Configure",
                   command=self._configure_selected).pack(side=tk.LEFT, padx=2)
        
        # Tool list
        columns = ("name", "version", "status", "installed_date")
        self.installed_tree = ttk.Treeview(
            self.installed_frame, 
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        self.installed_tree.heading("name", text="Tool Name")
        self.installed_tree.heading("version", text="Version")
        self.installed_tree.heading("status", text="Status")
        self.installed_tree.heading("installed_date", text="Installed Date")
        
        self.installed_tree.column("name", width=200)
        self.installed_tree.column("version", width=100)
        self.installed_tree.column("status", width=150)
        self.installed_tree.column("installed_date", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.installed_frame, orient=tk.VERTICAL,
                                   command=self.installed_tree.yview)
        self.installed_tree.configure(yscrollcommand=scrollbar.set)
        
        self.installed_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click
        self.installed_tree.bind("<Double-1>", self._on_tool_double_click)
    
    def _create_available_tab(self):
        """Create the available tools tab."""
        # Toolbar
        toolbar = ttk.Frame(self.available_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Install Selected",
                   command=self._install_selected).pack(side=tk.LEFT, padx=2)
        
        # Search
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        
        # Tool list
        columns = ("name", "latest_version", "description", "installed")
        self.available_tree = ttk.Treeview(
            self.available_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        self.available_tree.heading("name", text="Tool Name")
        self.available_tree.heading("latest_version", text="Latest Version")
        self.available_tree.heading("description", text="Description")
        self.available_tree.heading("installed", text="Installed")
        
        self.available_tree.column("name", width=150)
        self.available_tree.column("latest_version", width=100)
        self.available_tree.column("description", width=400)
        self.available_tree.column("installed", width=80)
        
        scrollbar = ttk.Scrollbar(self.available_frame, orient=tk.VERTICAL,
                                   command=self.available_tree.yview)
        self.available_tree.configure(yscrollcommand=scrollbar.set)
        
        self.available_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_dependencies_tab(self):
        """Create the dependencies tab."""
        # Toolbar
        toolbar = ttk.Frame(self.deps_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Check Dependencies",
                   command=self._check_dependencies).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Fix Missing",
                   command=self._fix_dependencies).pack(side=tk.LEFT, padx=2)
        
        # Dependencies list
        columns = ("name", "status", "version")
        self.deps_tree = ttk.Treeview(
            self.deps_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        self.deps_tree.heading("name", text="Dependency")
        self.deps_tree.heading("status", text="Status")
        self.deps_tree.heading("version", text="Version")
        
        self.deps_tree.pack(fill=tk.BOTH, expand=True)
    
    def _create_logs_tab(self):
        """Create the logs tab."""
        # Toolbar
        toolbar = ttk.Frame(self.logs_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Refresh",
                   command=self._refresh_logs).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear",
                   command=self._clear_logs).pack(side=tk.LEFT, padx=2)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            self.logs_frame,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _refresh_tool_list(self):
        """Refresh the installed tools list."""
        # Clear existing items
        for item in self.installed_tree.get_children():
            self.installed_tree.delete(item)
        
        # Add installed tools
        tools = self.tool_manager.list_installed_tools()
        for tool in tools:
            self.installed_tree.insert("", tk.END, values=(
                tool.name,
                tool.version,
                tool.status.value,
                tool.install_date[:10] if tool.install_date else "N/A"
            ))
        
        # Clear and repopulate available tools
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)
        
        available = self.tool_manager.list_available_tools()
        for tool in available:
            installed = "✓" if tool['id'] in self.tool_manager.installed_tools else ""
            self.available_tree.insert("", tk.END, values=(
                tool['name'],
                tool['latest_version'],
                tool['description'][:60] + "..." if len(tool['description']) > 60 else tool['description'],
                installed
            ))
        
        self._set_status("Tool list refreshed")
    
    def _set_status(self, message: str):
        """Set status bar message."""
        self.status_var.set(message)
    
    def _show_install_dialog(self):
        """Show tool installation dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Install Tool")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Tool selection
        ttk.Label(dialog, text="Select tool:").pack(pady=10)
        
        tools = self.tool_manager.list_available_tools()
        tool_names = [t['name'] for t in tools]
        
        tool_var = tk.StringVar()
        tool_combo = ttk.Combobox(dialog, textvariable=tool_var, values=tool_names)
        tool_combo.pack(pady=5)
        
        # Version selection
        ttk.Label(dialog, text="Version (optional):").pack(pady=5)
        version_var = tk.StringVar()
        version_entry = ttk.Entry(dialog, textvariable=version_var)
        version_entry.pack(pady=5)
        
        def do_install():
            tool = tool_var.get().lower()
            version = version_var.get() or None
            dialog.destroy()
            self._run_in_thread(
                lambda: self.tool_manager.install_tool(tool, version),
                f"Installing {tool}...",
                f"{tool} installed successfully"
            )
        
        ttk.Button(dialog, text="Install", command=do_install).pack(pady=20)
    
    def _install_selected(self):
        """Install the selected tool from available list."""
        selection = self.available_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tool to install")
            return
        
        item = self.available_tree.item(selection[0])
        tool_name = item['values'][0].lower()
        
        self._run_in_thread(
            lambda: self.tool_manager.install_tool(tool_name),
            f"Installing {tool_name}...",
            f"{tool_name} installed successfully"
        )
    
    def _uninstall_selected(self):
        """Uninstall the selected tool."""
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tool to uninstall")
            return
        
        item = self.installed_tree.item(selection[0])
        tool_name = item['values'][0].lower()
        
        if messagebox.askyesno("Confirm", f"Uninstall {tool_name}?"):
            self._run_in_thread(
                lambda: self.tool_manager.uninstall_tool(tool_name),
                f"Uninstalling {tool_name}...",
                f"{tool_name} uninstalled successfully"
            )
    
    def _update_selected(self):
        """Update the selected tool."""
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tool to update")
            return
        
        item = self.installed_tree.item(selection[0])
        tool_name = item['values'][0].lower()
        
        self._run_in_thread(
            lambda: self.tool_manager.update_tool(tool_name),
            f"Updating {tool_name}...",
            f"{tool_name} updated successfully"
        )
    
    def _configure_selected(self):
        """Configure the selected tool."""
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tool to configure")
            return
        
        item = self.installed_tree.item(selection[0])
        tool_name = item['values'][0].lower()
        
        success = self.tool_manager.configure_tool(tool_name)
        if success:
            messagebox.showinfo("Success", f"{tool_name} configured successfully")
        else:
            messagebox.showerror("Error", f"Failed to configure {tool_name}")
    
    def _check_updates(self):
        """Check for tool updates."""
        self._set_status("Checking for updates...")
        
        def check():
            updates = self.tool_manager.check_updates()
            has_updates = [f"{k}: {v}" for k, v in updates.items() if v]
            
            if has_updates:
                messagebox.showinfo("Updates Available", 
                                   "Updates available for:\n" + "\n".join(has_updates))
            else:
                messagebox.showinfo("Up to Date", "All tools are up to date!")
            
            self._set_status("Ready")
        
        threading.Thread(target=check).start()
    
    def _update_all(self):
        """Update all installed tools."""
        if messagebox.askyesno("Confirm", "Update all installed tools?"):
            self._run_in_thread(
                lambda: self.tool_manager.update_all_tools(),
                "Updating all tools...",
                "All tools updated"
            )
    
    def _check_dependencies(self):
        """Check system dependencies."""
        self._set_status("Checking dependencies...")
        
        # Clear existing
        for item in self.deps_tree.get_children():
            self.deps_tree.delete(item)
        
        result = self.tool_manager.check_all_dependencies()
        
        for dep in result['installed']:
            version = self.tool_manager.dependency_checker.get_version(dep) or "N/A"
            self.deps_tree.insert("", tk.END, values=(dep, "✓ Installed", version))
        
        for dep in result['missing']:
            self.deps_tree.insert("", tk.END, values=(dep, "✗ Missing", "-"))
        
        self._set_status("Dependency check complete")
    
    def _fix_dependencies(self):
        """Attempt to fix missing dependencies."""
        if messagebox.askyesno("Confirm", "Attempt to install missing dependencies?"):
            self._run_in_thread(
                lambda: self.tool_manager.dependency_checker.fix_all_dependencies(),
                "Installing dependencies...",
                "Dependencies fixed"
            )
    
    def _refresh_logs(self):
        """Refresh the log display."""
        logs = self.tool_manager.get_logs(100)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "".join(logs))
        self.log_text.see(tk.END)
    
    def _clear_logs(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)
    
    def _on_search(self, *args):
        """Handle search input."""
        query = self.search_var.get().lower()
        
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)
        
        available = self.tool_manager.list_available_tools()
        for tool in available:
            if query in tool['name'].lower() or query in tool['description'].lower():
                installed = "✓" if tool['id'] in self.tool_manager.installed_tools else ""
                self.available_tree.insert("", tk.END, values=(
                    tool['name'],
                    tool['latest_version'],
                    tool['description'][:60],
                    installed
                ))
    
    def _on_tool_double_click(self, event):
        """Handle double-click on tool."""
        selection = self.installed_tree.selection()
        if selection:
            item = self.installed_tree.item(selection[0])
            tool_name = item['values'][0].lower()
            
            info = self.tool_manager.get_tool_info(tool_name)
            if info:
                messagebox.showinfo(
                    f"Tool: {info.name}",
                    f"Version: {info.version}\n"
                    f"Status: {info.status.value}\n"
                    f"Path: {info.install_path}\n"
                    f"Installed: {info.install_date}"
                )
    
    def _run_in_thread(self, func, status_msg: str, success_msg: str):
        """Run a function in a background thread."""
        self._set_status(status_msg)
        
        def run():
            try:
                result = func()
                self.root.after(0, lambda: self._set_status(success_msg))
                self.root.after(0, self._refresh_tool_list)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self._set_status("Error occurred"))
        
        threading.Thread(target=run).start()
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About eSim Tool Manager",
            "eSim Automated Tool Manager\n"
            "Version 1.0.0\n\n"
            "An automated tool for managing external tools\n"
            "and dependencies for eSim EDA software.\n\n"
            "© 2024 eSim Team"
        )
    
    def run(self):
        """Start the GUI application."""
        self._check_dependencies()
        self._refresh_logs()
        self.root.mainloop()