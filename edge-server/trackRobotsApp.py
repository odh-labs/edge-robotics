import cv2
import requests
import json
import time
import datetime
#import uuid
import os
import glob
import configparser
from RobotTracker import RobotTracker, State
from flask import Flask, render_template, request, Response
from flask_sock import Sock
from collections import deque
from YoloObjectDetection import YoloObjectDetection
from ApriltagObjectDetection import ApriltagObjectDetection

app = Flask(__name__)

sock = Sock(app)
wsQueue = deque()
tmpFolder = "video_frame"

# def doHousekeeping():
#     # check if folder exists
#     if os.path.exists(tmpFolder):
#         # remove tmp files
#         files = glob.glob(tmpFolder +"/*.jpg")
#         for f in files:
#             os.remove(f)
#     else:
#         # create folder
#         os.makedirs(tmpFolder)

# draw stats on image
def drawStats(robot, image, y):
    color = (0, 0, 255)
    if robot.getName() == "B-Robot":
        color = (255, 0, 0)
    cv2.putText(image, "{}: {}".format(robot.getName(), robot.getState()), 
        (10, y), cv2.FONT_HERSHEY_SIMPLEX, .5, color, 2)
    cv2.putText(image, "{}: Stopped for {:.3f}s".format(robot.getName(), robot.getStoppageTime()), 
        (10, y + 18), cv2.FONT_HERSHEY_SIMPLEX, .5, color, 2)

# video generator. Each client has its own video generator.
def generateFrames(ws): 

    # variable used in calaculating fps
    prev_time = time.time()
    frCount = 0
    fps = str(0)

    # set up RobotTrackers
    robots = {}
    detect = None
    if detection == "Apriltag":
        robots["Robot-0"] = RobotTracker("Robot-0", State.UNKNOWN)
        robots["Robot-1"] = RobotTracker("Robot-1", State.UNKNOWN)
        detect = ApriltagObjectDetection(apriltag_url, "image")
    elif detection == "Yolov5":
        robots["B-Robot"] = RobotTracker("B-Robot", State.UNKNOWN)
        robots["R-Robot"] = RobotTracker("R-Robot", State.UNKNOWN)
        detect = YoloObjectDetection(yolov5_url, "image")
    else:
        msg = "Unsupported detection method: " + detection
        raise Exception(msg)

    # set up external services
      
    vcap = cv2.VideoCapture(rtsp_url)
    fps = vcap.get(cv2.CAP_PROP_FPS)
    skipCount = int(fps / float(target_fps))

    # save copy of the frame for later use
    #filename = "video_frame/" + uuid.uuid4().hex + ".jpg"
    while True:
        # Capture a frame for processing
        success, frame = vcap.read()
        if not success or frame is None:
            print("Failed to read frame or frme is None.")
            break
        else:
            frameId = int(round(vcap.get(1)))
            if skipCount > 1 and frameId % skipCount != 0:
                continue

            rowCall = {}

            image = frame.copy()
            # cv2.imwrite(filename, frame)
            success, jpeg = cv2.imencode(".jpg", frame)

            eventList = []

            # call inference REST API
            # detect.invokeModel(filename)
            detect.invokeModel(jpeg.tobytes())
            # os.remove(filename)
            count = 0
            for d in detect.getNameCenterAndConfidence():

                (name, corner, center, confidence) = d
                if float(confidence) < .6:
                    continue

                if name in robots:
                    count += 1
                    rowCall[name] = 1

                    # draw center of detected robot in saved image
                    cv2.circle(image, center, 4, (0, 0, 255), -1)

                    # draw robot name and confidence level in saved image
                    nameStr =("Id: {}  {:.3f}".format(name, confidence))
                    cv2.putText(image, nameStr, (corner[0], max(10, corner[1] - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    # print("Id: {}".format(name))

                    # update robot state
                    curRobot = robots.get(name)
                    if curRobot.updateStateTrackingCenter(center[0], center[1]):
                        msg = "{}: {} at {}".format(datetime.datetime.now().strftime("%H:%M:%S"),
                                name, curRobot.getState()
                                )
                        eventList.append(msg)
                        print(msg)
                
            # identify if there is any out-of-view robots
            for key in robots.keys():
                if key not in rowCall:
                    robot = robots[key]
                    if robot.updateStateDirect(State.OUT_OF_VIEW):
                        msg ="{}: {} at {}".format(datetime.datetime.now().strftime("%H:%M:%S"),
                            robot.getName(), robot.getState()
                            )
                        eventList.append(msg)
                        print(msg)

            if ws is not None:
                try:
                    # print("reached ws processing.")
                    for event in eventList:
        
                        print("Event=" + event)
                        ws.send(json.dumps({
                                'text': event
                        }))
                except:
                    break
            else:
                print("ws not set in generateFrames.")
                break          
            eventList.clear()

            # calculate FPS
            frCount += 1
            interval = time.time() - prev_time
            if (interval) >= 1.:
                # calculate FPS
                fps = str(round(frCount / interval))
                prev_time = time.time()
                frCount = 0

            # draw state info near top left-hand corner on image
            if count != 0:
                y = 15
                for key in robots.keys():
                    drawStats(robots[key], image, y)
                    y += 36

            # display FPS near top right-hand corner
            cv2.putText(image, fps, (image.shape[1] - 120, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)
        
            # convert image to jpeg and let client display jpeg images quickly to simulate a video
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

# Stream video to the client
@app.route('/video')
def video():

    ws = None

    for x in range(3):
        if len(wsQueue) == 0:
            print("Waiting to get ws.")
            time.sleep(2)

    if len(wsQueue) == 0:
        # failed to get client websocket, no video will be streamed
        print("wsQueue empty.")
        return "No websocket for event notification."
    else:
        ws = wsQueue.popleft()
        print ("ws set.")

    # invoke video generator to get frames
    return Response(generateFrames(ws), mimetype='multipart/x-mixed-replace; boundary=frame')

# render home page
@app.route('/')
def renderPage():
    return render_template('index.html')


# let client register its websocket for receiving events
@sock.route('/events')
def events(ws):
    print("Reached events route.")

    wsQueue.append(ws)
    while True:
        data = ws.receive()
    #     if data == 'stop':
    #         break


if __name__ == '__main__':

    # doHousekeeping()
    
    section = 'DEFAULT'

    config = configparser.ConfigParser()
    #config.read('/app/config/properties.ini')
    config.read('config/properties.ini')
    # if section == 'DEFAULT':
    #     config.read('/app/config/properties.ini')
    # else:
    #     config.read('./config/properties.ini')

    rtsp_url = config[section]['rtsp_url']
    yolov5_url = config[section]['yolov5_url']
    apriltag_url = config[section]['apriltag_url']
    # detection can be either 'Yolov5' or 'Apriltag'
    #detection = config[section]['detection']
    target_fps = os.environ['TARGET_FPS']
    detection = os.environ['DETECTION'] 
    print("* {}: {}".format('rtsp_url', rtsp_url))
    print("* {}: {}".format('target_fps', target_fps))
    print("* {}: {}".format('yolov5_url', yolov5_url))
    print("* {}: {}".format('apriltag_url', apriltag_url))
    print("* {}: {}".format('detection', detection))
    app.run(host="0.0.0.0", port=5005)
