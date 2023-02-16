# import pyrebase
import datetime
#from pickle import TRUE
from .sqlite_tool import SQLiteTool
from .sys_colors import bcolors
import os 
import cv2 

class Database:
    def __init__(self, config,duplicate_check=8,whitelist_counter=1):

        self.__sqlite_db = SQLiteTool()
        self.__lpslist = []
        self.__thresold_ocr = 3
        self.__duplicate_check = duplicate_check
        self._whitelist_counter = whitelist_counter

    def get_current_time(self):
        return datetime.datetime.now()

    def saveRobotImage(self,img,img_path):
        cv2.imwrite(img_path, img)

    def writeRobotAlert(self, data_robot):
        basepath = "images"
        if not os.path.exists(f"flask_app/static/{basepath}/robots/"):
            os.mkdir(f"flask_app/static/{basepath}/robots/")
        main_path = f"flask_app/static/{basepath}/robots/"
        img_path = main_path + data_robot['label'] + str(data_robot['id'])+'.png'
        im_path_db = f"{basepath}/robots/" + data_robot['label'] + str(data_robot['id'])+'.png'
        #self.saveRobotImage(data_robot['image'],img_path)
        #print("Saved Images")
               
        
        vehicle_data = {
            "label": data_robot['label'],
            #"image_path": im_path_db,
            "alert_type":data_robot['alert_type'],
            # "timestamp": str(datetime.datetime.now()),
            "timestamp": data_robot['timestamp'],
            "id":data_robot['id']}
            
            # "violations": vehicle.get_violations() if len(vehicle.get_violations()) > 0 else "NaN"}
        # print(vehicle_data)
        
        # SQLITE DB insertion
        a = self.__sqlite_db.insert_robot(vehicle_data)
        #print(a)
            
                #print(f'{bcolors.FAIL}[DB] Info: Flagged {vehicle_data["ocr"]} detected{bcolors.ENDC}')

            # self.__sqlite_db.disconnect()