"""Main application module for ASCII Webcam."""

import cv2
import click
from rich.console import Console
from rich.live import Live

from .converter import ASCIIConverter
from .status import StatusDisplay

class ASCIIWebcam:
    """Main application class for ASCII Webcam viewer."""
    
    def __init__(self, camera_id: int = 0, width: int = 80, preset: str = 'classic', color_scheme: str = 'true'):
        """Initialize the ASCII Webcam viewer.
        
        Args:
            camera_id: ID of the webcam to use (default: 0)
            width: Width of ASCII output (default: 80)
            preset: Character preset to use (default: 'classic')
            color_scheme: Color scheme to use (default: 'true')
        """
        self.camera_id = camera_id
        self.cap = None
        self.console = Console()
        self.converter = ASCIIConverter(preset=preset, width=width, color_scheme=color_scheme)
        self.status = StatusDisplay(self.console)
        self.preset = preset
        self.color_scheme = color_scheme
        
    def setup(self):
        """Set up the webcam capture."""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise click.ClickException(f"Could not open camera {self.camera_id}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap is not None:
            self.cap.release()
    
    def capture_frame(self):
        """Capture a frame from the webcam."""
        ret, frame = self.cap.read()
        if not ret:
            raise click.ClickException("Failed to capture frame")
        return frame
    
    def run(self):
        """Run the ASCII webcam viewer."""
        try:
            self.setup()
            with Live(refresh_per_second=30) as live:
                while True:
                    frame = self.capture_frame()
                    # Convert frame to ASCII art
                    ascii_frame = self.converter.convert_frame(frame)
                    # Create display with status bar
                    display = self.status.create_display(
                        ascii_frame,
                        self.preset,
                        self.color_scheme
                    )
                    live.update(display)
        except KeyboardInterrupt:
            click.echo("\nExiting...")
        finally:
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
    
    app = ASCIIWebcam(camera_id=camera, width=width, preset=preset, color_scheme=scheme)
    app.run()

if __name__ == '__main__':
    main() 