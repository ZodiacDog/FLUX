"""
FLUX Protocol Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flux-protocol",
    version="1.0.0",
    author="ML",
    author_email="contact@fluxprotocol.dev",
    description="AI-to-AI communication protocol with 48% size reduction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flux-protocol",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - stdlib only!
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "matplotlib>=3.5",
            "numpy>=1.20",
        ],
        "benchmark": [
            "matplotlib>=3.5",
            "numpy>=1.20",
        ],
    },
    entry_points={
        "console_scripts": [
            "flux-benchmark=benchmarks.run_benchmarks:main",
        ],
    },
    keywords="ai communication protocol serialization compression binary",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/flux-protocol/issues",
        "Source": "https://github.com/yourusername/flux-protocol",
        "Documentation": "https://github.com/yourusername/flux-protocol/docs",
    },
)
