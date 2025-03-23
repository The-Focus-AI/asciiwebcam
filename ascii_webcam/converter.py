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
            np.minimum(r * 1.4, 255),
            np.minimum(g * 1.4, 255),
            np.minimum(b * 1.2, 255)
        ),  # Brighter, more vibrant
        'matrix': lambda b, g, r: (
            np.zeros_like(b),
            np.minimum(g * 1.5, 255),
            np.zeros_like(r)
        ),  # Green only, Matrix style
        'vintage': lambda b, g, r: (
            np.minimum(r * 1.2, 255),
            np.minimum(g * 1.2, 255),
            np.maximum(b * 0.8, 0)
        ),  # Sepia-like tones
        'cyberpunk': lambda b, g, r: (
            np.minimum(b * 1.4, 255),
            np.minimum(g * 1.2, 255),
            np.minimum(r * 1.6, 255)
        ),  # Purple/pink hues
    }
    
    def __init__(self, preset: str = 'classic', width: int = 80, height: int = None, color_scheme: str = 'true'):
        """Initialize the ASCII converter."""
        if preset not in self.CHAR_PRESETS:
            raise ValueError(f"Unknown preset '{preset}'. Available presets: {list(self.CHAR_PRESETS.keys())}")
        if color_scheme not in self.COLOR_SCHEMES:
            raise ValueError(f"Unknown color scheme '{color_scheme}'. Available schemes: {list(self.COLOR_SCHEMES.keys())}")
        
        self.chars = self.CHAR_PRESETS[preset]
        self.width = width
        self.height = height
        self.char_range = len(self.chars) - 1
        self.color_scheme_name = color_scheme  # Store the name
        
        # Cache for frame dimensions and buffers
        self._last_frame_dims: Optional[Tuple[int, int]] = None
        self._last_target_dims: Optional[Tuple[int, int]] = None
        self._resized_buffer: Optional[np.ndarray] = None
        self._gray_buffer: Optional[np.ndarray] = None
        self._char_buffer: Optional[np.ndarray] = None
        self._color_buffer: Optional[np.ndarray] = None
        self._intensity_buffer: Optional[np.ndarray] = None
        self._char_indices_buffer: Optional[np.ndarray] = None
        
        # Pre-compute character array for faster mapping
        self._char_array = np.array(list(self.chars))
        
        # Pre-compute ANSI color code template and parts
        self._color_start = "\033[38;2;"
        self._color_sep = ";"
        self._color_end = "m"
        self._color_reset = "\033[0m"
        
        # Pre-allocate string builders for each line
        self._line_builders = []
        self._line_parts = []  # For building lines more efficiently
        
        # Create optimized color scheme function
        self._setup_color_function(color_scheme)
    
    def _setup_color_function(self, color_scheme: str):
        """Set up the optimized color function for the given scheme."""
        if color_scheme == 'true':
            # Simple BGR to RGB swap with buffer reuse
            def true_color(frame):
                if self._color_buffer is None or self._color_buffer.shape != frame.shape:
                    self._color_buffer = np.empty_like(frame, dtype=np.uint8)
                # Reorder channels into pre-allocated buffer
                self._color_buffer[..., 0] = frame[..., 2]  # R = B
                self._color_buffer[..., 1] = frame[..., 1]  # G = G
                self._color_buffer[..., 2] = frame[..., 0]  # B = R
                return self._color_buffer
            self._color_func_vec = true_color
        elif color_scheme == 'matrix':
            # Optimized matrix effect
            def matrix_color(frame):
                result = np.zeros_like(frame, dtype=np.uint8)
                result[..., 1] = np.minimum(frame[..., 1] * 1.5, 255).astype(np.uint8)
                return result
            self._color_func_vec = matrix_color
        else:
            # Optimized color scheme with pre-allocated buffer
            color_func = self.COLOR_SCHEMES[color_scheme]  # Get the color function directly
            def optimized_color_func(frame):
                if self._color_buffer is None or self._color_buffer.shape != frame.shape:
                    self._color_buffer = np.empty_like(frame, dtype=np.uint8)
                
                # Process each color channel separately for better vectorization
                b, g, r = frame[..., 0].astype(np.float32), frame[..., 1].astype(np.float32), frame[..., 2].astype(np.float32)
                
                # Apply color function and combine channels
                r_out, g_out, b_out = color_func(b, g, r)
                
                # Stack channels and ensure proper type
                self._color_buffer[..., 0] = b_out.astype(np.uint8)
                self._color_buffer[..., 1] = g_out.astype(np.uint8)
                self._color_buffer[..., 2] = r_out.astype(np.uint8)
                
                return self._color_buffer
            self._color_func_vec = optimized_color_func
    
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
        """Resize the frame to match terminal dimensions while maintaining aspect ratio."""
        frame_height, frame_width = frame.shape[:2]
        
        # Check if dimensions have changed
        if (self._last_frame_dims != (frame_width, frame_height) or
            self._last_target_dims != (self.width, self.height)):
            # Calculate new dimensions
            new_width, new_height = self._calculate_dimensions(frame_width, frame_height)
            self._last_frame_dims = (frame_width, frame_height)
            self._last_target_dims = (self.width, self.height)
            
            # Reallocate buffers if needed
            if (self._resized_buffer is None or 
                self._resized_buffer.shape[:2] != (new_height, new_width)):
                self._resized_buffer = np.empty((new_height, new_width, 3), dtype=np.uint8)
                self._gray_buffer = np.empty((new_height, new_width), dtype=np.uint8)
                self._char_buffer = np.empty((new_height, new_width), dtype='<U1')
                self._color_buffer = np.empty((new_height, new_width, 3), dtype=np.uint8)
                self._intensity_buffer = np.empty((new_height, new_width), dtype=np.float32)
                self._char_indices_buffer = np.empty((new_height, new_width), dtype=np.int32)
                self._line_builders = [''] * new_height
                self._line_parts = [[] for _ in range(new_height)]
        else:
            new_width, new_height = self._calculate_dimensions(frame_width, frame_height)
        
        # Resize into pre-allocated buffer
        cv2.resize(frame, (new_width, new_height), dst=self._resized_buffer, interpolation=cv2.INTER_AREA)
        return self._resized_buffer
    
    def _frame_to_grayscale(self, frame: np.ndarray) -> np.ndarray:
        """Convert frame to grayscale for intensity mapping."""
        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY, dst=self._gray_buffer)
        return self._gray_buffer
    
    def _map_intensity_to_chars(self, intensity: np.ndarray) -> np.ndarray:
        """Map grayscale intensities to ASCII characters."""
        # Pre-allocate buffers if needed
        if self._char_indices_buffer is None or self._char_indices_buffer.shape != intensity.shape:
            self._char_indices_buffer = np.empty_like(intensity, dtype=np.int32)
            self._intensity_buffer = np.empty_like(intensity, dtype=np.float32)
        
        # Normalize intensity to match char range (using pre-allocated buffer)
        np.multiply(intensity, self.char_range / 255.0, out=self._intensity_buffer, dtype=np.float32)
        # First clip in float32
        np.clip(self._intensity_buffer, 0, self.char_range, out=self._intensity_buffer)
        # Then convert to int32
        np.floor(self._intensity_buffer, out=self._intensity_buffer)
        np.copyto(self._char_indices_buffer, self._intensity_buffer.astype(np.int32))
        
        # Map indices to characters using pre-computed array
        np.take(self._char_array, self._char_indices_buffer, out=self._char_buffer)
        return self._char_buffer
    
    def _create_ansi_text(self, frame: np.ndarray, ascii_chars: np.ndarray) -> str:
        """Create a string with ANSI color codes for the ASCII art."""
        height, width = ascii_chars.shape
        
        # Apply color scheme to entire frame at once
        colors = self._color_func_vec(frame)
        
        # Ensure we have enough line parts
        if len(self._line_parts) < height:
            self._line_parts = [[] for _ in range(height)]
        
        # Process each line using pre-allocated builders
        for y in range(height):
            parts = self._line_parts[y]
            parts.clear()
            
            # Build line with minimal string operations
            for x in range(width):
                r, g, b = colors[y, x]
                parts.extend((
                    self._color_start,
                    str(r), self._color_sep,
                    str(g), self._color_sep,
                    str(b), self._color_end,
                    ascii_chars[y, x]
                ))
            parts.append(self._color_reset)
            self._line_builders[y] = ''.join(parts)
        
        # Join all lines with newlines
        return '\n'.join(self._line_builders)
    
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