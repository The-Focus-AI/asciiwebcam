# ASCII Webcam Art - Technical Context

## Technology Stack

### Core Technologies

- Python 3.8+ (for cross-platform compatibility and rich library support)
- OpenCV (webcam capture and image processing)
- Direct ANSI terminal control (for efficient display updates)
- Click (CLI framework)
- NumPy (efficient image processing)

### Development Tools

- mise (2025.3.0) for tool and environment management
- uv (latest) for dependency and virtual environment management
- Pytest (8.3.5) for testing framework
- Ruff (0.11.2) for code formatting and linting
- Coverage (7.7.1) for test coverage

## Technical Constraints

### Terminal Requirements

- Modern terminal with:
  - True color support
  - Unicode support
  - Minimum 80x24 resolution
  - VT100 compatibility
  - ANSI escape sequence support

### System Requirements

- Python 3.11.11
- Working webcam
- Operating System:
  - Linux (X11 or Wayland)
  - macOS 10.13+ (verified on darwin 24.3.0)
  - Windows 10+

### Performance Targets

- Dynamic frame rate control:
  - Fast mode: 15 FPS
  - Slow mode: 5 FPS
  - Real-time switching
- Maximum 100MB memory usage
- CPU usage below 30% on modern processors
- Efficient screen updates with minimal flicker

## Dependencies

### Core Dependencies

- opencv-python ^4.11.0
- numpy ^2.2.4
- click ^8.1.0

### Development Dependencies

- pytest ^8.3.5
- ruff ^0.11.2
- coverage ^7.7.1
- pytest-cov ^6.0.0

## Development Setup

- Running in a virtual environment managed by mise and uv
- Using mise for tool version management
- Using uv for dependency management and environment control
- Camera access required
- Development on macOS (darwin 24.3.0)
- mise tasks configured for common operations:
  - install: Install dependencies
  - dev-install: Install development dependencies
  - run: Run the ASCII webcam viewer
  - list: List available presets
  - matrix/cyberpunk/vintage/neon: Run with specific presets
  - test: Run tests
  - lint: Check code with ruff
  - format: Format code with ruff
  - clean: Clean up generated files
  - info: Print project information
  - term-test: Run terminal test pattern

## Display Architecture

### Terminal Control

- Direct ANSI escape sequence usage for:
  - Cursor positioning
  - Color control
  - Screen clearing
  - Line clearing
- Dynamic frame rate control:
  - Fast mode (15 FPS)
  - Slow mode (5 FPS)
  - Real-time switching
- Efficient screen updates without full clears
- Proper handling of terminal dimensions

### Display Features

- Line number display (every 5 lines)
- Status bar with:
  - Terminal size
  - Current frame rate
  - Active preset
  - Color scheme
  - Error messages
- Help display integration
- Dynamic resizing support
- Proper aspect ratio handling

### Error Handling

- Custom exception hierarchy:
  - ASCIIWebcamError (base)
  - CameraError (camera issues)
  - TerminalError (terminal issues)
- User-friendly error messages:
  - Clear descriptions
  - Recovery instructions
  - Color-coded display
- Recovery mechanisms:
  - Camera retry functionality
  - Terminal restoration
  - Resource cleanup
  - Graceful fallbacks
- Resource management:
  - Proper cleanup on exit
  - Safe terminal restoration
  - Camera release handling

## Current Technical Challenges

1. ~~Terminal display issues:~~ ✅ All Fixed

   - ~~Double spacing in ASCII output~~ ✅ Fixed with direct ANSI control
   - ~~Screen flicker and jitter~~ ✅ Fixed with optimized updates
   - ~~Terminal resizing issues~~ ✅ Fixed with proper dimension handling
   - ~~Frame rate control~~ ✅ Fixed with dynamic FPS settings
   - ~~Error handling~~ ✅ Fixed with comprehensive system

2. Performance optimization:
   - CPU usage optimization
   - Memory usage monitoring
   - Frame processing efficiency
   - Color mapping optimization

## Technical Decisions

1. Error Handling Architecture:

   - Custom exception hierarchy for better error categorization
   - User-friendly error messages with recovery instructions
   - Color-coded error display for visibility
   - Resource cleanup in all error cases
   - Recovery options where possible

2. Display System:

   - Direct ANSI control for performance
   - Error message integration in status bar
   - Dynamic frame rate control
   - Efficient screen updates
   - Clean terminal restoration

3. Resource Management:
   - Safe cleanup procedures
   - Proper error recovery
   - Terminal state preservation
   - Camera resource handling

## Build Process

- uv for package and environment management
- PyInstaller for binary distribution
- GitHub Actions for CI/CD

## Testing Environment

- Pytest for unit and integration tests
- Coverage.py for code coverage
- Tox for multi-environment testing

## Technical Constraints

- Terminal character aspect ratio (roughly 2:1 height:width)
- Terminal size limitations
- Need to handle terminal resizing events
- Need to maintain proper aspect ratio during frame conversion
- Need to handle camera access permissions
- Need to manage terminal state properly
- Need to handle various error conditions gracefully
