"""Defines a function to auto select
the type of video reader with default configs.
Doesn't use VideoReaderThreaded.
"""
from streamer.reader import VideoReader, VideoReaderThreaded
from streamer.chunker import StreamChunker
from streamer.utils.sys_colors import bcolors


def streamer(source, pre_process=None, is_pipeline_fast=True):
    """Initiate a video reader object based on
    type of the source.

    Args:
        source (str): Filename/URL of source video

        pre_process (function, optional): Preprocess to be applied before
        frame is returned.. Defaults to None.

        is_pipeline_fast(bool, optional): True if pipeline's FPS is fast or
        as fast as the streams. False otherwise.

    Returns:
        VideoReader | StreamChunker: Reader object inititated with default
        configs.
    """
    source = str(source)
    if source.isnumeric() or source.startswith('rtsp') or source.startswith(
            'http'):
        print(f"{bcolors.OKCYAN}[Streamer] Info: Initiating",
              f"{'VideoReaderT' if is_pipeline_fast else 'StreamChunker'}",
              f"for {source}...{bcolors.ENDC}")

        if is_pipeline_fast:
            return VideoReaderThreaded(
                source=source,
                pre_process=pre_process,
                skip_frames=2,
                buffer_size=3 if source.isnumeric() else None,
                restart_time=-1)

        # else
        return StreamChunker(source=source,
                             save_pre_process=pre_process,
                             skip_frames=2,
                             buffer_size=3 if source.isnumeric() else None,
                             chunk_size=5,
                             chunk_dir='../temp_chunks',
                             restart_time=-1)

    else:
        print(f"{bcolors.OKCYAN}[Streamer] Info: Initiating Video Reader for",
              f"{source}...{bcolors.ENDC}")

        return VideoReader(source=source, pre_process=pre_process)
