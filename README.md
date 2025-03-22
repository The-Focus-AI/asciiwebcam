# ASCII Webcam

Real-time ASCII art webcam viewer in the terminal. Transform your webcam feed into beautiful, colorful ASCII art right in your terminal!

## Features

- Real-time webcam to ASCII conversion
- Full color support
- Multiple style presets
- Keyboard shortcuts for style switching
- Configurable camera source

## Installation

1. Ensure you have Python 3.8 or newer installed
2. Install using pip:
   ```bash
   pip install ascii-webcam
   ```

## Usage

Run the basic viewer:

```bash
ascii-webcam
```

Specify a different camera:

```bash
ascii-webcam --camera 1
```

## Development Setup

1. Clone the repository
2. Install Poetry if you haven't already
3. Install dependencies:
   ```bash
   poetry install
   ```
4. Run the application:
   ```bash
   poetry run python -m ascii_webcam
   ```

## Running Tests

```bash
poetry run pytest
```

## License

MIT License
