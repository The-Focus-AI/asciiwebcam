"""Test configuration and shared fixtures for ASCII Webcam tests."""
import os
import pytest
import numpy as np
import cv2
from unittest.mock import MagicMock
from typing import Generator, Tuple

@pytest.fixture
def mock_terminal_size() -> Tuple[int, int]:
    """Provide a consistent terminal size for tests."""
    return (80, 24)

@pytest.fixture
def mock_webcam() -> Generator[MagicMock, None, None]:
    """Create a mock webcam that returns a test frame."""
    mock = MagicMock(spec=cv2.VideoCapture)
    
    # Create a simple test frame (black and white gradient)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    for i in range(480):
        frame[i, :] = i // 2  # Create a horizontal gradient
    
    # Configure mock to return the test frame
    mock.read.return_value = (True, frame)
    mock.isOpened.return_value = True
    
    yield mock
    
    # Cleanup (simulating release)
    mock.release.assert_called_once()

@pytest.fixture
def test_frame() -> np.ndarray:
    """Provide a consistent test frame for converter tests."""
    # Create a 4x4 test frame with known values
    frame = np.zeros((4, 4, 3), dtype=np.uint8)
    frame[0, 0] = [0, 0, 0]      # Black
    frame[0, 1] = [255, 255, 255] # White
    frame[0, 2] = [0, 255, 0]     # Green
    frame[0, 3] = [0, 0, 255]     # Red
    frame[1, 0] = [255, 0, 0]     # Blue
    frame[1, 1] = [255, 255, 0]   # Cyan
    frame[1, 2] = [255, 0, 255]   # Magenta
    frame[1, 3] = [0, 255, 255]   # Yellow
    # Fill remaining with gradient
    frame[2:, :] = np.linspace(0, 255, 8).reshape(2, 4, 1).repeat(3, axis=2)
    return frame

@pytest.fixture
def mock_terminal():
    """Mock terminal environment with controlled dimensions and output capture."""
    class MockTerminal:
        def __init__(self):
            self.width = 80
            self.height = 24
            self.output = []
            self.cursor_x = 0
            self.cursor_y = 0
            
        def write(self, text: str):
            """Simulate terminal output."""
            self.output.append(text)
            
        def get_output(self) -> str:
            """Get captured output."""
            return ''.join(self.output)
            
        def clear(self):
            """Clear terminal output."""
            self.output = []
            self.cursor_x = 0
            self.cursor_y = 0
            
        def get_size(self) -> Tuple[int, int]:
            """Get terminal dimensions."""
            return (self.width, self.height)
    
    return MockTerminal()

@pytest.fixture
def temp_config(tmp_path) -> str:
    """Create a temporary configuration file."""
    config_path = tmp_path / "config.toml"
    config_path.write_text("""
    [ascii_webcam]
    camera_id = 0
    preset = "classic"
    color_scheme = "true"
    frame_rate = 15.0
    show_status = true
    show_help = true
    """)
    return str(config_path) 