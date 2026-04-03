# 🛠️ eSim Automated Tool Manager

<div align="center">

![eSim Tool Manager](https://img.shields.io/badge/eSim-Tool%20Manager-blue?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-GPL--3.0-red?style=for-the-badge)

**An automated tool manager for eSim - simplifying the installation, configuration, and management of external EDA tools and dependencies.**

[Features](#-features) •
[Installation](#-installation) •
[Usage](#-usage) •
[Commands](#-commands) •
[Documentation](#-documentation) •
[Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Supported Tools](#-supported-tools)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Commands Reference](#-commands-reference)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 📖 About

**eSim** is an open-source EDA (Electronic Design Automation) tool for circuit design, simulation, analysis, and PCB design. It integrates several external tools like Ngspice, KiCad, and others to provide a seamless environment for engineers and researchers.

The **eSim Automated Tool Manager** solves the challenge of manually managing these external tools by providing:

- 🔄 **Automated Installation** - One-command installation of required tools  
- 📦 **Version Control** - Install and manage specific versions  
- ⚙️ **Auto-Configuration** - Automatic PATH and environment setup  
- 🔍 **Dependency Management** - Check and resolve missing dependencies  
- 🖥️ **Cross-Platform Support** - Works on Windows, Linux, and macOS  

---

## ✨ Features

### ✅ Tool Installation Management
- Download and install external tools automatically
- Support for multiple installation methods (ZIP, installers, package managers)
- Version control with specific version installation
- Verification of successful installations

### ✅ Update and Upgrade System
- Check for available updates for all installed tools
- Update individual tools or all tools at once
- Automatic backup before updates
- Rollback capability if updates fail

### ✅ Configuration Handling
- Automatic PATH management
- Environment variable configuration
- Tool-specific configuration files
- eSim integration setup

### ✅ Dependency Checker
- System dependency verification
- Missing dependency detection
- Automatic installation assistance
- Detailed feedback for manual resolution

### ✅ User Interface
- Interactive command-line interface (CLI)
- Color-coded output for better readability
- Comprehensive help system
- Activity logging

### ✅ Cross-Platform Support
- Windows 10/11
- Linux (Ubuntu, Fedora, Arch)
- macOS

---

## 🔧 Supported Tools

| Tool | Description | Category | Windows | Linux | macOS |
|------|-------------|----------|:-------:|:-----:|:-----:|
| **Ngspice** | Open-source SPICE circuit simulator | Simulation | ✅ | ✅ | ✅ |
| **KiCad** | Electronic Design Automation suite | EDA/PCB | ✅ | ✅ | ✅ |
| **GTKWave** | Waveform viewer for simulation results | Visualization | ✅ | ✅ | ✅ |
| **Verilator** | Verilog/SystemVerilog simulator | Simulation | ✅ | ✅ | ✅ |
| **Icarus Verilog** | Verilog simulation and synthesis | Simulation | ✅ | ✅ | ✅ |
| **GHDL** | VHDL simulator | Simulation | ✅ | ✅ | ✅ |
| **Yosys** | RTL synthesis framework | Synthesis | ⚠️ | ✅ | ✅ |
| **OpenOCD** | On-chip debugger | Debug | ✅ | ✅ | ✅ |

> ✅ = Fully Supported | ⚠️ = Partial Support

---

## 💻 System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10/11, Ubuntu 18.04+, macOS 10.14+ |
| **Python** | 3.8 or higher |
| **RAM** | 4 GB minimum |
| **Storage** | 2 GB free space (more for tools) |
| **Network** | Internet connection for downloads |

### Python Dependencies

```

requests>=2.28.0
packaging>=21.0
tabulate>=0.9.0
colorama>=0.4.6
tqdm>=4.64.0

````

---

## 📥 Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/esim-tool-manager.git

# Navigate to project directory
cd esim-tool-manager
````

### Step 2: Create Virtual Environment

#### Windows (PowerShell)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

#### Linux/macOS

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Navigate to source directory
cd src

# Run the tool manager
python main.py
```

# You should see the welcome screen

---

## 🚀 Usage

### Interactive Mode

```bash
cd src
python main.py
```

```
╔═══════════════════════════════════════════════════════════════╗
║           eSim Automated Tool Manager v1.1.0                  ║
║                     Windows Compatible                        ║
║                                                               ║
║  Type 'help' for available commands or 'quit' to exit.       ║
╚═══════════════════════════════════════════════════════════════╝
```

### Direct Command Mode

```bash
# Install a tool
python main.py install ngspice

# List available tools
python main.py list --available

# Check dependencies
python main.py check-deps
```

### Quick Start Example

```bash
# 1. Start the tool manager
python main.py

# 2. Check your system
(esim-tools) platform

# 3. View available tools
(esim-tools) available

# 4. Install Ngspice
(esim-tools) install ngspice

# 5. Verify installation
(esim-tools) installed

# 6. Get tool info
(esim-tools) info ngspice

# 7. Exit
(esim-tools) quit
```

---

## 📚 Commands Reference

### Tool Management Commands

| Command                    | Description              | Example            |
| -------------------------- | ------------------------ | ------------------ |
| available                  | List all available tools | available          |
| installed                  | List installed tools     | installed          |
| install `<tool>`           | Install a tool           | install ngspice    |
| install `<tool> <version>` | Install specific version | install ngspice 42 |
| uninstall `<tool>`         | Uninstall a tool         | uninstall ngspice  |
| info `<tool>`              | Show tool information    | info ngspice       |

### Update Commands

| Command         | Description                 | Example        |
| --------------- | --------------------------- | -------------- |
| check_updates   | Check for available updates | check_updates  |
| update `<tool>` | Update a specific tool      | update ngspice |
| update all      | Update all installed tools  | update all     |

### System Commands

| Command    | Description               | Example    |
| ---------- | ------------------------- | ---------- |
| check_deps | Check system dependencies | check_deps |
| fix_deps   | Fix missing dependencies  | fix_deps   |
| platform   | Show platform information | platform   |
| logs       | View recent activity logs | logs       |
| logs `<n>` | View last n log entries   | logs 50    |

### General Commands

| Command     | Description           |
| ----------- | --------------------- |
| help        | Show help information |
| clear       | Clear the screen      |
| quit / exit | Exit the tool manager |

---

## 📁 Project Structure

```
esim-tool-manager/
│
├── 📁 src/
│   ├── 📄 main.py
│   ├── 📁 core/
│   │   ├── installer.py
│   │   ├── updater.py
│   │   ├── config_handler.py
│   │   └── dependency_checker.py
│   ├── 📁 tools/
│   ├── 📁 utils/
│   └── 📁 ui/
│
├── 📁 config/
│   ├── tools.json
│   ├── settings.json
│   └── installed.json
│
├── 📁 logs/
├── 📁 tests/
├── requirements.txt
├── setup.py
├── README.md
├── DESIGN_DOCUMENT.md
└── LICENSE
```

---

## ⚙️ Configuration

### Application Settings

```json
{
    "auto_update_check": true,
    "log_level": "INFO",
    "backup_before_update": true,
    "max_backup_count": 3,
    "download_timeout": 300
}
```

### Installed Tools Record

```json
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

### Installation Paths

| Platform | Default Installation Path                |
| -------- | ---------------------------------------- |
| Windows  | %LOCALAPPDATA%\eSim\tools                |
| Linux    | ~/.local/share/esim/tools                |
| macOS    | ~/Library/Application Support/eSim/tools |

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Download Fails (403/404 Error)

```bash
pip install requests
(esim-tools) install ngspice
```

#### 2. Tool Not Found After Installation

Restart terminal or add tool path to PATH.

#### 3. Permission Denied Error

Run as Administrator or fix folder permissions.

#### 4. Python Module Not Found

```bash
pip install -r requirements.txt
```

---

## 🧪 Testing

```bash
pip install pytest pytest-cov
pytest tests/ -v
pytest tests/ -v --cov=src --cov-report=html
```

---

## 🤝 Contributing

```bash
git checkout -b feature/your-feature-name
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

---

## 📜 License

GNU General Public License v3.0

---

## 🙏 Acknowledgments

* eSim Team at FOSSEE, IIT Bombay
* Ngspice Development Team
* KiCad Development Team
* Open Source Community

---

<div align="center">

⭐ If you find this project useful, please consider giving it a star! ⭐

Made with ❤️ for the eSim Community

Developed as part of eSim Semester Long Internship Spring 2026

</div>
```

