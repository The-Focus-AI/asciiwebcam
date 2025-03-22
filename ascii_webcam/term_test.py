#!/usr/bin/env python3
"""
Terminal testing tool for the ASCII webcam project.
Tests terminal sizing, layout, and keyboard input handling.
"""
import os
import signal
import time
import sys
import threading
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
import click

class TerminalTest:
    def __init__(self):
        """Initialize the terminal test application."""
        # Initialize Rich console with default settings
        self.console = Console()
        self.running = True
        self.width, self.height = 80, 24  # Default fallback size
        
        try:
            self.width, self.height = os.get_terminal_size()
        except (OSError, IOError):
            # Use the console size if available, otherwise stick with defaults
            self.width = self.console.width or self.width
            self.height = self.console.height or self.height
        
        # Set up signal handler for graceful exit with Ctrl+C
        signal.signal(signal.SIGINT, self.handle_exit)
    
    def get_terminal_size(self):
        """Get the current terminal size."""
        try:
            self.width, self.height = os.get_terminal_size()
        except (OSError, IOError):
            # Use the console size if available
            new_width = self.console.width
            new_height = self.console.height
            
            if new_width and new_height:
                self.width, self.height = new_width, new_height
            # Otherwise keep the previous values
            
        return self.width, self.height
    
    def display_terminal_info(self):
        """Display terminal size information and borders."""
        width, height = self.get_terminal_size()
        
        # Create layout
        layout = Layout()
        layout.split(
            Layout(name="main", ratio=3),
            Layout(name="status", ratio=1)
        )
        
        # Main content panel
        main_content = Text(f"Terminal Size: {width}x{height}")
        main_panel = Panel(
            main_content,
            title="Main Window",
            border_style="green",
            padding=(1, 2)
        )
        
        # Status panel
        status_content = Text("Press 'q' to quit")
        status_panel = Panel(
            status_content,
            title="Status Window",
            border_style="blue",
            padding=(1, 2)
        )
        
        # Set panels to layout
        layout["main"].update(main_panel)
        layout["status"].update(status_panel)
        
        # Print the layout
        self.console.print(layout)
    
    def handle_exit(self, sig, frame):
        """Handle exit signals."""
        self.running = False
    
    def input_listener(self):
        """Thread function to listen for the 'q' key."""
        while self.running:
            # Use click.getchar() for non-blocking key input
            try:
                # This is still blocking, but in a separate thread
                key = click.getchar(echo=False)
                if key.lower() == 'q':
                    self.running = False
                    break
            except Exception:
                # If getchar fails, sleep a bit and try again
                time.sleep(0.1)
    
    def run(self):
        """Main loop to monitor terminal size."""
        try:
            # Start input listener thread
            input_thread = threading.Thread(target=self.input_listener, daemon=True)
            input_thread.start()
            
            while self.running:
                # Clear screen and move cursor to top-left
                self.console.clear()
                
                # Display updated terminal info with layout
                self.display_terminal_info()
                
                # Brief pause to prevent high CPU usage
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Make sure we exit cleanly
            self.running = False

if __name__ == "__main__":
    term_test = TerminalTest()
    term_test.run()