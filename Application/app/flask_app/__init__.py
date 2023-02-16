import os
from config import Config_ANPR,Config
from utils import bcolors
from flask import Flask
from flask_cors import CORS
from flask_jsglue import JSGlue
import logging
import sys
from datetime import datetime
from .robot import ROBOT

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"


CAM_OBJECTS = {}
config_ANPR = Config_ANPR(default=True)
config = Config(default=True)

# Get logger object
LOGS_DIR = "logs/"
UPLOAD_FOLDER = "images/"

if (os.name == 'nt'):
    log_filename = "{}logfile_{}.log".format(LOGS_DIR, str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
else:
    log_filename = "{}logfile_{}.log".format(LOGS_DIR, str(datetime.now()))
#import pdb;pdb.set_trace()
logging.basicConfig(filename=log_filename,
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
# Create web server object
app = Flask(__name__, static_url_path='')
cors = CORS(app)
jsglue = JSGlue(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
PIPELINE_CONFIG = config_ANPR.init_config['pipeline_config']

HOSTIP = "localhost"
PORT = "30000"
address = HOSTIP+":"+"PORT"

# Load models
robot = ROBOT(logger=logger)

if not robot.init_anpr():
    sys.exit(0)

for i in range(0,PIPELINE_CONFIG['stream_count']):
    if not robot.init_pipeline(i):
        logger.error(f"Unable to load")
        sys.exit(0)

logger.info(f"Loaded Pipeline")


print(f"{bcolors.HEADER}[Init] Info: Please copy the following link in your browser: http://{HOSTIP}:{PORT} \n{bcolors.ENDC}")
from .server import *
if(PIPELINE_CONFIG['autostart']):
    autostart()
    # init_stream_all()
