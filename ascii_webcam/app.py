"""Main application module for ASCII Webcam."""

import cv2
import click
import sys
import termios
import tty
import select
import shutil
import signal
import time
import psutil
from typing import Dict, Tuple, Optional
import numpy as np

from .converter import ASCIIConverter

class ASCIIWebcamError(Exception):
    """Base exception class for ASCII Webcam errors."""
    pass

class CameraError(ASCIIWebcamError):
    """Exception raised for camera-related errors."""
    pass

class TerminalError(ASCIIWebcamError):
    """Exception raised for terminal-related errors."""
    pass

class ASCIIWebcam:
    """Main application class for ASCII Webcam viewer."""
    
    # Keyboard controls
    CONTROLS = {
        'p': 'Next preset',
        's': 'Next color scheme',
        't': 'Toggle status',
        'h': 'Hide help',
        'f': 'Fast mode (15 FPS)',
        'w': 'Slow mode (5 FPS)',
        'r': 'Retry camera',
        'q': 'Quit',
    }
    
    def __init__(self, camera_id: int = 0, preset: str = 'classic', color_scheme: str = 'true'):
        """Initialize the ASCII Webcam viewer.
        
        Args:
            camera_id: ID of the webcam to use (default: 0)
            preset: Character preset to use (default: 'classic')
            color_scheme: Color scheme to use (default: 'true')
        
        Raises:
            ValueError: If preset or color scheme is invalid
        """
        if preset not in ASCIIConverter.CHAR_PRESETS:
            raise ValueError(f"Invalid preset '{preset}'. Available presets: {list(ASCIIConverter.CHAR_PRESETS.keys())}")
        if color_scheme not in ASCIIConverter.COLOR_SCHEMES:
            raise ValueError(f"Invalid color scheme '{color_scheme}'. Available schemes: {list(ASCIIConverter.COLOR_SCHEMES.keys())}")
        
        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None
        self.preset = preset
        self.color_scheme = color_scheme
        self.show_status = True
        self.show_help = True  # Show help by default
        self.frame_num = 0
        self.frame_rate = 15.0  # Default to 15 FPS
        self.error_message: Optional[str] = None
        
        # Performance monitoring
        self.process = psutil.Process()
        self.frame_times = np.zeros(30)  # Rolling window of frame times
        self.frame_time_idx = 0
        self.last_frame_time = 0
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.actual_fps = 0.0
        
        # Get available presets and color schemes
        self.presets = ASCIIConverter.available_presets()
        self.color_schemes = ASCIIConverter.available_color_schemes()
        
        try:
            # Initialize terminal size and converter
            self.terminal_size = self.get_terminal_size()
            self.converter = self.create_converter()
            
            # Setup signal handler for terminal resize
            signal.signal(signal.SIGWINCH, self.handle_resize)
        except Exception as e:
            raise TerminalError(f"Failed to initialize terminal: {e}")
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """Get current terminal size.
        
        Returns:
            Tuple of (columns, rows)
        """
        terminal = shutil.get_terminal_size()
        # Ensure minimum dimensions
        return (max(terminal.columns, 40), max(terminal.lines, 20))
    
    def create_converter(self) -> ASCIIConverter:
        """Create a new converter with current terminal size.
        
        Returns:
            ASCIIConverter instance
        """
        width, height = self.terminal_size
        
        # Calculate effective dimensions
        # Subtract 3 for line numbers and padding
        effective_width = max(width - 3, 40)
        # Subtract 2 for status bar (if enabled) and ensure minimum height
        effective_height = max(height - 2, 10) if self.show_status else max(height - 1, 10)
        
        return ASCIIConverter(
            preset=self.preset,
            width=effective_width,
            height=effective_height,
            color_scheme=self.color_scheme
        )
    
    def handle_resize(self, signum=None, frame=None):
        """Handle terminal resize event."""
        # Get new terminal size
        new_size = self.get_terminal_size()
        
        # Only update if size actually changed
        if new_size != self.terminal_size:
            self.terminal_size = new_size
            # Update converter with new dimensions
            self.converter = self.create_converter()
            # Force refresh display
            self.print_display()
    
    def setup(self):
        """Set up the webcam capture.
        
        Raises:
            CameraError: If camera initialization fails
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                raise CameraError(f"Could not open camera {self.camera_id}")
            
            # Try to capture a test frame
            ret, _ = self.cap.read()
            if not ret:
                raise CameraError("Camera opened but failed to capture frame")
            
            # Clear screen once at startup
            print("\033[2J\033[H", end="")
            self.error_message = None
        except Exception as e:
            self.error_message = f"Camera error: {e}. Press 'r' to retry or 'q' to quit."
            raise CameraError(str(e))
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass  # Ignore cleanup errors
        # Clear screen on exit
        try:
            print("\033[2J\033[H", end="")
        except Exception:
            pass  # Ignore terminal cleanup errors
    
    def capture_frame(self):
        """Capture a frame from the webcam.
        
        Returns:
            numpy.ndarray: Captured frame
        
        Raises:
            CameraError: If frame capture fails
        """
        if self.cap is None:
            raise CameraError("Camera not initialized")
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                raise CameraError("Failed to capture frame")
            return frame
        except Exception as e:
            self.error_message = f"Frame capture error: {e}. Press 'r' to retry or 'q' to quit."
            raise CameraError(str(e))
    
    def next_preset(self):
        """Switch to the next available character preset."""
        current_idx = self.presets.index(self.preset)
        next_idx = (current_idx + 1) % len(self.presets)
        self.preset = self.presets[next_idx]
        self.converter = self.create_converter()
    
    def next_color_scheme(self):
        """Switch to the next available color scheme."""
        current_idx = self.color_schemes.index(self.color_scheme)
        next_idx = (current_idx + 1) % len(self.color_schemes)
        self.color_scheme = self.color_schemes[next_idx]
        self.converter = self.create_converter()
    
    def toggle_status(self):
        """Toggle the status display."""
        self.show_status = not self.show_status
        # Recreate converter to adjust for status bar height
        self.converter = self.create_converter()
    
    def toggle_help(self):
        """Toggle the help display."""
        self.show_help = not self.show_help
    
    def set_frame_rate(self, fps: float):
        """Set the frame rate.
        
        Args:
            fps: Target frames per second
        """
        self.frame_rate = fps
    
    def retry_camera(self):
        """Attempt to reinitialize the camera."""
        try:
            if self.cap is not None:
                self.cap.release()
            self.setup()
            self.error_message = None
        except Exception as e:
            self.error_message = f"Camera retry failed: {e}. Press 'r' to retry again or 'q' to quit."
    
    def handle_keyboard(self) -> bool:
        """Handle keyboard input.
        
        Returns:
            bool: True to continue running, False to exit
        """
        # Check if there's input available
        if select.select([sys.stdin], [], [], 0.0)[0]:
            try:
                key = sys.stdin.read(1)
                if key == 'q':
                    return False
                elif key == 'p':
                    self.next_preset()
                elif key == 's':
                    self.next_color_scheme()
                elif key == 't':
                    self.toggle_status()
                elif key == 'h':
                    self.toggle_help()
                elif key == 'f':
                    self.set_frame_rate(15.0)
                elif key == 'w':
                    self.set_frame_rate(5.0)
                elif key == 'r' and self.error_message is not None:
                    self.retry_camera()
            except Exception as e:
                self.error_message = f"Input error: {e}"
        return True
    
    def update_performance_stats(self):
        """Update performance statistics."""
        current_time = time.time()
        
        # Update frame timing
        if self.last_frame_time > 0:
            frame_time = current_time - self.last_frame_time
            self.frame_times[self.frame_time_idx] = frame_time
            self.frame_time_idx = (self.frame_time_idx + 1) % len(self.frame_times)
            
            # Calculate actual FPS from rolling average
            actual_frame_time = np.mean(self.frame_times[self.frame_times > 0])
            self.actual_fps = 1.0 / actual_frame_time if actual_frame_time > 0 else 0.0
        
        self.last_frame_time = current_time
        
        # Update CPU and memory usage (every 30 frames)
        if self.frame_num % 30 == 0:
            self.cpu_usage = self.process.cpu_percent()
            self.memory_usage = self.process.memory_info().rss / 1024 / 1024  # MB
    
    def print_display(self):
        """Print the current display using ANSI control codes."""
        try:
            width, height = self.terminal_size
            
            # Move cursor to home position
            print("\033[H", end="")
            
            if self.error_message is not None:
                # Display error message
                print("\033[31m")  # Red text
                print(self.error_message.center(width))
                print("\033[0m")  # Reset color
                return
            
            try:
                # Get ASCII art from converter
                frame_start = time.time()
                ascii_frame = self.converter.convert_frame(self.capture_frame())
                frame_time = time.time() - frame_start
                
                lines = ascii_frame.split('\n')
                
                # Print each line with line numbers
                for i, line in enumerate(lines):
                    # Add line number if it's a multiple of 5
                    prefix = f"\033[36m{i:2d}\033[0m " if i % 5 == 0 else "   "
                    # Print line with clear to end
                    print(f"{prefix}{line}\033[K", end="")
                    # Move cursor to next line
                    print("\033[1E", end="")
                
                # Clear any remaining lines
                for i in range(len(lines), height - 1):
                    print("\033[K", end="")
                    print("\033[1E", end="")
                
                # Print status at the bottom if enabled
                if self.show_status:
                    # Create status line with size and current settings
                    status_parts = [
                        f"Size: {width}×{height}",
                        f"Target FPS: {self.frame_rate:.1f}",
                        f"Actual FPS: {self.actual_fps:.1f}",
                        f"CPU: {self.cpu_usage:.1f}%",
                        f"Mem: {self.memory_usage:.1f}MB",
                        f"Frame: {frame_time*1000:.1f}ms",
                        f"Preset: {self.preset}",
                        f"Scheme: {self.color_scheme}"
                    ]
                    
                    # Add controls if help is enabled
                    if self.show_help:
                        controls = " | ".join(f"{k}: {v}" for k, v in self.CONTROLS.items())
                        status_parts.append(controls)
                    
                    # Join all parts with separators
                    status_line = " | ".join(status_parts)
                    
                    # Calculate available width (accounting for padding)
                    available_width = width - 2  # -2 for padding
                    
                    # Truncate status line if too long
                    if len(status_line) > available_width:
                        status_line = status_line[:available_width-3] + "..."
                    
                    # Print centered status line
                    print(f"\033[K{status_line.center(width)}", end="")
                
                # Update performance stats
                self.frame_num += 1
                self.update_performance_stats()
            except CameraError:
                # Camera errors are handled via error_message
                pass
            except Exception as e:
                self.error_message = f"Display error: {e}. Press 'r' to retry or 'q' to quit."
            
            # Flush output
            sys.stdout.flush()
        except Exception as e:
            # Terminal errors
            self.error_message = f"Terminal error: {e}. Press 'q' to quit."
    
    def run(self):
        """Run the ASCII webcam viewer."""
        old_settings = None
        try:
            self.setup()
            # Save terminal settings
            old_settings = termios.tcgetattr(sys.stdin)
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())
            
            # Initialize frame timing
            frame_interval = 1.0 / self.frame_rate  # Use dynamic frame rate
            last_frame_time = 0
            last_size = self.terminal_size
            
            running = True
            while running:
                try:
                    current_time = time.time()
                    
                    # Update frame interval based on current frame rate
                    frame_interval = 1.0 / self.frame_rate
                    
                    # Check if it's time for next frame
                    if current_time - last_frame_time >= frame_interval:
                        # Only update display if terminal size changed or it's time for next frame
                        current_size = self.get_terminal_size()
                        if current_size != last_size:
                            self.terminal_size = current_size
                            self.converter = self.create_converter()
                            last_size = current_size
                        
                        # Update display
                        self.print_display()
                        last_frame_time = current_time
                    
                    # Handle keyboard input with shorter timeout
                    running = self.handle_keyboard()
                    
                    # Small sleep to prevent CPU spinning
                    time.sleep(0.01)
                except Exception as e:
                    self.error_message = f"Runtime error: {e}. Press 'r' to retry or 'q' to quit."
                    time.sleep(1)  # Prevent error message flood
                
        except KeyboardInterrupt:
            click.echo("\nExiting...")
        except Exception as e:
            click.echo(f"\nFatal error: {e}")
        finally:
            # Restore terminal settings
            if old_settings is not None:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                except Exception:
                    pass  # Ignore terminal restoration errors
            self.cleanup()

def print_presets():
    """Print available character presets and color schemes."""
    # Print character presets
    presets = ASCIIConverter.available_presets()
    click.echo("Available character presets:")
    for preset in presets:
        chars = ASCIIConverter.CHAR_PRESETS[preset]
        click.echo(f"  {preset:8} - Characters: {chars}")
    
    # Print color schemes
    click.echo("\nAvailable color schemes:")
    for scheme in ASCIIConverter.available_color_schemes():
        click.echo(f"  {scheme:8} - {scheme.title()} colors")

@click.command()
@click.option('--camera', '-c', default=0, help='Camera device ID (default: 0)')
@click.option('--width', '-w', default=80, help='Width of ASCII output (default: 80)')
@click.option('--preset', '-p', default='classic', help='Character preset to use (default: classic)')
@click.option('--scheme', '-s', default='true', help='Color scheme to use (default: true)')
@click.option('--list-presets', '-l', is_flag=True, help='List available presets and color schemes and exit')
def main(camera: int, width: int, preset: str, scheme: str, list_presets: bool):
    """Real-time ASCII art webcam viewer in the terminal."""
    if list_presets:
        print_presets()
        return
    
    if preset not in ASCIIConverter.CHAR_PRESETS:
        click.echo(f"Error: Unknown preset '{preset}'")
        print_presets()
        return
    
    if scheme not in ASCIIConverter.COLOR_SCHEMES:
        click.echo(f"Error: Unknown color scheme '{scheme}'")
        print_presets()
        return
    
    app = ASCIIWebcam(camera_id=camera, preset=preset, color_scheme=scheme)
    app.run()

if __name__ == '__main__':
    main() 