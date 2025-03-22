"""Tests for the ASCII converter module."""

import numpy as np
import pytest
from rich.text import Text

from ascii_webcam.converter import ASCIIConverter

def test_converter_init():
    """Test ASCIIConverter initialization."""
    converter = ASCIIConverter()
    assert converter.chars == ASCIIConverter.CHAR_PRESETS['classic']
    assert converter.width == 80
    assert converter.char_range == len(ASCIIConverter.CHAR_PRESETS['classic']) - 1

def test_converter_invalid_preset():
    """Test ASCIIConverter with invalid preset."""
    with pytest.raises(ValueError) as exc_info:
        ASCIIConverter(preset='invalid')
    assert 'Unknown preset' in str(exc_info.value)

def test_available_presets():
    """Test getting available presets."""
    presets = ASCIIConverter.available_presets()
    assert 'classic' in presets
    assert 'blocks' in presets
    assert 'matrix' in presets
    assert len(presets) == len(ASCIIConverter.CHAR_PRESETS)

def test_converter_preset_chars():
    """Test different character presets."""
    # Test each preset
    for preset, chars in ASCIIConverter.CHAR_PRESETS.items():
        converter = ASCIIConverter(preset=preset)
        assert converter.chars == chars
        assert converter.char_range == len(chars) - 1

def test_resize_frame():
    """Test frame resizing."""
    converter = ASCIIConverter(width=40)
    # Create a simple test frame
    frame = np.zeros((100, 200, 3), dtype=np.uint8)
    resized = converter._resize_frame(frame)
    assert resized.shape[1] == 40  # Width matches target
    assert resized.shape[0] == 10  # Height maintains aspect ratio (with 0.5 factor)

def test_frame_to_grayscale():
    """Test grayscale conversion."""
    converter = ASCIIConverter()
    # Create a colored test frame
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    frame[:, :, 0] = 255  # Blue channel
    gray = converter._frame_to_grayscale(frame)
    assert gray.shape == (10, 10)
    assert len(gray.shape) == 2  # Single channel

def test_map_intensity_to_chars():
    """Test intensity to character mapping."""
    # Test with matrix preset (binary characters)
    converter = ASCIIConverter(preset='matrix')
    # Test with black and white intensities
    intensity = np.array([[0, 255]], dtype=np.uint8)
    chars = converter._map_intensity_to_chars(intensity)
    assert chars[0][0] == "0"  # Darkest char for black
    assert chars[0][1] == "1"  # Lightest char for white

def test_convert_frame():
    """Test full frame conversion."""
    converter = ASCIIConverter(width=2)
    # Create a simple 2x2 test frame
    frame = np.zeros((2, 2, 3), dtype=np.uint8)
    frame[0, 0] = [255, 0, 0]  # Red pixel
    frame[1, 1] = [0, 255, 0]  # Green pixel
    
    result = converter.convert_frame(frame)
    assert isinstance(result, Text)
    # Result should contain colored characters and newlines 