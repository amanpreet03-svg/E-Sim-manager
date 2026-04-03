#!/usr/bin/env python3
"""
Setup script for eSim Tool Manager.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="esim-tool-manager",
    version="1.0.0",
    author="eSim Team",
    author_email="contact-esim@fossee.in",
    description="Automated Tool Manager for eSim EDA Software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/esim-tool-manager",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "packaging>=21.0",
        "tabulate>=0.9.0",
        "certifi>=2022.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "esim-tools=main:main",
        ],
    },
)