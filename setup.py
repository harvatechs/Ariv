#!/usr/bin/env python3
"""
Setup script for Ariv - Indian AI Orchestra
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]

# GUI requirements
gui_requirements = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
]

# TUI requirements
tui_requirements = [
    "textual>=0.44.0",
]

# Development requirements
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
]

# All optional dependencies
all_requirements = gui_requirements + tui_requirements + dev_requirements

setup(
    name="ariv",
    version="2.0.0",
    author="Ariv Contributors",
    author_email="ariv@example.com",
    description="Ariv: The Indian AI Orchestra - Production Ready",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harvatechs/Ariv",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: English",
        "Natural Language :: Hindi",
        "Natural Language :: Tamil",
        "Natural Language :: Bengali",
        "Natural Language :: Telugu",
        "Natural Language :: Marathi",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "gui": gui_requirements,
        "tui": tui_requirements,
        "dev": dev_requirements,
        "all": all_requirements,
        "cuda": ["torch>=2.0.0"],
    },
    entry_points={
        "console_scripts": [
            "ariv=maha_system:main",
            "ariv-download=models.download_models:main",
            "ariv-gui=gui.launch:main",
            "ariv-tui=tui.launch:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.tcss", "*.html", "*.css", "*.js"],
        "gui": ["*.html", "*.css", "*.js"],
        "tui": ["*.tcss"],
        "prompts": ["*.yaml", "*.yml"],
    },
    keywords=[
        "ai", "llm", "language-models", "indian-languages", "nlp",
        "hindi", "tamil", "bengali", "telugu", "marathi", "reasoning",
        "chain-of-thought", "india", "multilingual", "ai-orchestrator"
    ],
    project_urls={
        "Bug Reports": "https://github.com/harvatechs/Ariv/issues",
        "Source": "https://github.com/harvatechs/Ariv",
        "Documentation": "https://github.com/harvatechs/Ariv/wiki",
        "Discord": "https://discord.gg/ariv",
    },
)
