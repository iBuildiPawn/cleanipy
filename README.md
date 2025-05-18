# CleanIPy

<p align="center">
  <strong>A powerful terminal-based storage cleaning utility for Python</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#development">Development</a> •
  <a href="#license">License</a>
</p>

---

## Features

CleanIPy is a comprehensive storage cleaning utility that helps you analyze and free up disk space on your system. It provides a user-friendly terminal interface with the following features:

- **Disk Usage Analysis**: View detailed information about disk usage across your system
- **Directory Analysis**: Analyze directories to find large files and understand storage distribution
- **Temporary Files Cleaning**: Identify and clean temporary files from system, browser, and package caches
- **Duplicate Files Detection**: Find and manage duplicate files to reclaim wasted space
- **Large Files Management**: Locate and clean large files that are consuming excessive storage
- **Safe File Removal**: Files are sent to trash instead of being permanently deleted
- **Rich Terminal UI**: User-friendly interface with tables, progress bars, and color-coded information

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/iBuildiPawn/cleanipy.git

# Navigate to the project directory
cd cleanipy

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## Usage

### Running CleanIPy

After installation, you can run CleanIPy using the following command:

```bash
python -m cleanipy.main
```

### Main Menu Options

1. **Show disk usage**: Displays information about disk usage across all mounted filesystems
2. **Analyze directory**: Analyzes a directory to find large files and understand storage distribution
3. **Analyze temporary files**: Identifies temporary files that can be safely cleaned
4. **Analyze duplicate files**: Finds duplicate files that are wasting storage space
5. **Clean temporary files**: Removes temporary files to free up space
6. **Clean large files**: Helps you identify and remove large files
7. **Clean duplicate files**: Provides options to manage duplicate files (delete, replace with links)
8. **Exit**: Exits the application

## Screenshots

Screenshots will be added soon.

## Development

### Project Structure

```
cleanipy/
├── analyzers/         # Analysis functionality
├── cleaners/          # Cleaning functionality
├── utils/             # Utility functions
├── main.py            # Main application entry point
└── __init__.py        # Package initialization
```

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Rich](https://github.com/Textualize/rich) - For the beautiful terminal interface
- [Click](https://click.palletsprojects.com/) - For command-line interface utilities
- [Send2Trash](https://github.com/arsenetar/send2trash) - For safely sending files to trash

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/iBuildiPawn">iBuildiPawn</a>
</p>
