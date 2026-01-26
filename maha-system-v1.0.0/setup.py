from setuptools import setup, find_packages

setup(
    name="maha-system",
    version="1.0.0",
    description="Sovereign Indian AI via Test-Time Compute Orchestration",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "llama-cpp-python>=0.2.0",
        "huggingface_hub>=0.19.0",
        "pyyaml>=6.0",
        "tqdm>=4.65.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "api": ["fastapi>=0.100.0", "uvicorn>=0.23.0"],
        "benchmark": ["datasets>=2.14.0"],
        "dev": ["pytest>=7.4.0", "black>=23.0.0"]
    },
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'maha-system=maha_system:main',
        ],
    },
)
