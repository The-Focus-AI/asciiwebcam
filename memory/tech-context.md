# ASCII Webcam Art - Technical Context

## Technology Stack

### Core Technologies

- Python 3.8+ (for cross-platform compatibility and rich library support)
- OpenCV (webcam capture and image processing)
- Rich or Blessed (terminal UI and color handling)
- Click or Typer (CLI framework)
- NumPy (efficient image processing)

### Development Tools

- Poetry (dependency management)
- Pytest (testing framework)
- Black (code formatting)
- Pylint (code quality)
- MyPy (type checking)

## Technical Constraints

### Terminal Requirements

- Modern terminal with:
  - True color support
  - Unicode support
  - Minimum 80x24 resolution
  - VT100 compatibility

### System Requirements

- Python 3.8 or higher
- Working webcam
- Operating System:
  - Linux (X11 or Wayland)
  - macOS 10.13+
  - Windows 10+

### Performance Targets

- Minimum 15 FPS on modern hardware
- Maximum 100MB memory usage
- CPU usage below 30% on modern processors

## Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.8"
opencv-python = "^4.8.0"
numpy = "^1.24.0"
rich = "^13.0.0"
click = "^8.1.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
black = "^23.7.0"
pylint = "^2.17.0"
mypy = "^1.5.0"
```

## Development Setup

1. Install Python 3.8+
2. Install Poetry
3. Clone repository
4. Run `poetry install`
5. Activate virtual environment
6. Run development server with `poetry run python -m ascii_webcam`

## Build Process

- Poetry for package management
- PyInstaller for binary distribution
- GitHub Actions for CI/CD

## Testing Environment

- Pytest for unit and integration tests
- Coverage.py for code coverage
- Tox for multi-environment testing
