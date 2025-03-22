"""Tests for the ASCII Webcam application."""

import pytest
from ascii_webcam.app import ASCIIWebcam

def test_ascii_webcam_init():
    """Test ASCIIWebcam initialization."""
    app = ASCIIWebcam()
    assert app.camera_id == 0
    assert app.cap is None

def test_ascii_webcam_custom_camera():
    """Test ASCIIWebcam with custom camera ID."""
    app = ASCIIWebcam(camera_id=1)
    assert app.camera_id == 1 