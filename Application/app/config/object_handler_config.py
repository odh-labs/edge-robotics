import json
from .utils import read_json

class ObjectHandlerConfig:
    def __init__(self):
        self.top_lim = 5
        self.bottom_lim = 1438
        self.require_clean_ocr = True

        self.model_config = read_json("config/model_config.json")
        self.robot_model_config = self.model_config["robot"]