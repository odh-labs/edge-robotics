# Under Construction

***All files in this folder are subject to minor/major changes.***

## 1. Prerequisites to run Demo:
1. A RTSP server streaming video as input
2. The Inference REST API to detect trackRobotsApp
3. A virtua environment having all the required packages in the requirements.txt installed
4. start the flask app: 
        python trackRobotsApp.py 
    using default options

## 2. Ways to run:
1. point your browser to the root flask app URL eg, http://host:port/
2. open the robotTracking.html using a browser. Note the URLs are hardcoded (for now).
    You may need to change them.

Getting help:
~~~~
python trackRobotsApp.py --help
usage: trackRobotsApp.py [-h] [--port PORT] [--RTSP_URL RTSP_URL]
                         [--INFERENCE_API_URL INFERENCE_API_URL]
                         [--DETECTION DETECTION]

Flask api exposing robot tracking video and metadata

options:
  -h, --help            show this help message and exit
  --port PORT           eg, port 5005
  --RTSP_URL RTSP_URL   eg, rtsp://localhost:8554/mystream
  --INFERENCE_API_URL INFERENCE_API_URL
                        eg, http://127.0.0.1:5000/v1/object-detection/yolov5
  --DETECTION DETECTION
                        eg, Yolo or Apriltag

~~~~
Example:
~~~~
python trackRobotsApp.py

using default options is equivalent to:

python trackRobotsApp.py --port 5005 \
--INFERENCE_API_URL http://localhost:5000/v1/object-detection/yolov5 \
--RTSP_URL  rtsp://localhost:8554/mystream \
--DETECTION Yolo
~~~~
