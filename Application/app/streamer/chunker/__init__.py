"""Read Live Stream and save them as chunks to be
read later by the main thread. Use it if your pipeline's
processing speed is significantly slower than input stream's FPS.
"""
from .chunker import StreamChunker
