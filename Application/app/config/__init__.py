import json
from .object_handler_config import ObjectHandlerConfig
# from .centroidtracker_config import CentroidTrackerConfig
from .utils import read_json


class Config:
    """
	Default configuration file for Pipeline.
	Please Make necessary changes to paths/hyper-params values below
	"""
    def __init__(self, default=True):
        self.object_handler_config = ObjectHandlerConfig()
        # self.centroidtracker_config = CentroidTrackerConfig()
        # self.dlibtracker_config = read_json("config/dlib_tracker.json")
        # self.deepsort_tracker_config = read_json("config/deep_sort_tracker_config.json")
        self.byte_tracker_config = read_json("config/byte_tracker_config.json")
        self.database_config = read_json("config/db_config.json")
        # self.database_config = read_json("config/db_config.json")
        # self.traffic_light_config = read_json("config/traffic_light.json")["main.mp4"]
        # self.violation_detector_config = read_json("config/violation_config.json")e

        self.top_lim = 5
        self.bottom_lim = 1438

class Config_ANPR:
    def __init__(self, default=True):
        self.init_config = read_json("config/init_config.json")