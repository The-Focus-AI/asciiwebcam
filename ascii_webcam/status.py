"""Status display module for ASCII Webcam."""

import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

class StatusDisplay:
    """Handles the status display for ASCII Webcam."""
    
    def __init__(self, console: Console):
        """Initialize the status display.
        
        Args:
            console: Rich console instance
        """
        self.console = console
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps = 0.0
        self.layout = Layout()
        
        # Create the layout
        self.layout.split(
            Layout(name="main", ratio=9),
            Layout(name="status", ratio=1)
        )
    
    def _calculate_fps(self):
        """Calculate current FPS."""
        current_time = time.time()
        self.frame_count += 1
        
        # Update FPS every second
        if current_time - self.last_frame_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_frame_time)
            self.frame_count = 0
            self.last_frame_time = current_time
    
    def create_status_bar(self, preset: str, color_scheme: str) -> Panel:
        """Create the status bar panel.
        
        Args:
            preset: Current character preset
            color_scheme: Current color scheme
        
        Returns:
            Rich Panel containing status information
        """
        self._calculate_fps()
        
        # Create status table
        table = Table.grid(padding=1)
        table.add_column("Preset", justify="left")
        table.add_column("Color", justify="left")
        table.add_column("FPS", justify="right")
        table.add_column("Help", justify="right")
        
        # Add status information
        table.add_row(
            f"Preset: {preset}",
            f"Color: {color_scheme}",
            f"FPS: {self.fps:.1f}",
            "Press '?' for help"
        )
        
        return Panel(table, title="Status", border_style="blue")
    
    def create_display(self, ascii_frame: Text, preset: str, color_scheme: str) -> Layout:
        """Create the full display with ASCII frame and status bar.
        
        Args:
            ascii_frame: The ASCII art frame
            preset: Current character preset
            color_scheme: Current color scheme
        
        Returns:
            Layout containing the frame and status bar
        """
        # Update layout sections
        self.layout["main"].update(ascii_frame)
        self.layout["status"].update(self.create_status_bar(preset, color_scheme))
        
        return self.layout 