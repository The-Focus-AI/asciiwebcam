"""ASCII conversion module for transforming webcam frames to ASCII art."""

import numpy as np
import cv2
from rich.text import Text
from rich.style import Style
from typing import Dict, Callable

class ASCIIConverter:
    """Converts image frames to ASCII art with color support."""
    
    # Character set presets from darkest to lightest
    CHAR_PRESETS: Dict[str, str] = {
        'classic': ' .:-=+*#%@',  # Classic ASCII art style
        'blocks': '░▒▓█',         # Unicode blocks
        'simple': ' .*#',         # Minimal set for high contrast
        'detailed': ' .",:;!~*=#$@',  # More gradual transitions
        'matrix': '01',           # Binary style
        'dots': '·•●',           # Dot-based style
        'lines': '─│┌┐└┘├┤┬┴┼',   # Line drawing characters
    }
    
    # Color scheme functions
    COLOR_SCHEMES = {
        'true': lambda b, g, r: f"rgb({r},{g},{b})",  # True colors from webcam
        'neon': lambda b, g, r: f"rgb({min(int(r * 1.4), 255)},{min(int(g * 1.4), 255)},{min(int(b * 1.2), 255)})",  # Brighter, more vibrant
        'matrix': lambda b, g, r: f"rgb(0,{min(int(g * 1.5), 255)},0)",  # Green only, Matrix style
        'vintage': lambda b, g, r: f"rgb({min(int(r * 1.2), 255)},{min(int(g * 1.2), 255)},{max(int(b * 0.8), 0)})",  # Sepia-like tones
        'cyberpunk': lambda b, g, r: f"rgb({min(int(b * 1.4), 255)},{min(int(g * 1.2), 255)},{min(int(r * 1.6), 255)})",  # Purple/pink hues
    }
    
    def __init__(self, preset: str = 'classic', width: int = 80, color_scheme: str = 'true'):
        """Initialize the ASCII converter.
        
        Args:
            preset: Name of the character preset to use
            width: Target width of ASCII output
            color_scheme: Name of the color scheme to use
        """
        if preset not in self.CHAR_PRESETS:
            raise ValueError(f"Unknown preset '{preset}'. Available presets: {list(self.CHAR_PRESETS.keys())}")
        if color_scheme not in self.COLOR_SCHEMES:
            raise ValueError(f"Unknown color scheme '{color_scheme}'. Available schemes: {list(self.COLOR_SCHEMES.keys())}")
        
        self.chars = self.CHAR_PRESETS[preset]
        self.width = width
        self.char_range = len(self.chars) - 1
        self.color_scheme = self.COLOR_SCHEMES[color_scheme]
    
    @classmethod
    def available_presets(cls) -> list[str]:
        """Get list of available character presets."""
        return list(cls.CHAR_PRESETS.keys())
    
    @classmethod
    def available_color_schemes(cls) -> list[str]:
        """Get list of available color schemes."""
        return list(cls.COLOR_SCHEMES.keys())
    
    def _resize_frame(self, frame: np.ndarray) -> np.ndarray:
        """Resize the frame to match terminal width while maintaining aspect ratio."""
        height, width = frame.shape[:2]
        aspect_ratio = height / width
        new_width = self.width
        new_height = int(new_width * aspect_ratio * 0.5)  # * 0.5 to account for terminal char height
        return cv2.resize(frame, (new_width, new_height))
    
    def _frame_to_grayscale(self, frame: np.ndarray) -> np.ndarray:
        """Convert frame to grayscale for intensity mapping."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    def _map_intensity_to_chars(self, intensity: np.ndarray) -> np.ndarray:
        """Map grayscale intensities to ASCII characters."""
        # Normalize intensity to match char range
        char_indices = (intensity / 255 * self.char_range).astype(int)
        # Map indices to characters
        return np.array(list(self.chars))[char_indices]
    
    def _create_rich_text(self, frame: np.ndarray, ascii_chars: np.ndarray) -> Text:
        """Create Rich Text with color information."""
        text = Text()
        height, width = ascii_chars.shape
        
        for y in range(height):
            for x in range(width):
                # Get BGR color from original frame
                b, g, r = frame[y, x]
                # Apply color scheme
                color = self.color_scheme(b, g, r)
                # Create style with color
                style = Style(color=color)
                # Add character with color
                text.append(ascii_chars[y, x], style=style)
            text.append("\n")
        
        return text
    
    def convert_frame(self, frame: np.ndarray) -> Text:
        """Convert a video frame to colored ASCII art.
        
        Args:
            frame: BGR image as numpy array
        
        Returns:
            Rich Text object containing colored ASCII art
        """
        # Resize frame to target width
        resized = self._resize_frame(frame)
        
        # Convert to grayscale for character mapping
        gray = self._frame_to_grayscale(resized)
        
        # Map intensities to ASCII characters
        ascii_chars = self._map_intensity_to_chars(gray)
        
        # Create colored text
        return self._create_rich_text(resized, ascii_chars) 