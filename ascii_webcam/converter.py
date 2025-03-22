"""ASCII conversion module for transforming webcam frames to ASCII art."""

import numpy as np
import cv2
from rich.text import Text
from rich.style import Style
from typing import Dict, Callable, Tuple, Optional
from functools import lru_cache

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
        'true': lambda b, g, r: (r, g, b),  # True colors from webcam
        'neon': lambda b, g, r: (
            min(int(r * 1.4), 255),
            min(int(g * 1.4), 255),
            min(int(b * 1.2), 255)
        ),  # Brighter, more vibrant
        'matrix': lambda b, g, r: (0, min(int(g * 1.5), 255), 0),  # Green only, Matrix style
        'vintage': lambda b, g, r: (
            min(int(r * 1.2), 255),
            min(int(g * 1.2), 255),
            max(int(b * 0.8), 0)
        ),  # Sepia-like tones
        'cyberpunk': lambda b, g, r: (
            min(int(b * 1.4), 255),
            min(int(g * 1.2), 255),
            min(int(r * 1.6), 255)
        ),  # Purple/pink hues
    }
    
    def __init__(self, preset: str = 'classic', width: int = 80, height: int = None, color_scheme: str = 'true'):
        """Initialize the ASCII converter.
        
        Args:
            preset: Name of the character preset to use
            width: Target width of ASCII output
            height: Target height of ASCII output (optional)
            color_scheme: Name of the color scheme to use
        """
        if preset not in self.CHAR_PRESETS:
            raise ValueError(f"Unknown preset '{preset}'. Available presets: {list(self.CHAR_PRESETS.keys())}")
        if color_scheme not in self.COLOR_SCHEMES:
            raise ValueError(f"Unknown color scheme '{color_scheme}'. Available schemes: {list(self.COLOR_SCHEMES.keys())}")
        
        self.chars = self.CHAR_PRESETS[preset]
        self.width = width
        self.height = height
        self.char_range = len(self.chars) - 1
        self.color_scheme = self.COLOR_SCHEMES[color_scheme]
        
        # Cache for frame dimensions
        self._last_frame_dims: Optional[Tuple[int, int]] = None
        self._last_target_dims: Optional[Tuple[int, int]] = None
        
        # Pre-compute character array for faster mapping
        self._char_array = np.array(list(self.chars))
        
        # Pre-compute ANSI color code template
        self._color_template = "\033[38;2;{};{};{}m{}"
        
        # Pre-allocate buffers for color processing
        self._color_buffer = np.zeros((3,), dtype=np.int32)
        
        # Create vectorized color scheme function
        if color_scheme == 'true':
            self._color_func_vec = lambda frame: frame[..., ::-1]  # Just swap BGR to RGB
        elif color_scheme == 'matrix':
            self._color_func_vec = lambda frame: np.stack([
                np.zeros_like(frame[..., 0]),
                np.minimum(frame[..., 1] * 1.5, 255),
                np.zeros_like(frame[..., 2])
            ], axis=-1)
        else:
            # For other schemes, create a vectorized version
            self._color_func_vec = np.vectorize(
                self.color_scheme,
                signature='(n)->(n)',
                otypes=[np.int32]
            )
    
    @classmethod
    def available_presets(cls) -> list[str]:
        """Get list of available character presets."""
        return list(cls.CHAR_PRESETS.keys())
    
    @classmethod
    def available_color_schemes(cls) -> list[str]:
        """Get list of available color schemes."""
        return list(cls.COLOR_SCHEMES.keys())
    
    @lru_cache(maxsize=32)
    def _calculate_dimensions(self, frame_width: int, frame_height: int) -> Tuple[int, int]:
        """Calculate target dimensions for frame resizing.
        
        Args:
            frame_width: Original frame width
            frame_height: Original frame height
        
        Returns:
            Tuple of (new_width, new_height)
        """
        aspect_ratio = frame_height / frame_width
        
        # Calculate target dimensions
        new_width = min(self.width, frame_width)  # Don't upscale beyond original size
        
        if self.height is not None:
            # If height is specified, use it as a constraint
            new_height = min(self.height, frame_height)
            # Adjust width to maintain aspect ratio if needed
            width_by_height = int(new_height / aspect_ratio / 0.45)  # 0.45 for terminal char aspect
            new_width = min(new_width, width_by_height)
        else:
            # Use width to determine height, accounting for terminal character aspect ratio
            new_height = int(new_width * aspect_ratio * 0.45)
        
        # Ensure minimum dimensions
        new_width = max(new_width, 10)
        new_height = max(new_height, 5)
        
        return new_width, new_height
    
    def _resize_frame(self, frame: np.ndarray) -> np.ndarray:
        """Resize the frame to match terminal dimensions while maintaining aspect ratio.
        
        Args:
            frame: BGR image as numpy array
        
        Returns:
            Resized frame as numpy array
        """
        frame_height, frame_width = frame.shape[:2]
        
        # Check if dimensions have changed
        if (self._last_frame_dims != (frame_width, frame_height) or
            self._last_target_dims != (self.width, self.height)):
            # Calculate new dimensions
            new_width, new_height = self._calculate_dimensions(frame_width, frame_height)
            self._last_frame_dims = (frame_width, frame_height)
            self._last_target_dims = (self.width, self.height)
        else:
            # Use cached dimensions
            new_width, new_height = self._calculate_dimensions(frame_width, frame_height)
        
        # Resize using area interpolation for better quality
        return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    def _frame_to_grayscale(self, frame: np.ndarray) -> np.ndarray:
        """Convert frame to grayscale for intensity mapping."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    def _map_intensity_to_chars(self, intensity: np.ndarray) -> np.ndarray:
        """Map grayscale intensities to ASCII characters."""
        # Normalize intensity to match char range and convert to indices
        char_indices = (intensity / 255 * self.char_range).astype(np.int32)
        # Map indices to characters using pre-computed array
        return self._char_array[char_indices]
    
    def _create_ansi_text(self, frame: np.ndarray, ascii_chars: np.ndarray) -> str:
        """Create a string with ANSI color codes for the ASCII art.
        
        Args:
            frame: BGR image as numpy array
            ascii_chars: Array of ASCII characters
        
        Returns:
            String with ANSI color codes
        """
        height, width = ascii_chars.shape
        
        # Apply color scheme to entire frame at once
        colors = self._color_func_vec(frame)
        
        # Pre-allocate list for lines
        lines = []
        line_buffer = []
        
        # Process each line
        for y in range(height):
            # Clear line buffer
            line_buffer.clear()
            
            # Process each character in the line
            for x in range(width):
                r, g, b = colors[y, x]
                line_buffer.append(self._color_template.format(r, g, b, ascii_chars[y, x]))
            
            # Add reset code and join line
            line_buffer.append("\033[0m")
            lines.append("".join(line_buffer))
        
        # Join all lines with newlines
        return "\n".join(lines)
    
    def convert_frame(self, frame: np.ndarray) -> str:
        """Convert a video frame to colored ASCII art.
        
        Args:
            frame: BGR image as numpy array
        
        Returns:
            String with ANSI color codes for the ASCII art
        """
        # Resize frame to target dimensions
        resized = self._resize_frame(frame)
        
        # Convert to grayscale for character mapping
        gray = self._frame_to_grayscale(resized)
        
        # Map intensities to ASCII characters
        ascii_chars = self._map_intensity_to_chars(gray)
        
        # Create colored text with ANSI codes
        return self._create_ansi_text(resized, ascii_chars) 