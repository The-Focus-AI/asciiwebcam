"""Unit tests for the ASCII converter module."""
import pytest
import numpy as np
from ascii_webcam.converter import ASCIIConverter

def test_converter_init():
    """Test converter initialization with default parameters."""
    converter = ASCIIConverter()
    assert converter.width == 80
    assert converter.height is None
    assert converter.color_scheme_name == 'true'
    assert converter._color_buffer is None

def test_converter_init_invalid_preset():
    """Test converter initialization with invalid preset."""
    with pytest.raises(ValueError, match="Unknown preset"):
        ASCIIConverter(preset='invalid')

def test_converter_init_invalid_color_scheme():
    """Test converter initialization with invalid color scheme."""
    with pytest.raises(ValueError, match="Unknown color scheme"):
        ASCIIConverter(color_scheme='invalid')

def test_color_scheme_true(test_frame):
    """Test true color scheme (BGR to RGB conversion)."""
    converter = ASCIIConverter(color_scheme='true')
    result = converter._color_func_vec(test_frame)
    
    # Check specific colors are correctly converted
    assert np.array_equal(result[0, 0], [0, 0, 0])      # Black stays black
    assert np.array_equal(result[0, 1], [255, 255, 255]) # White stays white
    assert np.array_equal(result[0, 2], [0, 255, 0])     # Green stays green
    assert np.array_equal(result[0, 3], [255, 0, 0])     # BGR Red becomes RGB Red

def test_color_scheme_matrix(test_frame):
    """Test matrix color scheme (green channel only)."""
    converter = ASCIIConverter(color_scheme='matrix')
    result = converter._color_func_vec(test_frame)
    
    # Check only green channel is preserved and enhanced
    assert result[0, 0, 0] == 0  # No blue
    assert result[0, 0, 2] == 0  # No red
    assert result[0, 2, 1] == min(int(255 * 1.5), 255)  # Enhanced green

def test_color_scheme_neon(test_frame):
    """Test neon color scheme (enhanced brightness)."""
    converter = ASCIIConverter(color_scheme='neon')
    result = converter._color_func_vec(test_frame)
    
    # Test brightness enhancement
    original_brightness = np.mean(test_frame)
    neon_brightness = np.mean(result)
    assert neon_brightness > original_brightness
    
    # Check values are properly clipped
    assert np.all(result <= 255)
    assert np.all(result >= 0)

def test_color_scheme_vintage(test_frame):
    """Test vintage color scheme (sepia effect)."""
    converter = ASCIIConverter(color_scheme='vintage')
    result = converter._color_func_vec(test_frame)
    
    # Check sepia characteristics
    assert np.mean(result[..., 0]) < np.mean(result[..., 1])  # Blue is reduced
    assert np.mean(result[..., 1]) <= np.mean(result[..., 2])  # Red is enhanced

def test_color_scheme_cyberpunk(test_frame):
    """Test cyberpunk color scheme (purple/pink hues)."""
    converter = ASCIIConverter(color_scheme='cyberpunk')
    result = converter._color_func_vec(test_frame)
    
    # Check purple/pink characteristics
    assert np.mean(result[..., 0]) > np.mean(test_frame[..., 0])  # Enhanced blue
    assert np.mean(result[..., 2]) > np.mean(test_frame[..., 2])  # Enhanced red

def test_color_buffer_reuse():
    """Test that color buffers are reused for efficiency."""
    converter = ASCIIConverter()
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    
    # First call should create buffer
    result1 = converter._color_func_vec(frame)
    buffer_id1 = id(result1)
    
    # Second call should reuse buffer
    result2 = converter._color_func_vec(frame)
    buffer_id2 = id(result2)
    
    assert buffer_id1 == buffer_id2

def test_color_buffer_resize():
    """Test that color buffer is reallocated when frame size changes."""
    converter = ASCIIConverter()
    frame1 = np.zeros((10, 10, 3), dtype=np.uint8)
    frame2 = np.zeros((20, 20, 3), dtype=np.uint8)
    
    # Process first frame
    result1 = converter._color_func_vec(frame1)
    shape1 = result1.shape
    
    # Process second frame with different dimensions
    result2 = converter._color_func_vec(frame2)
    shape2 = result2.shape
    
    assert shape1 != shape2
    assert result2.shape == frame2.shape

def test_type_safety():
    """Test type safety in color processing."""
    converter = ASCIIConverter()
    
    # Test with different input types
    frame_uint8 = np.zeros((10, 10, 3), dtype=np.uint8)
    frame_float = np.zeros((10, 10, 3), dtype=np.float32)
    
    result_uint8 = converter._color_func_vec(frame_uint8)
    result_float = converter._color_func_vec(frame_float)
    
    assert result_uint8.dtype == np.uint8
    assert result_float.dtype == np.uint8  # Should convert to uint8 