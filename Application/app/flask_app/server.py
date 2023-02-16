import os
import json
import logging, logging.config
from flask import request
from . import app
from . import *
from datetime import datetime
from utils import bcolors

#ImageFile.LOAD_TRUNCATED_IMAGES = True
import time

CWD = os. getcwd()

@app.after_request
def add_header(req):
    """
    Add headers to both force latest IE rendering or Chrome Frame,
    and also to cache the rendered page for 10 minutes
    """
    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers["Cache-Control"] = "public, max-age=0"
    return req

@app.route('/')
def home():
    return app.send_static_file('index.html') 

@app.route('/dashboard')
def dashboard():
    return app.send_static_file('index.html')

def autostart(rtspAddress=None,cam_no=-1,single_stream=False,wait_time = 1):
    # check if rtsp address exists already
    if rtspAddress is None:
        rtspAddress = []
        for cam_no in range(PIPELINE_CONFIG['stream_count']):
            try:
                file = f'.streamAddress_{cam_no}.txt' 
                with open(file, 'r') as filetoread:
                    rtsp = filetoread.read()
                    if rtsp == '':
                        continue
                    rtspAddress.append(rtsp)
            except Exception as e:
                continue
    
    # run pipeline
    flag = False
    for cam,rtsp in enumerate(rtspAddress):
        flag = robot.run_pipeline(rtsp,cam,wait_time)
        if not flag:
            break
        # time.sleep(2)
    
    message = "Successful"
    if not flag:
        message = "Unable to Start Stream"
        return {"flag":flag,"status":message}
            
    return {"flag":flag,"status":message}


# def gather_img():
#     while True:
#         img = robot._pipelines[0].fframe
#         _, frame = cv2.imencode('.jpg', img)
#         yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')
# @app.route("/mjpeg")
# def mjpeg():
#     return Response(gather_img(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/init_stream_all", methods=["POST"])
def init_stream_all():
    #time.sleep(20)
    try:
        cam_no = 0
        wait_time = 0.1
        try:
            rtspAddress = [request.form.get("RTSP")]
            wait_time = int(request.form.get("wait_time"))
        except:
            return json.dumps({"flag":False,"status":"Unable to Start Stream"})
        
        #print(request.get_json())
        print(rtspAddress)
        
        # rtspAddress.append(rtspAddress[0])
        for cam_no,rtsp in enumerate(rtspAddress):
            file = f'.streamAddress_{cam_no}.txt' 
            print(f"{bcolors.OKCYAN}[Server] Info: Stream Source: {rtsp}{bcolors.ENDC}")
            with open(file, 'w') as filetowrite:
                filetowrite.write(rtsp)
    
        return json.dumps(autostart(rtspAddress=rtspAddress,wait_time = wait_time))
    except Exception as exp:
        print(exp)
        return json.dumps({"flag":False,"status":"Unable to Start Stream"})

@app.route("/start_stream", methods=["POST"])
# @token_required
def start_stream():
    try:
        cam_no = int(request.form.get("cam_no")) or 0
    except:
        cam_no = 0
    result = robot.switch_stream(cam_no)

    return json.dumps({"status":result}) # Change



@app.route("/get_robot_data", methods=["GET"])
def get_robot_data():
    
    
    robot_data = robot.sqlite_db.fetch_robot_data()
    
    json_data = json.dumps(robot_data)
    return json_data

@app.route("/get_robot_status", methods=["GET"])
def get_robot_status():
    status_data= robot._pipelines[0].robot_status            
    json_data = json.dumps(status_data)
    return json_data

