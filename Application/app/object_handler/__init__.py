import random
import numpy as np
from utils import Profiler



class ObjectHandler:
    def __init__(self, config, stream=None,object_detection_models=None):
        """Initialize object handler.
        Args:
            config (Config): Configuration for object handler.
        """
        self.__config = config
        
        self._model_robot = object_detection_models['model_robot']
       
        self._colors = self.__get_colors()
    # def get_vehicles(self):
    #     return iter(self._vehicles)

    # def get_persons(self):
    #     return iter(self._persons)
    
    def __get_colors(self):
        colors = dict()
        for label in self._model_robot.classes:
            colors[label] = [random.randint(0, 255) for _ in range(3)]
        return colors

    # def __repr__(self):
    #     return f"Vehicles: {len(self._vehicles)}, Persons: {len(self._persons)}"
    
    def __filter_detections(self, boxes, labels, scores, vl_class):
        """Filter detections based on limits and classes.
        Args:
            boxes (list): bounding boxes.
            labels (list): labels corresponding to the bounding boxes.
            scores (list): scores corresponding to the bounding boxes.
            vl_class (list): classes to filter for.
        Returns:
            list: list of tuple of box, label, score.
        """
        # filter based on upper and lower limits (y coordinate)
        # in_range = lambda y: self.__top_lim <= y <= self.__bottom_lim
        # check valid class
        valid_class = lambda cls: cls in vl_class
        return [(box, label, score) for box, label, score in zip(boxes, labels, scores) if valid_class(label)]

    def xyxy2xywh(self, x):
        """Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
        """
        y = np.zeros_like(x)
        y[:, 0] = x[:, 0]
        y[:, 1] = x[:, 1]
        y[:, 2] = x[:, 2] - x[:, 0]  # width
        y[:, 3] = x[:, 3] - x[:, 1]  # height
        return y

    
    def update_robots_tracker(self, frame):
        """Update the objects to be detected. Format for DeepSort
        Args:
            frame (numpy.ndarray): frame to run detection on.
            detections (list, optional): list of detections. Defaults to None.
        """       
        with Profiler('detect_Robots'):
             
            boxes, labels, scores = self._model_robot._do_inference(frame)
            #print(boxes)
            '''print(boxes)
            boxes = boxes.astype(int)
            print(boxes,labels)'''
        with Profiler('postProcess_robots'):
            boxes_xywh = self.xyxy2xywh(boxes)
            #print(boxes_xywh)
            _vehicles = self.__filter_detections(boxes_xywh, 
                                                    labels, 
                                                    scores, 
                                                    vl_class=['Robot-R', 'Robot-B'])
            # print(_vehicles)
            try:
                _vehicles  = np.array(_vehicles) 
            except Exception as exp:
                pass
                # print("Error in detection for frame")
        
        return _vehicles
    


    def process_robots(self, frame, out_frame, tracker=None, frame_no=0, chunk_timestamp=None,_vehicles=list(),_lps=list(),draw_flag = False):
        """Track and update lp/ocr for a vehicle.
        Args:
            frame (numpy.ndarray): current frame.
            tracker (Tracker, optional): Tracker to keep tracking of vehicles. Defaults to None.
        """
        
        with Profiler('track'):
            if tracker:
                #import pdb;pdb.set_trace()
                _vehicles = tracker.update(_vehicles, _lps, out_frame, chunk_timestamp)
        print(_vehicles)
        for vehicle in _vehicles:
            # process lp and ocr
            vehicle.process_robot(
                frame, 
                out_frame, 
                model_helmet=None,
                frame_no=frame_no,
            )
            # print(vehicle)
            if draw_flag:
                vehicle.draw(out_frame,self._colors)
        return out_frame
    def draw(self, frame,_vehicles):
        """Draw objects on frame.
        Args:
            frame (numpy.ndarray): Frame to draw on.
        """
        for vehicle in _vehicles:
            vehicle.draw(frame, self._colors)

        # boxes overlap with rider
        for person in self._persons:
            person.draw(frame, self._colors)
    
    def destroy(self):
        print("Cleaning up ...", end="")
        # self._model_ocr._destroy()
        # self._yolo_lpd._destroy()
        # self._yolo_od._destroy()
        # print()
