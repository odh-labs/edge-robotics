import os
import cv2
import numpy as np
#from utils import preprocess_img, scale_coords, postprocess_ocr_yolov5
from .object import Object


class Vehicle(Object):
    def __init__(self, box, label, score, association=None, chunk_timestamp=None):
        """Initialize vehicle class.
        Args:
            box (list): bounding box.
            label (list): label.
            score (list): score.
        """
        super().__init__(box, label, score)
        self.id = None
        self.__lp_box = None
        self._lp_image_path = None
        self._image = None
        self._lp_image = None
        self._image_path = None
        self.__ocr = ""
        self.__ocr_hist = {}
        self.__count = 1
        self._skip_frame = 1
        self.__lp_orentation = None
        self.conf = 0.55
        self.__timestamp = None
        # uncomment to use centroid tracker
        # self.centroid = self.__calculate_centroid()
        
        self.update_timestamp(chunk_timestamp)
        self.update_association(association)

    def __repr__(self):
        return f"{self.id}, {self._label}, {self.__ocr}"

    def __calculate_centroid(self):
        return (self._bbox[0] + self._bbox[2]) // 2, (self._bbox[1] + self._bbox[3]) // 2

    def get_timestamp(self):
        return self.__timestamp

    def get_ocr(self):
        return self.__ocr

    def get_ocr_conf(self):
        return self.conf
        
    def set_id(self, _id):
        self.id = _id

    def get_id(self):
        return self.id

    def process_robot(self,
                frame,
                out_frame,
                buffer_threshold = 4,
                **kwargs):
        """Detect lp and do ocr for this vehicle detected in the current frame.
        Args:
            frame (numpy.ndarray): current frame.
            model_ocr_single (tensorrt-model): OCR model with input_size (240, 80).
            model_ocr_double (tensorrt-model): OCR model with input_size (240, 160). 
            clean_ocr (CleanOCR): OCR cleaning function.
        """

        x1, y1, x2, y2 = self._get_roi()
        # print(f"frame - {frame_no} - {x1,y1,x2,y2}")
        # extract vehicle
        vehicle = out_frame[y1:y2, x1:x2]
        # if x1 !=0 and x2 !=0 and y1!=0 and y2 !=0:
        #     im = Image.fromarray(vehicle)
        #     im.save(f"your_file_lp1{frame_no}.jpeg")
        if self._image is None :
            self._image = vehicle.copy()
        # print(self._image)             
        return True    

    def save_robot(self,cam_no):
        """
        Saves this vehicle and the (best ocr)license plate 
        after tracker evicts the vehicle from frame.
        """
        if self._image is None or min(self._image.shape[:2]) <= 0:
            return False
        basepath = f"images/cam_{cam_no}"

        self._image_path = f"{basepath}/robots/img_{self.id}_{self._label}.jpg"
        
        if not os.path.exists(f"flask_app/static/{basepath}/robots/"):
            os.mkdir(f"flask_app/static/{basepath}/robots/")

        cv2.imwrite("flask_app/static/"+ self._image_path, self._image)
        print("saved vehicle")
        
        return True


    def update_association(self, association):
        '''
        Updates the associated predicted lp with object
        '''
        self.__lp_box = association 
    
    def update_timestamp(self, chunk_timestamp):
        '''
        Updates the timestamp of the vehicle detection.
        '''
        if self.__timestamp is None:
            self.__timestamp = chunk_timestamp
