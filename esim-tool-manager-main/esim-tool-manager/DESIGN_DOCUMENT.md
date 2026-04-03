# eSim Automated Tool Manager - Design Document

## 1. Introduction

### 1.1 Purpose
The eSim Automated Tool Manager is a Python-based utility designed to automate the installation, configuration, update, and management of external tools and dependencies required by eSim - an open-source EDA tool for circuit design and simulation.

### 1.2 Scope
This tool manager handles:
- Automated installation of tools (Ngspice, KiCad, GTKWave, etc.)
- Version management and updates
- Dependency checking and resolution
- Cross-platform support (Windows, Linux, macOS)
- Configuration and PATH management

### 1.3 Target Users
- Electronics engineers using eSim
- Students learning circuit simulation
- Researchers in EDA field

---

## 2. System Architecture

### 2.1 High-Level Architecture
<img width="515" height="671" alt="image" src="https://github.com/user-attachments/assets/c86c0bd4-55ec-4784-a00b-8f7fc7911b07" />



### 2.2 Module Breakdown

| Module | File | Description |
|--------|------|-------------|
| Main Entry | `main.py` | Application entry point, argument parsing |
| Tool Manager | `core/tool_manager.py` | Central orchestrator for all operations |
| Installer | `core/installer.py` | Handles downloading and installing tools |
| Updater | `core/updater.py` | Manages version checking and updates |
| Config Handler | `core/config_handler.py` | Manages tool configurations and PATH |
| Dependency Checker | `core/dependency_checker.py` | Checks and installs dependencies |
| Tool Registry | `tools/tool_registry.py` | Database of available tools |
| CLI | `ui/cli.py` | Command-line interface |
| Platform Utils | `utils/platform_utils.py` | OS-specific utilities |
| Download Utils | `utils/download_utils.py` | File download management |
| Logger | `utils/logger.py` | Logging system |

---

## 3. Component Details

### 3.1 Tool Manager (Core)

**Responsibilities:**
- Initialize all subsystems
- Coordinate between modules
- Maintain installed tools registry
- Handle user requests

**Key Methods:**

install_tool(tool_name, version) -> bool
uninstall_tool(tool_name) -> bool
update_tool(tool_name) -> bool
check_updates() -> Dict[str, str]
list_installed_tools() -> List[ToolInfo]
list_available_tools() -> List[Dict]


3.2 Installer
Responsibilities:

Download tool packages
Extract archives (ZIP, TAR)
Run installers (EXE, MSI)
Verify installations
Download Methods (Priority Order):

PowerShell (Windows)
curl
Python requests
Python urllib
Manual browser download
3.3 Dependency Checker
Responsibilities:

Check system dependencies
Detect package managers
Install missing dependencies
Provide installation guidance
Supported Dependencies:

Python, pip, git, gcc, make, cmake
Platform-specific tools
3.4 Configuration Handler
Responsibilities:

Add tools to system PATH
Set environment variables
Create tool configuration files
Update eSim integration config


## 4. Data Flow
   
### 4.1 Installation Flow

<img width="424" height="292" alt="image" src="https://github.com/user-attachments/assets/bd24bb48-90d8-42bc-ab5e-8d11a02787fa" />

              
### 4.2 Update Flow

<img width="440" height="306" alt="image" src="https://github.com/user-attachments/assets/fd721dcb-75bc-4e96-a12e-e9c915bcf387" />


              
## 5. Supported Tools
Tool	Category	Platforms	Install Method
Ngspice	Simulation	Win/Lin/Mac	ZIP/Package
KiCad	EDA	Win/Lin/Mac	Installer/Package
GTKWave	Visualization	Win/Lin/Mac	ZIP/Package
Verilator	Simulation	Win/Lin/Mac	ZIP/Package
Icarus Verilog	Simulation	Win/Lin/Mac	Installer/Package
GHDL	Simulation	Win/Lin/Mac	ZIP/Package


## 6. Configuration Files

### 6.1 installed.json
Stores information about installed tools:


```JSON []
{
  "ngspice": {
    "name": "ngspice",
    "version": "43",
    "status": "installed",
    "install_path": "C:/Users/.../tools/ngspice",
    "install_date": "2024-01-15T10:30:00"
  }
}
```

### 6.2 settings.json

Application settings:

JSON

```JSON []
{
  "auto_update_check": true,
  "log_level": "INFO",
  "backup_before_update": true
}
```


## 7. Error Handling

Error Type	Handling Strategy
Download Failure	Try multiple methods, offer manual download
Extraction Failure	Clean up partial files, report error
Missing Dependencies	Prompt user, offer auto-install
Permission Error	Request elevation or suggest manual action
Network Error	Retry with timeout, offline fallback


## 8. Security Considerations
HTTPS for all downloads
Checksum verification (when available)
No storage of sensitive credentials
User confirmation for system changes


## 9. Future Enhancements
GUI interface with progress visualization
Plugin system for custom tools
Automatic scheduled updates
Integration with eSim main application
Cloud-based tool repository
Rollback functionality


## 10. Requirements Met

| Requirement                  | Status | Implementation            |
|-----------------------------|--------|---------------------------|
| Tool Installation Management | ✅     | installer.py              |
| Update and Upgrade System    | ✅     | updater.py                |
| Configuration Handling       | ✅     | config_handler.py         |
| Dependency Checker           | ✅     | dependency_checker.py     |
| User Interface (CLI)         | ✅     | cli.py                    |
| Cross-platform Support       | ✅     | platform_utils.p          |



## 11. Conclusion
The eSim Automated Tool Manager provides a robust, user-friendly solution for managing external tools required by eSim. Its modular architecture allows for easy extension and maintenance, while the multiple fallback mechanisms ensure reliable operation across different environments.



