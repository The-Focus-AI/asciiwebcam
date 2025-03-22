# ASCII Webcam Project Guide

## Build & Run Commands
- Install dependencies: `mise run install` or `mise run i`
- Install dev dependencies: `mise run dev-install` or `mise run di`
- Run application: `mise run run` or `python -m ascii_webcam.app`
- List presets: `mise run run-list` or `python -m ascii_webcam.app --list-presets`
- Run with Matrix theme: `mise run run-matrix`

## Test Commands
- Run all tests: `mise run test` or `pytest tests/`
- Run single test: `pytest tests/test_converter.py::test_converter_init`
- Run test class: `pytest tests/test_converter.py::TestClass`

## Lint & Format
- Lint code: `mise run lint` or `ruff check .`
- Format code: `mise run format` or `ruff format .`

## Code Style Guidelines
- **Imports**: stdlib → third-party → local modules, alphabetically ordered
- **Formatting**: Black-compatible, ~88 characters line length
- **Types**: Use Python type hints from typing module (Dict, List, Tuple, Optional)
- **Naming**: CamelCase for classes, snake_case for functions/variables, UPPER_SNAKE_CASE for constants
- **Error Handling**: Specific exceptions with descriptive messages, use click.ClickException for CLI errors
- **Documentation**: Google-style docstrings for all modules, classes, and functions