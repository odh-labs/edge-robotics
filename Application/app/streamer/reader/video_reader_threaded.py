"""Contains class defintion of VideoReaderThreaded.
"""
from threading import Thread, Event
from collections import deque
import time

from streamer.utils.sys_colors import bcolors
from .video_reader import VideoReader


class VideoReaderThreaded(VideoReader):
    """Read Video from a Live Stream. It's designed to continously
    fetch and store frames in queue (stored in the RAM) using an independent
    thread. It should be used in sitations where frames will be requested at
    a rate (equal or more) to the FPS of the input stream. If the request
    rate is slower than the stream's FPS and needed class configurations are
    not set, then system can run out of memory (as more new frames will be
    pushed onto the RAM).
    """
    def __init__(self,
                 source,
                 width=None,
                 height=None,
                 fps=None,
                 pre_process=None,
                 skip_frames=1,
                 buffer_size=None,
                 wait_time=2,
                 restart_time=0,
                 force_decode=False):
        """Initiate VideoReaderThreaded

        Args:
            source (str): Path to video file or URL of video source/stream

            width (int, optional): Set Width of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None


            height (int, optional): Set Height of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.

            fps (int, optional): Set FPS of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.

            pre_process (function, optional): Function to be applied on the frame
            before returning it to user. Defaults to None.

            skip_frames (int, optional): Pick every nth frame and skip the n frames in
            between. Defaults to None means picking every frame.

            buffer_size (int, optional): Size of Buffer used by OpenCV, recommened
            to be set for USB Cams usage. Defaults to None.

            wait_time (int, optional): Put main thread to sleep when there are no more
            frames to return, so that fetching thread can store more frames on to RAM.
            Defaults to 2.

            restart_time (int, optional): Count of how many times Chunker should try to restart the
            stream in case of failiures (server-error, network-error, corrupted frames, etc.).
            Defaults to -1 means to always restart the stream.

            force_decode (bool, optional): Change decoding method to something universal,
            use it if you get multiple decoding error messages. Defaults to False.

        Raises:
            Exception: VideoStart Error, raised when it's failed to Start reading from stream
            and the stream has already been restarted for the restart_time count
        """
        # init base video reader class
        super().__init__(source=source,
                         pre_process=pre_process,
                         skip_frames=skip_frames,
                         buffer_size=buffer_size,
                         force_decode=force_decode,
                         fps=fps,
                         width=width,
                         height=height)

        # sanity
        self.__thread = None

        # buffer(queue) to keep frames from live-stream
        self.__frames = deque()

        # guarantee first frame
        ret, frame = self._stream.read()
        if not ret:
            raise Exception(f'{bcolors.FAIL}VideoStart Error:\
                     Failed to Start/Read from the Stream {self.source}...{bcolors.ENDC}'
                            )
        self.__frames.append(frame)

        # start thread to read from stream
        self.__stop_event = Event()
        self.__thread = Thread(target=self.__read_from_stream, daemon=True)
        self.__thread.start()

        # set wait time to sleep when queue is empty
        self.__wait_time = wait_time

        # set warnning counter.
        self.__warnnings = 0

        # left restart count
        self.__restart_time = restart_time

        # wait for frame queue to get filled.
        time.sleep(self.__wait_time)

    def _read_frame(self):
        """Read frame from queue (stored on RAM) and return success flag and frame

        Returns:
            tuple(bool, ndarray): flag denoting whether frame read was successful,
            and the oldest frame read from the queue if flag is True else None.
        """
        while (not self.__frames) and (self._stream is not None):
            self.__warnnings += 1
            print(
                f'{bcolors.WARNING}[VideoReaderT] Warnning({self.__warnnings}):',
                'Frame Queue is Empty putting main',
                f'thread to sleep.{bcolors.ENDC}')
            time.sleep(self.__wait_time)

        if (not self.__frames) and (self._stream is None):
            return False, None

        return True, self.__frames.popleft()

    def __read_from_stream(self):
        """Read frames from the stream and store them into a queue.
        """
        try:
            while self._stream.isOpened():
                # kill thread if needed
                if self.__stop_event.is_set():
                    # end the process.
                    print(f"{bcolors.OKGREEN}[VideoReaderT] Info:",
                          f"Stopping the stream Reader Thread.{bcolors.ENDC}")
                    super().release()
                    return
                # have to skip frames
                if self._skip_frames > 1:
                    # skip frames
                    for _ in range(self._skip_frames):
                        self._stream.grab()

                    # read the nth frame
                    ret, frame = self._stream.retrieve()

                else:
                    ret, frame = self._stream.read()
                if not ret:
                    break
                self.__frames.append(frame)

            super().release()
            print(f'{bcolors.OKCYAN}[VideoReaderT] Info: Finished Reading',
                  f'Frames from {self.source} Stream.{bcolors.ENDC}')

        except Exception as error:
            print(f"{bcolors.FAIL}[VideoReaderT] Error:",
                  "Failed to Start/Read from the",
                  f"Stream {self.source}...\n{error}{bcolors.ENDC}")

        if self.__restart_time == 0:
            # end the process.
            print(f"{bcolors.OKGREEN}[VideoReaderT] Info:",
                  f"Stopping the stream Reader Thread.{bcolors.ENDC}")
            # self.release(main_thread=False)
            super().release()
            return

        # if not infinite restarts, then decrm count
        if self.__restart_time > 0:
            self.__restart_time -= 1

        # stop if main thread is dead
        if self.__stop_event.is_set():
            print(f"{bcolors.OKGREEN}[VideoReaderT] Info:",
                  f"Stopping the stream Reader Thread.{bcolors.ENDC}")
            super().release()
            return

        # restart stream
        try:
            print(f'{bcolors.OKCYAN}[VideoReaderT] Info: Restarting the',
                  f'Stream.{bcolors.ENDC}')
            self.start_stream()
            print(f'{bcolors.OKGREEN}[VideoReaderT] Info:',
                  f'Successfully Restarted the Stream.{bcolors.ENDC}')
        except Exception as error:
            print(f"{bcolors.FAIL}[VideoReaderT] Error:",
                  "Failed to ReStart the",
                  f"Stream {self.source}...\n{error}{bcolors.ENDC}")
            print(error)

        # restart reading
        self.__read_from_stream()

    def __del__(self):
        self.__stop_event.set()
        if self.__thread is not None and self.__thread.is_alive():
            self.__thread.join()
        super().__del__()

    def release(self):
        self.__del__()
