"""Contains class defintion of StreamChunker.
"""

import os
import shutil
import time
from datetime import datetime,timedelta
from threading import Thread, Lock, Event

from streamer.reader import VideoReader
from streamer.writer import VideoWriter
from streamer.utils.sys_colors import bcolors
# import inspect
import platform


class StreamChunker:
    """Read Live Stream and save them as chunks to be
    read later by the main thread. Use it if your pipeline's
    processing speed is significantly slower than input stream's FPS.
    It's an alternate to streamer.reader.VideoReaderThreaded, which saves
    streams frames in drive instead of RAM.
    """
    def __init__(self,
                 source,
                 width=None,
                 height=None,
                 fps=None,
                 pre_process=None,
                 save_pre_process=None,
                 skip_frames=1,
                 buffer_size=None,
                 chunk_size=5,
                 chunk_dir=None,
                 chunk_ext='mp4',
                 clean_chunks_before_exit=True,
                 clean_used_chunks=True,
                 wait_time=5,
                 restart_time=-1,
                 force_decode=False):
        """Initiate Chunker

        Args:
            source (str): Path to video file or URL of video source/stream

            width (int, optional): Set Width of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.

            height (int, optional): Set Height of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.

            fps (int, optional): Set FPS of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.

            pre_process (function, optional): Function to be applied on the frame
            before returning it to user. Defaults to None.

            save_pre_process (function, optional): Function to be applied on the frame
            before chunks are saved. Can be used to optimize memory usage.
            Defaults to None.

            skip_frames (int, optional): Pick every nth frame and skip the n frames in
            between. Defaults to 1 means picking every frame.

            buffer_size (int, optional): Size of Buffer used by OpenCV, recommened
            to be set for USB Cams usage. Defaults to None.

            chunk_size (int, optional): Length of each chunk in seconds. Defaults to 5.

            chunk_dir (str, optional): Path to directory where chunks will be saved.
            Defaults to None, and in that case dir path is not given, a new directory
            derived from the stream name will be used.

            chunk_ext (str, optional): Extension of saved chunk vidoes. Defaults to 'mp4'.

            clean_chunks_before_exit (bool, optional): If True, then delete all the used/unused
            chunks before ending the process. Defaults to True.

            clean_used_chunks (bool, optional): delete chunk once it has been read by the main
            thread. Defaults to True.

            wait_time (int, optional): Amount of time (in seconds) to put the main thread to sleep
            in case there are no saved chunks left to read (i.e. stream chunkering thread is either
            failing to read from stream, restarting the stream, or simply running behind).
            Defaults to 5.

            restart_time (int, optional): Count of how many times Chunker should try to restart the
            stream in case of failiures (server-error, network-error, corrupted frames, etc.).
            Defaults to -1 means to always restart the stream.

            force_decode (bool, optional): Change decoding method to something universal,
            use it if you get multiple decoding error messages. Defaults to False.

        Raises:
            Exception: Stream-Chunker Error, raised when it's failed to Start Chunker and the stream
            has already been restarted for the restart_time count
        """
        # const
        # sanity init for del safety
        self.__stream_reader = None
        self.__last_reader = self.__stream_reader
        self.__chunk_reader = None
        self.__chunk_writer = None
        self.__clean_chunks_before_exit = clean_chunks_before_exit

        self.__current_time = None
        self.__platform = platform.system()
        # chunk dir rename if live-stream or webcam
        if chunk_dir is None and (source.isnumeric()
                                  or source.startswith('rtsp')
                                  or source.startswith('http')):
            print(f'{bcolors.WARNING}[Stream-Chunker] Warning(0):',
                  f'No Chunk Dir name given for a live-stream/webcam source.',
                  f'Chunks will be saved at ./temp.{bcolors.ENDC}')
            chunk_dir = 'temp'

        self.__chunk_dir = chunk_dir if chunk_dir is not None \
            else f"{os.path.splitext(os.path.split(source)[1])[0]}_chunks"

        # clean saved chunks
        if self.__clean_chunks_before_exit and self.__chunk_dir is not None:
            self.remove_dir(self.__chunk_dir)
        # init base video reader class
        self._stream_args = {
            'source': source,
            'pre_process': save_pre_process,
            'skip_frames': skip_frames,
            'buffer_size': buffer_size,
            'force_decode': force_decode,
            'fps': fps,
            'width': width,
            'height': height
        }
        self.start_stream()

        # chunk count
        self.__chunk_write_count = 0
        self.__chunk_names = list()
        self.__chunk_read_count = 0
        self.__chunks_to_read = 0
        self.__chunk_size = chunk_size
        self.__chunk_ext = chunk_ext
        self.__chunk_ext_i = 0
        self.__chunk_frame_count = 0

        # set props
        self.__clean_used_chunks = clean_used_chunks
        self.__count = 0
        self.__restart_time = restart_time
        self.__out_pre_process = pre_process

        # start thread to read from stream and write chunks
        self._stop_event = Event()
        self.__thread = Thread(target=self.__chunker, daemon=True)
        self.__lock = Lock()
        self.__thread.start()

        # set preprocessing if needed
        self.read_frame = self.__read_frame

        # set warnning counter.
        self.__warnnings = 0
        self.__wait_time = wait_time

        # wait for first chunk to finish
        time.sleep(self.__wait_time)
        if self.__stream_reader is None and self.__chunks_to_read == 0:
            raise Exception(
                f'{bcolors.FAIL}Stream-Chunker Error: Failed to Start Chunker...{bcolors.ENDC}'
            )

        print(f'{bcolors.OKGREEN}[Stream-Chunker] Info:',
              f'Successfully started Chunker.{bcolors.ENDC}')

        # wait for first chunk to be finished
        if self.__chunks_to_read == 0:
            print(
                f'{bcolors.WARNING}[Stream-Chunker] Warning({self.__warnnings}):',
                f'First Chunk is still not ready. Putting main thread to sleep',
                f'for {self.__wait_time} seconds.{bcolors.ENDC}')
            # time.sleep(self.__chunk_size)
            time.sleep(self.__wait_time)

    @property
    def height(self):
        """Returns height of stream

        Returns:
            int: height of stream
        """
        return self.__stream_reader.height if self.__stream_reader is not None else self.__last_reader.height

    @property
    def width(self):
        """Returns width of stream

        Returns:
            int: width of stream
        """
        return self.__stream_reader.width if self.__stream_reader is not None else self.__last_reader.width

    @property
    def fps(self):
        """Returns fps of stream

        Returns:
            int: fps of stream
        """
        return self.__stream_reader.fps if self.__stream_reader is not None else self.__last_reader.fps

    @property
    def count(self):
        """Returns number of frames already read

        Returns:
            count: number of frames read from stream so far
        """
        return self.__count

    @property
    def source(self):
        """Returns name/URL of stream

        Returns:
            str: name/ULR of the source stream
        """
        return self.__stream_reader.source if self.__stream_reader is not None else self.__last_reader.source

    @property
    def config(self):
        """Returns information about the stream

        Returns:
            dict: a dictionary containing info regarding
            backend, source, width, height and fps.
        """
        return self.__stream_reader.config if self.__stream_reader is not None else self.__last_reader.config

    @property
    def duration(self):
        """Returns number of seconds already read

        Returns:
            float: number of seconds read from stream so far
        """
        return self.__count / (self.__stream_reader.fps if self.__stream_reader
                               is not None else self.__last_reader.fps)

    @property
    def duration_minutes(self):
        """Returns number of minutes already read

        Returns:
            float: number of minutes read from stream so far
        """
        return self.duration / 60.

    @staticmethod
    def remove_dir(dname):
        """Delete Directory

        Args:
            dname (str): path of the directory to be deleted
        """

        if dname is not None and os.path.exists(dname):
            shutil.rmtree(dname)

    @staticmethod
    def remove_file(fname):
        """Delete File

        Args:
            fname (str): path of the file to be deleted
        """
        if fname is not None and os.path.exists(fname):
            os.remove(fname)

    def start_stream(self):
        """Start/Restart the stream with the configurations given at
        StreamChunker initialization.
        """
        print(f"{bcolors.OKCYAN}[Stream-Chunker] Info: Initializing stream reader.{bcolors.ENDC}")
        # print(self._stream_args['source'])
        self.__stream_reader = VideoReader(
            source=self._stream_args['source'],
            pre_process=self._stream_args['pre_process'],
            skip_frames=self._stream_args['skip_frames'],
            buffer_size=self._stream_args['buffer_size'],
            force_decode=self._stream_args['force_decode'],
            fps=self._stream_args['fps'],
            width=self._stream_args['width'],
            height=self._stream_args['height'])
        print(
                f"{bcolors.OKBLUE}[Stream-Chunker] Info:",
                f"Initialized stream reader.{bcolors.ENDC}")
        
    def __create_writer(self):
        """Create a streamer.writer.VideoWriter object for
        writing a chunk of stream.

        Returns:
            VideoWriter: object to write a chunk to file system.
        """
        # fname = f"{self.__chunk_write_count}.mp4"
        if(self.__platform == "Windows"):
            tmp_time = self.__current_time.strftime("%Y-%m-%d-%H-%M-%S")
        else:
            tmp_time = self.__current_time
        nfname = f"{str(tmp_time)}_{self.__chunk_write_count}.{self.__chunk_ext}"

        self.__chunk_names.append(nfname)
        # print("self.__chunk_dir: ",self.__chunk_dir)
        
        os.makedirs(self.__chunk_dir, exist_ok=True)
        writer = VideoWriter(source=self.__stream_reader,
                             filename=nfname,
                             root_dir=self.__chunk_dir,
                             ext=self.__chunk_ext,ext_i=self.__chunk_ext_i)
        # print("created")

        # update chunk counter
        self.__chunk_write_count += 1

        return writer

    def __create_reader(self):
        """Create a streamer.reader.VideoReader object for
        read a saved chunk from the stream.

        Returns:
            VideoReader: object to read a chunk from the file system.
        """
        # fname = f"{self.__chunk_read_count}.mp4"
        nfname = self.__chunk_names[self.__chunk_read_count]


        # TODO: pop self.__chunk_names which have been read might overflow [highly improbable]
        v_source = os.path.join(self.__chunk_dir, nfname)
        while not os.path.exists(v_source):
            pass
        reader = VideoReader(source=v_source,
                             pre_process=self.__out_pre_process)

        # update chunk counter
        self.__chunk_read_count += 1
        return reader

    def __chunker(self):
        """Read from live stream, and write chunks of videos in the file
        system that will be read by the main thread later. It also broadcasts
        the information of which chunks are ready to be read, and restarts the
        stream (if args given at initialization) in the case of failiure.
        """
        count=0
        read_flag = False
        try:
            # print("start stream reader")
            for _, frame,chunk_timestamp in self.__stream_reader:
                # print('frame')
                # print(self._stop_event.is_set())
                self.__current_time = datetime.now()
                self.__current_time.strftime("%Y-%m-%d-%H:%M:%S")
                if self._stop_event.is_set():
                    print(
                        f"{bcolors.WARNING}[Stream-Chunker] Info:",
                        f"Stopping the stream chunker Thread.{bcolors.ENDC}")
                    if self.__chunk_writer is not None:
                        self.__chunk_writer.release()
                        self.__chunk_writer = None
                    return

                if (self.__stream_reader.duration % self.__chunk_size == 0
                        or self.__chunk_writer is None):
                    if self.__chunk_writer is not None:
                        # close current writer
                        self.__chunk_writer.release()
                        # update counter of readable chunks
                        # number of chunks: read-write diff
                        self.__lock.acquire()
                        self.__chunks_to_read += 1
                        self.__lock.release()

                    # start new stream
                    self.__chunk_writer = None
                    EXT = ['mp4','avi','avi','avi','avi','avi','avi','avi','avi','mkv']
                    for i,_ext in enumerate(EXT):
                        try:
                            self.__chunk_ext = _ext
                            self.__chunk_ext_i = i
                            self.__chunk_writer = self.__create_writer()
                        #     print(
                        # f"{bcolors.OKCYAN}[Stream-Chunker] Info:",
                        # f"Extension set as {_ext}.{bcolors.ENDC}")
                            break
                        except:
                            continue

                if self.__chunk_writer is None:
                    raise Exception
                # write frame
                
                self.__chunk_writer.write(frame)
                read_flag = True
                # count+=1
                # if count>300:
                #     break
            # nothing more to read; stream ended
            # pass

        except Exception as error:
            # exception occured in reading from stream.
            print("Error.: ",error)

        # free resources

        if self.__chunk_writer is not None:
            self.__chunk_writer.release()
            self.__chunk_writer = None

            if read_flag:
                self.__lock.acquire()
                self.__chunks_to_read += 1
                self.__lock.release()

        if self.__chunk_reader is not None:
            self.__chunk_reader.release()
            self.__chunk_reader = None

        # release current
        self.__stream_reader.release()
        self.__last_reader = self.__stream_reader
        self.__stream_reader = None

        if self.__clean_chunks_before_exit and self.__chunk_dir is not None:
            print(f"{bcolors.OKCYAN}[Stream-Chunker] Info:",
                        f"Chunker Stopped. Removing chunks .{bcolors.ENDC}")
            retry = 0
            while True:
                try:
                    self.remove_dir(self.__chunk_dir)
                    self.__chunks_to_read =0
                    self.__chunk_names=list()
                    self.__chunk_read_count=0
                    break
                except:
                    print(f"{bcolors.FAIL}[Stream-Chunker] Error:",
                        f"Error in removing chunks,trying again .{bcolors.ENDC}")
                    time.sleep(2)
                    retry += 1
                if retry > 3:
                    break

        # restart streaming if needed
        self.__restart_time = 20
        # self._stop_event.clear()

        if self.__restart_time != 0:
            # clean up
            self.__chunk_writer = None

            # incrm restart warnings
            self.__warnnings += 1
            print(
                f"{bcolors.WARNING}[Stream-Chunker] Warning({self.__warnnings}):",
                "Failed to Read from the Source Stream.",
                f"Restarting the reader.{bcolors.ENDC}")

            # time.sleep(self.__wait_time)

            # restart
            restart_success_flag = False
            while self.__restart_time != 0:
                if self._stop_event.is_set():
                    print(
                        f"{bcolors.OKCYAN}[Stream-Chunker] Info:",
                        f"Stopping the stream chunker Thread.{bcolors.ENDC}")
                    return

                # decr restart countconda 
                if self.__restart_time > 0:
                    self.__lock.acquire()
                    self.__restart_time -= 1
                    self.__lock.release()

                # try restart
                try:
                    self.start_stream()
                    restart_success_flag = True
                    print(f"{bcolors.OKBLUE}[Stream-Chunker] Info:",
                          f"Successfully Restarted the reader.{bcolors.ENDC}")
                    break
                except Exception as error:
                    self.__warnnings += 1
                    print(
                        f"{bcolors.FAIL}[Stream-Chunker] Error({self.__warnnings}):",
                        f"Failed to restart Stream Reader. {error}. Will Try Again in",
                        f"{self.__wait_time} seconds.{bcolors.ENDC}")
                    time.sleep(self.__wait_time)
            # start chunker again
            if restart_success_flag:
                self.__chunker()


    def __read_frame(self):
        """Read frame from available chunks which were saved in the file storage,
        and returns success flag and frame from chunks.

        Returns:
            tuple(bool, ndarray): flag denoting whether frame read was successful,
            and the latest frame read from the stream if flag is True else None.
        """
        # check for stream end
        if  not self.__chunk_names:
            time.sleep(self.__wait_time)
        if self.__chunk_reader is None and self.__chunks_to_read == 0 and self.__restart_time == 0 and self.__stream_reader is None:
            # print('#####################no chunks to read############')
            return False, None

        # initialize new reader of needed
        if self.__chunk_reader is None:
                    # wait until there's chunk to read and stream is open
            while self.__chunks_to_read == 0 and self.__stream_reader is not None:
                self.__warnnings += 1
                # print(
                #     f"{bcolors.WARNING}[Stream-Chunker] Warning({self.__warnnings}):",
                #     "All saved chunks already processed. Putting main thread to",
                #     f"sleep for {self.__wait_time} seconds.{bcolors.ENDC}")
                time.sleep(self.__wait_time)
            if self.__chunks_to_read != 0 and self.__stream_reader is  None:
                self.__warnnings += 1
                time.sleep(self.__wait_time)
            # end stream; check needed to avoid
            # run conditions caused by threading
            if self.__stream_reader is None and self.__chunks_to_read == 0:
                time.sleep(15)
                # return False, None


            # create new reader
            self.__chunk_reader = self.__create_reader()
            # update counter of readable chunks
            # number of chunks: read-write diff
            self.__lock.acquire()
            self.__chunks_to_read -= 1
            self.__lock.release()

        ret, frame = self.__chunk_reader.read_frame()
        # free up current reader if needed
        if not ret:
            # release reader
            self.__chunk_reader.release()
            # remove used chunk
            if self.__clean_used_chunks:
                self.remove_file(self.__chunk_reader.source)

            self.__chunk_reader = None
            self.__chunk_frame_count = 0
            print(f'{bcolors.OKCYAN}[Stream-Chunker] Info:',
                  'Finised reading from current Chunk, switching',
                  f'to next chunk.{bcolors.ENDC}')

            return self.__read_frame()
        
        self.__chunk_frame_count += 1
        return ret, frame

    def __iter__(self):
        """Iterator for reading frames

        Returns:
            StreamChunker: can be used in next function or loops directly
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
        self.__count += 1

        # get timestamp of current chunk
        chunk_name = self.__chunk_reader.source
        try:
            if(self.__platform == "Windows"):
                chunk_timestamp = chunk_name.split('\\')[1].split('_')[0]
                d = datetime.strptime(chunk_timestamp,"%Y-%m-%d-%H-%M-%S")
                delta = (1/self.__chunk_reader.fps) * self.__chunk_frame_count
                d_ = d + timedelta(seconds = delta)

                chunk_timestamp = datetime.strftime(d_,"%Y-%m-%d %H:%M:%S")
            else:
                chunk_timestamp = chunk_name.split('/')[1].split('_')[0]
        except:
            chunk_timestamp = chunk_name.split('/')[1].split('_')[0]
        return ret, frame, chunk_timestamp

    # def __del__(self):
    #     """Freeup resources and stream to avoid resource wastage and
    #     corruption of the stream. Deletes used/unused chunks if specified
    #     at the time of initialization.
    #     """
    #     try:
    #         if not self._stop_event.is_set(): 
    #             print(
    #             f'{bcolors.HEADER}[Stream-Chunker]: Setting stop event.{bcolors.ENDC}'
    #             )
    #             self._stop_event.set()
    #     except Exception as e:
    #         print("Error while setting stop event:",e)
    #     try: 
    #         if self.__thread:
    #             print(
    #             f'{bcolors.HEADER}[Stream-Chunker]: Stop chunker thread.{bcolors.ENDC}', 
    #             self.__thread)
    #             self.__thread.join()
    #     except Exception as e:
    #         print("Error while stopping chunker thread:",e)

       
        # print(
        #     f'{bcolors.HEADER}[Stream-Chunker]: Releasing Resources.{bcolors.ENDC}'
        # )
        # # clean saved chunks
        # try:
        #     if self.__clean_chunks_before_exit and self.__chunk_dir is not None:
        #         self.remove_dir(self.__chunk_dir)
        #         self.__chunk_dir = None
        # except Exception as e:
        #     print("couldn't remove chunks ... ",e)

        # try:
        # # release stream reader if open
        #     if self.__stream_reader is not None:
        #         self.__stream_reader.release()
        #         self.__stream_reader = None
        # except Exception as e:
        #     print("couldn't rlease stream reader ... ",e)

        # # release chunk reader if open
        # try:
        #     if self.__chunk_reader is not None:
        #         self.__chunk_reader.release()
        #         self.__chunk_reader = None
        # except Exception as e:
        #     print("couldn't rlease chunk reader ... ",e)

        # # release chunk writer if open
        # try:
        #     if self.__chunk_writer is not None:
        #         self.__chunk_writer.release()
        #         self.__chunk_writer = None
        # except Exception as e:
        #     print("couldn't rlease chunk writer ... ",e)

    def release(self):
        """Manually call del on the object to Freeup resources and
        stream to avoid resource wastage and corruption of the stream.
        """
        try:
            # print("check stop_event: ",self._stop_event.is_set())
            if not self._stop_event.is_set(): 
                print(
                f'{bcolors.OKCYAN}[Stream-Chunker]: Setting stop event.{bcolors.ENDC}'
                )
                self._stop_event.set()
        except Exception as e:
            print("Error while setting stop event:",e)
        try: 
            # print("check thread status: ",self.__thread.is_alive())
            if self.__thread:
                print(
                f'{bcolors.OKCYAN}[Stream-Chunker]: Stop chunker thread.{bcolors.ENDC}', 
                self.__thread)
                self.__thread.join()
        except Exception as e:
            print("Error while stopping chunker thread:",e)

        try:
        # release stream reader if open
            if self.__stream_reader is not None:
                # print("releasing stream_reader")
                self.__stream_reader.release()
                self.__stream_reader = None
        except Exception as e:
            print("couldn't rlease stream reader ... ",e)

        # release chunk reader if open
        try:
            if self.__chunk_reader is not None:
                # print("releasing chunk_reader")
                self.__chunk_reader.release()
                self.__chunk_reader = None
        except Exception as e:
            print("couldn't rlease chunk reader ... ",e)

        # release chunk writer if open
        try:
            if self.__chunk_writer is not None:
                print("releasing chunk_writer")
                self.__chunk_writer.release()
                self.__chunk_writer = None
        except Exception as e:
            print("couldn't rlease chunk writer ... ",e)

        if self.__clean_chunks_before_exit and self.__chunk_dir is not None:
            print(f"{bcolors.OKCYAN}[Stream-Chunker] Info:",
                        f"Removing chunks .{bcolors.ENDC}", self.__chunk_dir)
            self.remove_dir(self.__chunk_dir)
            self.__chunk_dir = None

        # self.__del__()
        
