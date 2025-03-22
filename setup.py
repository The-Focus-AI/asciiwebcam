from setuptools import setup, find_packages

setup(
    name="ascii-webcam",
    version="0.1.0",
    description="Real-time ASCII art webcam viewer in the terminal",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.11.0",
        "numpy>=2.2.4",
        "click>=8.1.8",
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "black>=24.2.0",
            "ruff>=0.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ascii-webcam=ascii_webcam.app:main",
        ],
    },
) 