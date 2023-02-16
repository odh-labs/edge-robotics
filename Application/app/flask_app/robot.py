import sys
import os
import time
import threading
from datetime import datetime

from config import Config_ANPR,Config
from .stream import Stream
from .pipeline import Pipeline
from utils import bcolors


from detection_engines import YOLOV5_s
from db import SQLiteTool

class ROBOT:
    def __init__(self,logger=None) -> None:
        
        # self.mk_dir_if_not_exists(self.LOGS_DIR)
        print(f"{bcolors.OKCYAN}[ROBOT] Info: Initiating ROBOT{bcolors.ENDC}")
        self.logger = logger
        
        self.UPLOAD_FOLDER = "images/"
        self.FLASK_APP = "flask_app/static/"
        self.IMAGES_FOLDER = "images/"
        self.IMAGE_CONTENTS = ["lp_images","vehicles"]
        self.STREAM_FOLDER = "live"
        self.REPORT_FOLDER = "reports"
        self.REPORT_DAILY_FOLDER = "reports_daily"
        
        self._set_directory()

        config_ANPR = Config_ANPR(default=True)
        self.config = Config(default=True)

        self.PIPELINE_CONFIG = config_ANPR.init_config['pipeline_config']
        self.STREAMS = self.PIPELINE_CONFIG['stream_count']
        self.STREAM_CONFIG = config_ANPR.init_config['stream_config']

        self.stream_count = self.PIPELINE_CONFIG['stream_count']

        if not (self.PIPELINE_CONFIG['model_type'] == 'openvino'):
            print("Change to OpenVino")
            sys.exit(0)
        else:
            pass
        self.sqlite_db = SQLiteTool(total_cam = self.stream_count)
        # self.mongo_db = MongoTool()

        self.models = {}
        self._stream_configs = []
        self.statistics = {}
        self.streams = {}

        self._pipelines = {}

        self._stream_switch_threshold = self.PIPELINE_CONFIG['stream_switch']
        self._active_stream = 0
        self._prev_stream = 0
        self.stream_thread = None

        self._stream_pids = []
    def init_anpr(self):
        
        for i in range (0,self.STREAMS):
            if (i > self.stream_count):
                break
            
            cam_path = 'cam_'+str(i)+'/'
            self.mk_dir_if_not_exists(self.FLASK_APP+self.IMAGES_FOLDER+cam_path)
            for path in self.IMAGE_CONTENTS:
                self.mk_dir_if_not_exists(self.FLASK_APP+self.IMAGES_FOLDER+cam_path+path)

            if (i > len(self.STREAM_CONFIG)):
                self._stream_configs.append(self.STREAM_CONFIG[0])
            else:
                self._stream_configs.append(self.STREAM_CONFIG[i])
            
            model = {}

            print(f"{bcolors.OKCYAN}[ROBOT] Info: Setting Up Stream:{i}{bcolors.ENDC}")

            try:
                
                model['model_robot']= YOLOV5_s(self.config.object_handler_config.robot_model_config)
                model['trt_logger'] = None

                self.models[i] = model
            except Exception as exp:
                print(exp)
                print(f"{bcolors.FAIL}[ROBOT] Error: Loading Model for: {i}{bcolors.ENDC}")
                return False
            # pipelines = []
            
            try:
                self.streams[i] = Stream(config = self.STREAM_CONFIG[i],cam=i)   
            except:
                print(f"{bcolors.FAIL}[ROBOT] Error: Loading for Stream: {i}{bcolors.ENDC}")
                return False
        return True
    def stop_all(self):

        for cam,pipeline in enumerate(self._pipelines):
            flag = self.stop_pipeline(cam)
            if not flag:
                return False
        return flag

    def stop_pipeline(self,cam):
        if self._pipelines[cam] is not None:
            f1 = self._pipelines[cam].stop_stream()
            if not self._stream_configs[cam]['livestream']:
                f2 = True
            else:
                f2 = self.streams[cam].reset_stream()
        return f1 and f2

    def run_pipeline(self,rtspAddress,cam,wait_time):
        
        if cam not in self._pipelines:
            return False
        
        if self._pipelines[cam] is not None:

            self.stop_pipeline(cam)

            pipeline_flag = self._pipelines[cam].run(rtspAddress,wait_time)
            if rtspAddress == '0' or rtspAddress.startswith('rtsp') or rtspAddress.startswith('http'):
                is_video = False
            else:
                is_video = True
            
            print(f"{bcolors.WARNING}[ROBOT] Info: Input Type Video - {is_video}{bcolors.ENDC}")
            #Start only first stream
            if not self._stream_configs[cam]['livestream']:
                print(f"{bcolors.WARNING}[ROBOT] Info: Livestream Disabled - {cam}{bcolors.ENDC}")
                stream_flag = True
            else:
                if cam == 0:
                    stream_flag = self.streams[cam].init_stream(source = rtspAddress,is_video=is_video)
                    self.set_stream_pid(cam)
                    self._active_stream = cam
                else:
                    stream_flag = True
                    self.streams[cam].set_source(rtspAddress)
                
            flag = pipeline_flag and stream_flag
            if not flag:
                print(f"{bcolors.FAIL}[ROBOT] Error: Unable to start stream - {cam}{bcolors.ENDC}")
                self.stop_pipeline(cam)
            return pipeline_flag and stream_flag

    def init_pipeline(self,cam):
        
        pipeline = None
        if cam not in self.models:
            return False
        try:
            pipeline = Pipeline(config=None, 
                                roi=None,
                                init_config=self.PIPELINE_CONFIG,
                                stream_configs=self._stream_configs[cam],
                                logger=self.logger,
                                models=self.models[cam],
                                whitelist = None,
                                cam = cam)
        except Exception as exp:
            print(exp)
            return False

        if cam < 0 or cam + 1 > self.STREAMS:
            return False
        if cam in self._pipelines:
            if self._pipelines[cam] is not None:
                
                self._pipelines[cam].stop_stream()
                try:
                    self._pipelines[cam].__del__()
                except:
                    print(f"{bcolors.FAIL}[ROBOT] Error: Unable to delete pipeline: {cam}{bcolors.ENDC}")

        self._pipelines[cam] = pipeline
        return True

    def stream_kill_thread(self):
        print(f"{bcolors.OKCYAN}[ROBOT] Info: Stream Kill Thread started.{bcolors.ENDC}")
        stream_to_kill = self._prev_stream
        timer = 0
        while True:
            if stream_to_kill != self._prev_stream:
                stream_to_kill = self._prev_stream
                timer = 0
            timer = timer + 1
            if timer > self._stream_switch_threshold:
                print(f"{bcolors.OKCYAN}[ROBOT] Info: Stream Killed {stream_to_kill}.{bcolors.ENDC}")
                self.streams[stream_to_kill].reset_stream()
                print(self.streams[stream_to_kill].status)
                break
            time.sleep(1)

    def mk_dir_if_not_exists(self,path):
        if not os.path.exists(path):
            os.mkdir(path)
            print(f"{bcolors.OKCYAN}[ROBOT] Info: Created a directory at {path}{bcolors.ENDC}")
            return True
        else:
            return False

    def _set_directory(self):

        print(f"{bcolors.OKCYAN}[ROBOT] Info: Updating Folders{bcolors.ENDC}")
        self.mk_dir_if_not_exists(self.FLASK_APP+self.IMAGES_FOLDER)
        self.mk_dir_if_not_exists(self.UPLOAD_FOLDER)
        self.mk_dir_if_not_exists(self.FLASK_APP+self.STREAM_FOLDER)

    def set_stream_pid(self,cam):
        for p in os.popen("tasklist | findstr ffmpeg"): 
            pid = int(p.split()[1])
            if pid not in self._stream_pids:
                self._stream_pids.append(pid)
                self.streams[cam].set_pid(pid)
            if len(self._stream_pids) > self.STREAMS:
                self._stream_pids.pop(0)
            