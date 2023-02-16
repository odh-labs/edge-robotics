"""Code for handling live streams, reading from Videos and writing Videos.
"""
from .streamer import streamer
from .reader import VideoReader, VideoReaderThreaded
from .writer import VideoWriter
from .chunker import StreamChunker

__version__ = "1.0.0"
