import argparse
import time
import threading
from streamer import StreamChunker, VideoWriter, VideoReader
from object_handler import ObjectHandler
from config import Config
from utils import Profiler,bcolors
import datetime
import datetime
class Pipeline:
    # @profile
    def __init__(self, config=None, roi=None,init_config=None,stream_configs=None,logger=None,models=None,whitelist = None,cam = 0):
        """Initialize the variables used for the pipeline.
        Args:
            config ([Config], optional): Provide custom configuration. Defaults to None.
        """

        # setup input/output source
        print(f"{bcolors.OKCYAN}[Pipeline] Info: Initiating pipeline: {cam}{bcolors.ENDC}")
        self.__width = None
        self.__height = None
        self.__fps = None
        self.__cam = int(cam)
        self.fframe = None
        self.robot_status=None

        self.__models = models
        # setup default configuration file
        config = config if config else Config(default=True)
        init_config = init_config

        # set detection limits
        self.__top_lim = config.top_lim
        self.__bottom_lim = config.bottom_lim

        
        self.__stream = None

        # create object handler
        
        self.__object_handler = ObjectHandler(
            config=config.object_handler_config,
            stream=self.__stream,object_detection_models=self.__models)
        
        self.__input_stream = None 
        self.__output_stream = None
        # Check for init flags
        self.__databaseFlag = init_config['database']
        self.__dbFrameCount = init_config['dbFrameCount']
        self.__duplicate_check = init_config['duplicate_check']
        self.__profile = init_config['profile']

        # print(stream_configs)
        self.__stream_config = stream_configs

        self.__stream_error = False

        self.__stop_event = False

        # create database
        if self.__databaseFlag:
            from db import Database
            self.__database = Database(config.database_config,duplicate_check=self.__duplicate_check)

        self.__roi = roi
        self.__thresold_ocr = 3
        self.to_be_removed = []

        self.__logger = logger
        self.__start = time.time()
        self.__stream_fail_wait = 60
    # loop over frames
    def check_motion_simple(self,input_list):
        if len(input_list)>2:
            last_x,last_y= input_list[-1]
            last1_x,last1_y =input_list[-2]
            #print('last',last_x,last_y)
            #print('last1',last1_x,last1_y)
            diff_x = abs(last_x-last1_x)
            diff_y = abs(last_y-last1_y)
            diff_sum = diff_x+diff_y
            if diff_sum < 1:
                return('Stopped')
            else:
                return('Moving')
        else:
            return('Initialising')

    def check_alert(self,input_list):
        reversed_list = input_list[::-1]
        i=0
        stop_count = 0
        while i < len(input_list):
            if reversed_list[i]=='Stopped':
                stop_count=stop_count+1
                i=i+1
            else:
                break
        time_stopped  = stop_count/30 #self.__input_stream.fps    
        return time_stopped
 
    def _process_input_streams(self):
        cam_no = self.__cam
        input_stream = self.__input_stream
        output_stream = self.__output_stream
        if input_stream is None:
            print(f"{bcolors.FAIL}[Pipeline] Error: Unable to reach stream {self.__cam}{bcolors.ENDC}")
            # print(f"Skipping stream: {cam_no}")
            return False
        print(f"{bcolors.OKCYAN}[Pipeline] Info: Reading Stream {self.__cam}{bcolors.ENDC}")
        robot_b_history = []
        robot_r_history = []
        status_b_history=[]
        status_r_history=[]
        alert_id = 0
        alert_r_message,alert_b_message = None,None
        for _, frame, chunk_timestamp in self.__input_stream:
            self.fframe =frame
            time_stamp = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            #print(time_stamp)
            alert_r = None
            alert_b = None
            #cv2.imwrite('./flask_app/static/input_frame.png',frame)
            #import pdb;pdb.set_trace()
            robot_r_status='Not in Frame'
            robot_b_status='Not in Frame'
            if self.__stream_error:
                if int(time.time() - self.__start_wait) > self.__stream_fail_wait:
                    self.__stream_error = False
                else:
                    # print(
                    #     f"[Process-Video] Warning:Cannot reach input stream {cam_no}, Will try again after {self.__stream_fail_wait} seconds.")
                    continue
            #try:
            out_frame = frame.copy()
            
            if self.__stop_event:
                # self.__object_handler.destroy()
                return True
            
            if self.__roi is not None:
                x1, y1, x2, y2 = self.__roi
                frame = out_frame.copy()[y1:y2, x1:x2]

            # if self.__input_stream.count >= 5000:
            #     break
            outstream_frame = None
            if input_stream.count % self.__stream_config['frameSkip'] == 0:
                # get objects
                #print(frame)
                _vehicles = self.__object_handler.update_robots_tracker(frame)
                for vehicle in _vehicles:
                    #import pdb;pdb.set_trace()
                                        
                    if vehicle[1]=='Robot-R':
                        x,y,w,h = vehicle[0].astype(int)
                        rx1,ry1,rx2,ry2 = x,y,(x+w),(y+h) 
                        robot_r_history.append([(rx1+rx2)/2,(ry1+ry2)/2])
                        robot_r_status=self.check_motion_simple(robot_r_history)
                    elif vehicle[1]=='Robot-B':
                        x,y,w,h = vehicle[0].astype(int)
                        bx1,by1,bx2,by2 = x,y,(x+w),(y+h) 
                        robot_b_history.append([(bx1+bx2)/2,(by1+by2)/2])
                        robot_b_status=self.check_motion_simple(robot_b_history)
                
                status_b_history.append(robot_b_status)
                status_r_history.append(robot_r_status)
                r_alert = self.check_alert(status_r_history)
                b_alert = self.check_alert(status_b_history)
                #print(r_alert,b_alert)
                if r_alert >0.1:#self._wait_time:
                    #print('Alert robot R stopped for greater than 1s')
                    alert_data={
                    'id': alert_id,
                    'label' :'Robot-R',
                    'timestamp' :time_stamp,
                    'alert_type': 'Stopped',
                    #'image' : frame[ry1:ry2,rx1:rx2]
                    }
                    alert_r='Stopped'
                    alert_id+=1
                    #print(alert_data)
                    self.__database.writeRobotAlert(alert_data)
                elif b_alert >0.1:#self._wait_time:
                    #print('Alert robot B stopped for greater than 1s')
                    alert_data={
                    'id': alert_id,
                    'label' :'Robot-B',
                    'timestamp' :time_stamp,
                    'alert_type': 'Stopped',
                    #'image' : frame[by1:by2,bx1:bx2]
                    }
                    alert_b='Stopped'
                    alert_id+=1
                    #print(alert_data)
                    self.__database.writeRobotAlert(alert_data)
                #print(robot_b_status,'robot:r',robot_r_status)
                #print(r_alert,b_alert)
                if robot_r_status=='Not in Frame':
                    alert_r = 'Not in Frame'
                    alert_data={
                    'id': alert_id,
                    'label' :'Robot-R',
                    'timestamp' :time_stamp,
                    'alert_type': 'Not in Frame',
                    }
                    
                    alert_id+=1
                    self.__database.writeRobotAlert(alert_data)
                elif robot_b_status=='Not in Frame':
                    alert_b = 'Not in Frame'
                    alert_data={
                    'id': alert_id,
                    'label' :'Robot-B',
                    'timestamp' :time_stamp,
                    'alert_type': 'Not in Frame',
                    }
                    
                    alert_id+=1
                    self.__database.writeRobotAlert(alert_data)

                objects = [{'Robot-R':'Not in Frame' if alert_r=='Not in Frame' else 'Detected'},
                            {'Robot-B':'Not in Frame' if alert_b=='Not in Frame' else 'Detected'}]
                if alert_r =='Stopped':
                    alert_r_message = 'Robot-R stopped moving at '+ str(time_stamp)
                elif alert_r =='Not in Frame':
                    alert_r_message = 'Robot-R moved out of frame at '+str(time_stamp)

                if alert_b =='Stopped':
                    alert_b_message = 'Robot-B stopped moving at '+str(time_stamp)
                elif alert_b =='Not in Frame':
                    alert_b_message = 'Robot-B moved out of frame at '+str(time_stamp)    
                alerts = [{'Robot-R':alert_r_message},{'Robot-B':alert_b_message}]

                self.robot_status = {'Objects':objects,'alerts':alerts}  
                
        
        # clean up the streams
        # self.__object_handler.destroy()
        if self.__input_stream is not None:
            self.__input_stream.release()

        if self.__output_stream is not None:
            self.__output_stream.release()
        
        if self.__profile:
            self.profile_time()

        self.__logger.info("Done.")
        return True

    # @profile
    def _process_video(self):
        """Run the entire pipeline on a video
        Returns:
            bool: False indicates that the inference breaks in between.
        """
        print(f"{bcolors.OKCYAN}[Pipeline] Info: Starting Run: {self.__cam}{bcolors.ENDC}")
        self.__start = time.time()
        warning = 0
        while not self.__stop_event:
            # try:
            tmp_flag = self._process_input_streams()
            warning += 1
            if not self.__stop_event:
                print(f"{bcolors.WARNING}[Pipeline] Warning: Cannot reach input stream, Putting main thread to sleep for {self.__stream_fail_wait} seconds for {self.__cam}{bcolors.ENDC}")
                time.sleep(self.__stream_fail_wait)
            # except Exception as exp:
            #     print(exp)
            if warning > 5:
                print(f"{bcolors.FAIL}[Pipeline] Error: Cannot reach input stream for {self.__cam}{bcolors.ENDC}")
                break
        print(f"{bcolors.OKBLUE}[Pipeline] Info: Stopped stream for {self.__cam}{bcolors.ENDC}")
    def init_streamer(self,input_file,wait_time):
        
        cam_no = self.__cam
        self.__stop_event = True
        # time.sleep(1)
        self._wait_time = wait_time
        if self.__input_stream is not None:
            self.__input_stream.release()
        if self.__output_stream is not None:
            self.__output_stream.release()

        with Profiler('streamChunker'):
            if input_file == '0' or input_file.startswith('rtsp') or input_file.startswith('http'):
                print(f"{bcolors.OKCYAN}[Pipeline] Info: Starting Stream Chunker:{self.__cam}{bcolors.ENDC}")
                
                self.__input_stream = StreamChunker(source=input_file,
                                                    chunk_size=self.__stream_config['chunk_size'],
                                                    wait_time=self.__stream_config['chunk_wait'],
                                                    chunk_dir="chunks_"+str(cam_no))
            else:
                self.__input_stream = VideoReader(input_file)
        if self.__stream_config['outStream']:
            self.__output_stream = VideoWriter(source=self.__input_stream,
                                            root_dir="",
                                            filename="test_out_"+str(cam_no))

        if self.__input_stream is None:
            print(f"{bcolors.FAIL}[Pipeline] Error: Invalid Video Source: skipping this source:{self.__cam}{bcolors.ENDC}")
            return False
        # global thread
        self.__stop_event = False
        return True
    def run(self,input,wait_time):
        self.__logger.info('>>> Starting Run')
        self.__stop_event = True
        
        self.init_streamer(input,wait_time)
        
        # global thread
        self.__stop_event = False
        
        thread = threading.Thread(target=self._process_video, daemon=True)
        thread.start()
        
        return True

    def stop_stream(self):
        try:
            self.__logger.info('>>> Stopping Run')
            self.__stop_event = True
            time.sleep(1)

            if self.__input_stream is not None:
                self.__input_stream.release()

            if self.__output_stream is not None:
                self.__output_stream.release()

            if self.__profile:
                self.profile_time()
            return True
        except Exception as exp:
            self.__logger.error(exp)
            return False


    def profile_time(self):
        self.__logger.info('=================Timing Stats=================')
        self.__logger.info("FPS: {}".format(self.__input_stream.count/(time.time()-self.__start)))
        self.__logger.info(f"Total Time: {time.time()-self.__start}s")
        self.__logger.info(f"streamChunker: {Profiler.get_avg_millis('streamChunker')} ms")
        self.__logger.info(f"detect_Vehicles: {Profiler.get_avg_millis('detect_Vehicles')} ms")
        self.__logger.info(f"postProcess_Vehicles: {Profiler.get_avg_millis('postProcess_Vehicles')} ms")
        self.__logger.info(f"detect_LPs: {Profiler.get_avg_millis('detect_LPs')} ms")
        self.__logger.info(f"postProcess_LPs: {Profiler.get_avg_millis('postProcess_LPs')} ms")
        self.__logger.info(f"track: {Profiler.get_avg_millis('track')} ms")
        self.__logger.info(f"detect_OCR: {Profiler.get_avg_millis('detect_OCR')} ms")
        self.__logger.info(f"postProcess_OCR: {Profiler.get_avg_millis('postProcess_OCR')} ms")
        self.__logger.info(f"Database: {Profiler.get_avg_millis('Database')} ms")
        self.__logger.info(f"inference: {Profiler.get_avg_millis('inference')} ms")
        self.__logger.info(f"non_max: {Profiler.get_avg_millis('non_max')} ms")
        self.__logger.info(f"post_process_image: {Profiler.get_avg_millis('post_process_image')} ms")
if __name__ == '__main__':
    AP = argparse.ArgumentParser()
    AP.add_argument("-i", "--video", required=True, help="Path to input video.")
    AP.add_argument("-o", "--output", required=True, help="Path to output video.")
    args = vars(AP.parse_args())

    pipe = Pipeline(None, args["video"], args["output"], None, True)
    pipe.run()

