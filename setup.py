from setuptools import setup, find_packages

setup(
    name="ascii-webcam",
    version="0.1.0",
    description="Real-time ASCII art webcam viewer in the terminal",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Will Schenk",
    author_email="wschenk@gmail.com",
    url="https://github.com/wschenk/ascii-webcam",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.11.0",
        "numpy>=2.2.4",
        "click>=8.1.8",
        "psutil>=5.9.0",
        "rich>=13.9.4",
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
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Artistic Software",
    ],
    python_requires=">=3.11",
    keywords="ascii art webcam terminal console",
) 