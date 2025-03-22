"""Tests for the status display module."""

import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from ascii_webcam.status import StatusDisplay

def test_status_display_init():
    """Test StatusDisplay initialization."""
    console = Console()
    status = StatusDisplay(console)
    
    assert status.console == console
    assert status.frame_count == 0
    assert status.fps == 0.0
    assert isinstance(status.layout, Layout)

def test_calculate_fps():
    """Test FPS calculation."""
    console = Console()
    status = StatusDisplay(console)
    
    # Simulate frames over time
    status.last_frame_time = time.time() - 1.0  # Set last frame time to 1 second ago
    status.frame_count = 30
    
    status._calculate_fps()
    assert status.fps == 30.0  # Should be approximately 30 FPS

def test_create_status_bar():
    """Test status bar creation."""
    console = Console()
    status = StatusDisplay(console)
    
    panel = status.create_status_bar("classic", "true")
    assert isinstance(panel, Panel)
    assert "classic" in panel.renderable.renderable.rows[0][0]
    assert "true" in panel.renderable.renderable.rows[0][1]
    assert "FPS" in panel.renderable.renderable.rows[0][2]

def test_create_display():
    """Test full display creation."""
    console = Console()
    status = StatusDisplay(console)
    
    # Create a dummy ASCII frame
    ascii_frame = Text("Test Frame")
    
    layout = status.create_display(ascii_frame, "classic", "true")
    assert isinstance(layout, Layout)
    assert layout["main"].renderable == ascii_frame
    assert isinstance(layout["status"].renderable, Panel) 