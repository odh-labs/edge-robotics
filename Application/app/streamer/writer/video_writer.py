"""Contains class defintion of VideoWriter.
"""
import os
from operator import itemgetter

import cv2

from streamer.reader import VideoReader, VideoReaderThreaded
from streamer.utils.sys_colors import bcolors


class VideoWriter:
    """Write Video for any format with customizable configuration. It's basically
        a wrapper around OpenCV VideoWriter which can be easily initialize with
        VideoReader object. It also closes the video writer if any exception occurs
        so that the video doesn't get corrupted.
    """
    def __init__(self,
                 source=None,
                 root_dir=None,
                 filename=None,
                 width=None,
                 height=None,
                 fps=None,
                 ext='mp4',ext_i = 0):
        """Initiate VideoWriter

        Args:
            source (VideoReader, optional): Source to be used for all the configurations +
            to set default output file name (i.e. source's name + _output). If source name
            is not a valid filename (i.e. URL) then please provide filename arg. If this arg
            is given then other config args become optional, otherwise configs args are
            required. Defaults to None.

            root_dir (str, optional): Path where output video will be saved.
            Defaults to None (i.e. current directory is chosen).

            filename (str, optional): Name of the output file. Defaults to None,
            i.e. filename is chosen by appending '_output' to source object name.
            Must be provided if source object is not given.

            width (int, optional): Width of output stream, and overwrites the source's
            default width. Defaults to None, i.e. width is set to source's width.
            Must be provided if source object is not given.

            height (int, optional): Height of output stream, and overwrites the source's
            default height. Defaults to None, i.e. height is set to source's width.
            Must be provided if source object is not given.

            fps (int, optional): FPS of output stream, and overwrites the source's
            default fps. Defaults to None, i.e. fps is set to source's width.
            Must be provided if source object is not given.

            ext (str, optional): extension of output video. Defaults to 'mp4'.
        """
        self._stream = None
        # get init info from VideoReader
        if isinstance(source, VideoReader) or hasattr(source, 'config'):
            fname, width_, height_, fps_ = itemgetter('source', 'width',
                                                      'height',
                                                      'fps')(source.config)
            if filename is None:
                # overwrite filename
                if (source.source.isnumeric()
                        or source.source.startswith('rtsp')
                        or source.source.startswith('http')):
                    print(
                        f'{bcolors.WARNING}[Video-Writer] Warning:',
                        f'No Filename was given for a live-stream/webcam source.',
                        f'Output file will be named temp.mp4{bcolors.ENDC}')
                    filename = 'temp.mp4'

                root, fname = os.path.split(fname)
                fname = f"{os.path.splitext(fname)[0]}_output.{ext}"
                if root_dir is None:
                    root_dir = root if not isinstance(
                        source, VideoReaderThreaded) else './'
                filename = fname
            if width is None:
                width = width_
            if height is None:
                height = height_
            if fps is None:
                fps = fps_

        # sanity check for ext
        if '.' not in filename:
            filename += '.' + ext

        # set output dir
        if root_dir is not None:
            filename = os.path.join(root_dir, filename)

        # check if all needed info is given
        assert filename is not None, f'Bad FileName: Please provide a non-None valid Filename.'
        assert fps is not None, f'Bad fps: Please provide a non-None valid fps.'
        assert width is not None, f'Bad width: Please provide a non-None valid width.'
        assert height is not None, f'Bad height: Please provide a non-None valid height.'
        # create writing stream
        self._stream = cv2.VideoWriter(filename, self.fourcc(ext_i), fps,
                                       (width, height))

        self._name = filename
        self._width = width
        self._height = height
        self._fps = fps
        self._ext = ext

        self._config = {
            'name': self._name,
            'width': self._width,
            'height': self._height,
            'fps': self._fps,
            'ext': self._ext
        }
        # check if success
        assert self._stream.isOpened(), f'Failed to create {filename}'

    @property
    def name(self):
        """Returns name/URL of stream

        Returns:
            str: name/ULR of the source stream
        """
        return self._name

    @property
    def height(self):
        """Returns height of output stream

        Returns:
            int: height of output stream
        """
        return self._height

    @property
    def width(self):
        """Returns width of output stream

        Returns:
            int: width of output stream
        """
        return self._width

    @property
    def fps(self):
        """Returns fps of output stream

        Returns:
            int: fps of output stream
        """
        return self._fps

    @property
    def ext(self):
        """Returns ext of output stream

        Returns:
            int: ext of output stream
        """
        return self._ext

    @property
    def config(self):
        """Returns information about the output stream

        Returns:
            dict: a dictionary containing info regarding
            output filename, width, height, fps and ext.
        """
        return self._config

    def __enter__(self):
        """Context Manager entry point.

        Returns:
            VideoWriter: Used for context.
        """
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Context Manager Exit Point, frees up all the resources to make
        sure video is not corrupted.

        Args:
            exception_type (type): Indicates class of exception.
            exception_value (Error): indicates class of exception.
            traceback (traceback): Traceback is a report which has
            all of the information needed to solve the exception.
        """
        self.__del__()

    def __del__(self):
        """Frees up all the resources to make
        sure video is not corrupted.
        """
        if self._stream is not None:
            self._stream.release()

    def write(self, frame):
        """Write the given frame to the output video.

        Args:
            frame (ndarray): frame to be written.
        """
        self._stream.write(frame)

    def release(self):
        """Manually call to del to free up all the resources to make
        sure the video is not corrupted.
        """
        self.__del__()

    @staticmethod
    def fourcc(ext_i):
        """Returns cv2.VideoWriter_fourcc for video writer config

        Args:
            ext (str): extension of video file.

        Raises:
            Exception: Given ext is not in supported formats.

        Returns:
            cv2.VideoWriter_fourcc: Config for VideoWriter
        """
        # fourcc = {'mp4': 'mp4v', 'mkv': 'X264', 'avi': 'DIVX'}
        fourcc = ['mp4v','DIVX','PIM1','MJPG','MP42','DIV3','U263','I263','FLV1','X264']
        # if ext not in fourcc:
        #     raise Exception(f'Extension .{ext} not supported by backend.')

        return cv2.VideoWriter_fourcc(*fourcc[ext_i])

        #PIM1  = MPEG-1 codec
        #MJPG  = motion-jpeg codec
        #MP42 = MPEG-4.2 codec
        #DIV3 = MPEG-4.3 codec
        #DIVX = MPEG-4 codec
        #U263 = H263 codec
        #I263 = H263I codec
        #FLV1  = FLV1 codec