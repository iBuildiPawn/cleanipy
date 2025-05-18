from setuptools import setup, find_packages
import os

# Read requirements from file if it exists, otherwise define them here
if os.path.exists("requirements.txt"):
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
else:
    requirements = [
        "rich>=10.0.0",
        "click>=8.0.0",
        "send2trash>=1.8.0",
    ]

# Read long description from README if it exists
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A powerful terminal-based storage cleaning utility for Python"

setup(
    name="cleanipy",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "flake8>=3.9.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "cleanipy=cleanipy.main:main",
        ],
    },
    author="iBuildiPawn",
    author_email="ibuildiPawn@example.com",
    description="A powerful terminal-based storage cleaning utility for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iBuildiPawn/cleanipy",
    keywords="clean, storage, disk, python, utility, terminal, duplicate, files",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
)
