# ASCII Webcam

Real-time ASCII art webcam viewer in the terminal. Transform your webcam feed into beautiful, colorful ASCII art right in your terminal!

![Demo](out.gif)

## Features

- Real-time webcam to ASCII art conversion
- Multiple character presets:
  - Classic ASCII
  - Unicode blocks
  - Matrix style
  - Dots and lines
  - And more!
- Rich color schemes:
  - True color (webcam colors)
  - Matrix green
  - Cyberpunk neon
  - Vintage sepia
  - Enhanced neon
- Performance optimizations:
  - Dynamic frame rate control (5-15 FPS)
  - Smart frame skipping
  - Memory optimization
  - Efficient screen updates
- Interactive controls:
  - Style switching (press 'p')
  - Color scheme cycling (press 's')
  - Frame rate control (press 'f' or 'w')
  - Status toggle (press 't')
  - Help display (press 'h')
- Status display with:
  - Current FPS
  - CPU usage
  - Memory usage
  - Terminal size
  - Active settings
- Robust error handling and recovery
- Dynamic terminal resize support

## Requirements

- Python 3.11 or newer
- Working webcam
- Modern terminal with:
  - True color support
  - Unicode support
  - VT100 compatibility
  - Minimum 80x24 resolution

## Installation

1. Ensure you have Python 3.11+ installed
2. Install using pip:
   ```bash
   pip install ascii-webcam
   ```

Or install from source:

1. Clone the repository
2. Install mise if you haven't already:
   ```bash
   curl https://mise.run | sh
   ```
3. Setup the environment:
   ```bash
   mise install
   ```

## Usage

Basic usage:

```bash
ascii-webcam
```

List available presets and color schemes:

```bash
ascii-webcam --list-presets
```

Specify camera and initial style:

```bash
ascii-webcam --camera 1 --preset matrix --scheme neon
```

### Keyboard Controls

- `p`: Switch character preset
- `s`: Switch color scheme
- `f`: Fast mode (15 FPS)
- `w`: Slow mode (5 FPS)
- `t`: Toggle status display
- `h`: Toggle help
- `r`: Retry camera (if error)
- `q`: Quit

## Development

1. Clone the repository
2. Install mise:
   ```bash
   curl https://mise.run | sh
   ```
3. Setup development environment:
   ```bash
   mise install
   ```
4. Available commands:
   ```bash
   mise run install      # Install dependencies
   mise run dev-install  # Install development dependencies
   mise run run         # Run the ASCII webcam viewer
   mise run list        # List available presets
   mise run matrix      # Run with matrix preset
   mise run cyberpunk   # Run with cyberpunk preset
   mise run vintage     # Run with vintage preset
   mise run neon        # Run with neon preset
   ```

## License

MIT License - See LICENSE file for details
