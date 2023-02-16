"""Contains class defintion of VideoReader.
"""
import time

import numpy as np
import cv2

from streamer.utils.sys_colors import bcolors
from datetime import datetime

class VideoReader:
    """Read Video from Live Stream or Video saved on drive.
    It's designed to fetch the next frame when requested, so you'll lose frame
    in a live streaming sitatuaion if there's a gap in between request for
    fetching frames.
    """
    def __init__(self,
                 source,
                 pre_process=None,
                 skip_frames=1,
                 buffer_size=None,
                 force_decode=False,
                 fps=None,
                 width=None,
                 height=None):
        """Initiate VideoReader

        Args:
            source (str): Path to video file or URL of video source/stream

            pre_process (function, optional): Function to be applied on the frame
            before returning it to user. Defaults to None.

            skip_frames (int, optional): Pick every nth frame and the n frames in
            between. Defaults to 1 means picking every frame.

            buffer_size (int, optional): Size of Buffer used by OpenCV, recommened
            to be set for USB Cams usage. Defaults to None.

            force_decode (bool, optional): Change decoding method to something universal,
            use it if you get multiple decoding error messages. Defaults to False.

            fps (int, optional): Set FPS of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.

            width (int, optional): Set Width of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.

            height (int, optional): Set Height of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.
        """

        # saftey for del call if init fails
        self._stream = None

        # check skip frame isn't 0
        assert skip_frames > 0, 'Skip Frame cannot be less than 1'

        # sanity work to make sure source is string
        source = str(source)

        if source.isnumeric():
            source = int(source)

        # open stream
        init_flag = 0
        self._stream = cv2.VideoCapture(source)
        while True:
            _ret,_frame = self._stream.read()
            init_flag += 1
            if _ret or init_flag > 100:
                break
        assert _ret , f'Failed to Initialize Stream'
        # set buffersize if given
        if buffer_size is not None:
            self._stream.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)

        # force decode if needed
        if force_decode:
            self._stream.set(cv2.CAP_PROP_FOURCC,
                             cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        # set new FPS, Width, Height if given
        self._set_config("FPS", fps, cv2.CAP_PROP_FPS)
        self._set_config("Width", width, cv2.CAP_PROP_FRAME_WIDTH)
        self._set_config("Height", height, cv2.CAP_PROP_FRAME_HEIGHT)

        # check if success
        assert self._stream.isOpened(), f'Failed to open {source}'

        # set width, height, fps info
        self._width = int(self._stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._fps = int(self._stream.get(cv2.CAP_PROP_FPS))
        if self._fps > 100:
            self._fps = self._force_fps()
            print(f"{bcolors.OKCYAN}[VideoReader] Info: Stream FPS is : {self._fps}.{bcolors.ENDC}")

        self._count = 0
        self._source = source
        self._skip_frames = skip_frames

        # set preprocessing if given
        if pre_process is not None:
            _, temp = pre_process(True, np.zeros((self.height, self.width, 3)))
            self._height, self._width = temp.shape[:2]
            self.read_frame = self.compose_functions(self._read_frame,
                                                     pre_process)

        else:
            self.read_frame = self._read_frame

        # set config (can be used for creation of writer)
        self._config = {
            'backend': 'opencv',
            'source': self.source,
            'width': self.width,
            'height': self.height,
            'fps': self.fps
        }

        self._stream_args = {
            'source': source,
            'skip_frames': skip_frames,
            'buffer_size': buffer_size,
            'force_decode': force_decode,
            'fps': fps,
            'width': width,
            'height': height,
            'pre_process': pre_process
        }

    @property
    def height(self):
        """Returns height of stream

        Returns:
            int: height of stream
        """
        return self._height

    @property
    def width(self):
        """Returns width of stream

        Returns:
            int: width of stream
        """
        return self._width

    @width.setter
    def width(self, width):
        """Set width of stream

        Args:
            width (int): new width of stream
        """
        self._stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._width = width
        self._config['width'] = width

    @height.setter
    def height(self, height):
        """Set height of stream

        Args:
            height (int): new height of stream
        """
        self._stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._height = height
        self._config['height'] = height

    @property
    def fps(self):
        """Returns fps of stream

        Returns:
            int: fps of stream
        """
        return self._fps

    @property
    def count(self):
        """Returns number of frames already read

        Returns:
            count: number of frames read from stream so far
        """
        return self._count

    @property
    def source(self):
        """Returns name/URL of stream

        Returns:
            str: name/ULR of the source stream
        """
        return self._source

    @property
    def config(self):
        """Returns information about the stream

        Returns:
            dict: a dictionary containing info regarding
            backend, source, width, height and fps.
        """
        return self._config

    @property
    def duration(self):
        """Returns number of seconds already read

        Returns:
            float: number of seconds read from stream so far
        """
        return self.count / self.fps

    @property
    def duration_minutes(self):
        """Returns number of minutes already read

        Returns:
            float: number of minutes read from stream so far
        """
        return self.duration / 60.

    def __iter__(self):
        """Iterator for reading frames

        Returns:
            VideoReader: can be used in next function or loops directly
        """
        return self

    def __next__(self):
        """Returns next flag and frame read from stream

        Raises:
            StopIteration: raised when there are no more frames to read or
            stream has stopped or frames are corrupted thus read method has failed.

        Returns:
            tuple(bool, ndarray): flag denoting whether frame read was successful,
            and the latest frame read from the stream if flag is True else None.
        """
        ret, frame = self.read_frame()
        if not ret:
            raise StopIteration

        # incrm frame count
        self._count += 1
        # Dummy timestamp
        timestamp = '2001-01-01 01:01:01'
        return ret, frame, timestamp

    def __del__(self):
        """Freeup resources and stream to avoid resource wastage and
        corruption of the stream.
        """
        if self._stream is not None:
            self._stream.release()
            self._stream = None

    def __repr__(self):
        """Information of stream

        Returns:
            str: configuration of streams (containing info
            regarding backend, source, width, height and fps.)
        """
        return str(self.config)

    def _read_frame(self):
        """Read frame from stream and return success flag and frame

        Returns:
            tuple(bool, ndarray): flag denoting whether frame read was successful,
            and the latest frame read from the stream if flag is True else None.
        """
        # have to skip frames
        if self._skip_frames > 1:
            # skip frames
            for _ in range(self._skip_frames):
                self._stream.grab()
            # read the nth frame
            ret, frame = self._stream.retrieve()

        # no need to skip frames
        else:
            ret, frame = self._stream.read()

        return ret, frame

    def release(self):
        """Manually call del on the object to Freeup resources and
        stream to avoid resource wastage and corruption of the stream.
        """
        if self._stream is not None:
            self._stream.release()
            self._stream = None

    def start_stream(self):
        """Start the Video Stream with init args
        """

        # open stream
        init_flag = 0
        self._stream = cv2.VideoCapture(self._stream_args['source'])
        while True:
            _ret,_frame = self._stream.read()
            init_flag += 1
            if _ret or init_flag > 100:
                break
        assert _ret , f'Failed to Initialize Stream'

        # set buffersize if given
        if self._stream_args['buffer_size'] is not None:
            self._stream.set(cv2.CAP_PROP_BUFFERSIZE,
                             self._stream_args['buffer_size'])

        # force decode if needed
        if self._stream_args['force_decode']:
            self._stream.set(cv2.CAP_PROP_FOURCC,
                             cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        # set new FPS, Width, Height if given
        self._set_config("FPS", self._stream_args['fps'], cv2.CAP_PROP_FPS)
        self._set_config("Width", self._stream_args['width'],
                         cv2.CAP_PROP_FRAME_WIDTH)
        self._set_config("Height", self._stream_args['height'],
                         cv2.CAP_PROP_FRAME_HEIGHT)

        # check if success
        assert self._stream.isOpened(
        ), f'Failed to open {self._stream_args["source"]}'

        # set width, height, fps info
        self._width = int(self._stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._fps = int(self._stream.get(cv2.CAP_PROP_FPS))
        if self._fps > 100:
            self._fps = self._force_fps()

        # set preprocessing if given
        if self._stream_args['pre_process'] is not None:
            _, temp = self._stream_args['pre_process'](True,
                                                       np.zeros(
                                                           (self.height,
                                                            self.width, 3)))
            self._height, self._width = temp.shape[:2]

    def _set_config(self, config_name, new_value, prop):
        """Set new property of stream (see config for available props) if
        the new_value is valid, and setting prop is allowed by the stream source.
        Cannot set backend.

        Args:
            config_name (str): name of the prop to be changed
            new_value (int): new value of the prop
            prop (int): cv2 flag representing the prop in the backend.
        """
        # set new FPS if given
        if new_value is not None:
            flag = self._stream.set(prop, new_value)
            time.sleep(2)

            flag = flag and int(self._stream.get(prop)) == new_value
            if flag:
                while not self._stream.read()[0]:
                    time.sleep(1)
                print(
                    f"{bcolors.OKGREEN}[VideoReader] Info: Successfully Set",
                    f"{config_name} of the reader to {new_value}.{bcolors.ENDC}"
                )
            else:
                print(f"{bcolors.FAIL}[VideoReader] Info:",
                      f"Failed to set {config_name}.",
                      f"Either setting {config_name} is not",
                      "supported with this source or",
                      f"this {config_name}({new_value})",
                      f"configuration is not available.{bcolors.ENDC}")

    @staticmethod
    def compose_functions(function_1, function_2):
        """Composes function_1 & function_2 such that
        resulting function will behave as function_2(function_1(x))

        Args:
            function_1 (function): Inside function of composite function
            function_2 (function): Outside function of composite function

        Returns:
            function: composite function of function_2(function_1(x))
        """
        return lambda *args, **kwargs: function_2(*function_1(*args, **kwargs))
    
    def _force_fps(self):
        start = datetime.now()
        fps = 15
        cont = 0
        while True:  
            if cont == 50:
                a = datetime.now() - start 
                b = (a.seconds * 10e6 + a.microseconds)
                fps = ((50 * 10e6)/ b)
                break
            _,__ = self._stream.read()
                
            cont+=1
        return int(fps)

