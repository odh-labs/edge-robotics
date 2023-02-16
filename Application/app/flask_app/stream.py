import os
import argparse
import shutil
import time
import threading
import hashlib
from utils.sys_colors import bcolors
class Stream:
    def __init__(self,config=None,cam = 0):
        
        self._config = config
        self._cam = str(cam)
        self._file_no = 1
        self._check_attempts = 40
        self._is_video = False
        try:
            self._os_type = 1 if os.name == 'nt' else 0
        except:
            self._os_type = 0
        
        self._CWD = os.getcwd()
        #self._os_type = 0
        if self._os_type == 1:
            self._stream_dir = self._CWD + "\\flask_app\\static\\live\\"
            self._cam_dir = self._stream_dir + "cam_" + self._cam
            self.STREAM_FILE = f"{self._cam_dir}\\stream_{self._cam}.bat"
            self._Default_Stream_File  = f"{self._stream_dir}/stream.bat"
        else:
            self._stream_dir = self._CWD + "/flask_app/static/live/"
            self._cam_dir = self._stream_dir + "/cam_" + self._cam
            self.STREAM_FILE = f"{self._cam_dir}/stream_{self._cam}.sh"
            self._Default_Stream_File  = f"{self._stream_dir}/stream.sh"

        self.set_stream_file(f"{self._stream_dir}/cam_{self._cam}")

        self.status = False
        self.source = None
        self.pid = 0
    
    def set_pid(self,pid):
        self.pid = pid
    
    def update_stream_file(self,source):
        try:
            if self._os_type == 1:
                with open(self.STREAM_FILE, "r") as filename:
                    lines = filename.readlines()
                    if "VIDSOURCE" in lines[0]:
                        lines[0] = "set VIDSOURCE="+"\""+source+"\"\n"
                    if "OUTPUT_PATH" in lines[1]:
                        lines[1] = "set OUTPUT_PATH="+"\""+self._cam_dir+"\\mystream.m3u8\"\n"
                    if "ffmpeg" in lines[6]:
                        if self._is_video:
                            lines[6] = "ffmpeg -i \"%VIDSOURCE%\" -y \"%VIDEO_OPTS%\" \"%OUTPUT_HLS%\" -hls_flags delete_segments \"%OUTPUT_PATH%\"\n"
                        else:
                            lines[6] = "ffmpeg  -rtsp_transport tcp -i \"%VIDSOURCE%\" -y \"%VIDEO_OPTS%\" \"%OUTPUT_HLS%\" -hls_flags delete_segments \"%OUTPUT_PATH%\"\n"
                    if "del" in lines[7]:
                        lines[7] = "del "+"\""+self._cam_dir+"\\mystream*\"\n"
                    filename.close()

                with open(self.STREAM_FILE, "w") as f:
                    for line in lines:
                        if line =='\"\n':
                            pass
                        else:
                            f.writelines(line)
                    f.close()
                print(f"{bcolors.OKBLUE}[Stream] Info: Stream file updated{bcolors.ENDC}")
            else:
                with open(self.STREAM_FILE, "r") as filename:
                    lines = filename.readlines()
                    if "VIDSOURCE" in lines[1]:
                        lines[1] = "VIDSOURCE="+"\""+source+"\"\n"
                    if "OUTPUT_PATH" in lines[2]:
                        lines[2] = "OUTPUT_PATH="+"\""+self._cam_dir+"/mystream.m3u8\"\n"
                    if "ffmpeg" in lines[8]:
                        # print(f"FFMPEG{self._is_video}")
                        if self._is_video:
                            lines[9] = "ffmpeg -i \"$VIDSOURCE\" -y $VIDEO_OPTS $OUTPUT_HLS -hls_flags delete_segments $OUTPUT_PATH\n"
                        else:
                            lines[9] = "ffmpeg  -rtsp_transport tcp -i \"$VIDSOURCE\" -y $VIDEO_OPTS $OUTPUT_HLS -hls_flags delete_segments $OUTPUT_PATH\n"
                    if "rm" in lines[8]:
                        lines[8] = "rm -rf "+"\""+self._cam_dir+"/mystream*\"\n"
                    filename.close()

                with open(self.STREAM_FILE, "w") as f:
                    for line in lines:
                        if line =='\"\n':
                            pass
                        else:
                            f.writelines(line)
                    f.close()
            return True
        except:
            return False
    
    def copy_file(self,target,destination):
        try:
            shutil.copy(target,destination)
            print(f"{bcolors.OKGREEN}[Stream] Info: File copied successfully{bcolors.ENDC}")
        # If source and destination are same
        except shutil.SameFileError:
            print(f"{bcolors.FAIL}[Stream] Info: Source and destination represents the same file{bcolors.ENDC}")
        # If there is any permission issue
        except PermissionError:
            print(f"{bcolors.FAIL}[Stream] Info: Permission denied{bcolors.ENDC}") 
        # For other errors
        except:
            print(f"{bcolors.FAIL}[Stream] Info: Error occurred while copying file{bcolors.ENDC}")
    
    def set_stream_file(self,path):
        
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"{bcolors.OKGREEN}[Stream] Info: Created a directory at {path}{bcolors.ENDC}")
            self.copy_file(self._Default_Stream_File,self.STREAM_FILE)    
        else:
            if not os.path.isfile(self.STREAM_FILE):
                self.copy_file(self._Default_Stream_File,self.STREAM_FILE) 

    def reset_stream(self):
        if self._os_type == 1:
            try:
                if self.pid > 0:
                    os.popen(f"taskkill /f /PID {self.pid}")
            
                # os.popen(f"del {self._cam_dir}\\*.bat")
                os.popen(f"del {self._cam_dir}\\*.ts")
                os.popen(f"del {self._cam_dir}\\*.txt")
                print(f"{bcolors.OKGREEN}[Stream] Info: Removed previous files{bcolors.ENDC}")
            except Exception as exp:
                print(exp)
                print(f"{bcolors.WARNING}[Stream] Info: Cannot remove previous stream files{bcolors.ENDC}")
                
        else:
            os.popen(f"kill -9 `ps -ax | grep stream_"+ self._cam +" | grep -v grep | awk '{ print $1 }'`")
            try:
                os.popen('rm -rf '+ self._stream_dir + '/cam_'+self._cam+'/mystream*')
                print('Removed previous .ts files')
            except Exception as exp:
                # print(exp)
                print("Cannot remove previous .ts files...!!!")
            #os.popen("kill -9 `ps -ax | grep "+ sync_file +" | grep -v grep | awk '{ print $1 }'`")
        self.status = False
        return True
    def check_ts_file(self):
        fname = f"{self._cam_dir}/mystream{self._file_no}.ts"
        count_flag = 0
        while not os.path.isfile(fname):
            print(f"{bcolors.OKBLUE}[Stream] Info: Waiting for live stream, Attempt #{count_flag}{bcolors.ENDC}")
            time.sleep(2)
            count_flag = count_flag + 1
            if(count_flag > self._check_attempts):
                return False
        print(f"{bcolors.OKGREEN}[Stream] Info: Streaming for Cam:{self._cam}{bcolors.ENDC}")
        return True
    
    def fixRTSP(self,rtspAddress):
        if not rtspAddress:
            return False
        rtspAddress_escaped = rtspAddress.translate(str.maketrans({"^":  r"^^",
                                          "&":  r"^&",
                                          ">":  r"^>",
                                          "<":  r"^<",
                                          "|":  r"^|"}))
        return rtspAddress_escaped
    
    def set_source(self,source):
        if self._is_video:
            if self._os_type == 1:
                self.source = self._CWD + "\\" + source
            else:
                self.source = self._CWD + "/" + source
        else:
            self.source = self.fixRTSP(source)


    def init_stream(self,source=None,is_video=False):
        self.reset_stream()
        
        if self.source is None and source is None:
            return False
        
        self._is_video = is_video
        
        if source is not None:
            self.set_source(source)
        
        self.status = self._init_stream()
        return self.status
    
    def _init_stream(self):
        
        if self.source is None or not self.source:
            return False
        timestr = time.strftime("%m%d_%H%M")
        log_file = f"stream_log_{timestr}.txt"

        if(len(self.source)>0):
            if not self.update_stream_file(self.source):
                return False
            try:
                if self._os_type == 1:
                    os.popen(self.STREAM_FILE + 
                        ' > ' + self._cam_dir + '/'+log_file+' 2>&1 &')
                    
                    # thread = threading.Thread(target=self.keep_sync, args=(self._cam_dir),daemon=True)
                    #print("Starting stream sync thread")
                    # thread.start()
                    if not self.check_ts_file():
                        return False
                    
                else:
                    os.popen('sh '+ self.STREAM_FILE+' > '
                            + self._cam_dir + '/'+log_file+' 2>&1 &')
                    # time.sleep(5)
                    # os.popen('sh '+ live_path +'/'+sync_file+'.sh '
                    #         + live_path +' > ' + live_path + '/log.txt 2>&1 &')
                    #print("Streaming concurrently...")
                    if not self.check_ts_file():
                        return False
            except Exception as exp:
                print(exp)
                print(f"{bcolors.FAIL}[Stream] Error: Unable to Start Stream:{self._cam}{bcolors.ENDC}")
                return False

            return True
        
        else:
            return False

    def keep_sync(live_path):
        filename = os.path.join(live_path,"stream_log.txt")
        sync_event = False
        while True:
            time.sleep(60)
            try:
                m1  = hashlib.md5(open(f"{filename}","r").read().encode()).hexdigest()
                with open(f"{filename}","r") as f:
                    m2 = hashlib.md5(f.read().encode()).hexdigest()
                    if m1==m2:
                        with open(live_path+"/pid.txt","r") as fr:
                            pid = int(fr.read())
                        os.popen(f"taskkill /f /PID {pid}")
                        win_live_path = live_path.replace("/","\\")
                        os.popen(f"del {win_live_path}\\mystream*")
                        os.popen(live_path + '/stream_0.bat' + 
                            ' > ' + live_path + '/stream_log.txt 2>&1 &')

                        ffmpeg_pid = ""
                        for p in os.popen("tasklist | findstr ffmpeg"):
                            ffmpeg_pid = p.split()[1]
                        with open(live_path+"/pid.txt","w") as fw:
                            fw.write(ffmpeg_pid)  
                    else:
                        print("Live Stream Sync in progess")
                if sync_event:
                    break 
            except:
                continue       
            m1=m2


if __name__=="__main__":
    
    AP = argparse.ArgumentParser()
    AP.add_argument("-i", "--rtsp", required=True, help="Path to input.")
    args = vars(AP.parse_args())
    mt=Stream(cam = 0)
    mt.init_stream(args["rtsp"])