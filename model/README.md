# What this directory does 
Wraps the yolo model in flask api and deploys it on openshift via Dockerfile

# Directory contents
1. backend.py : Loads the model (yolov5s.pt) and expose the detect funtion as flask API  
2. yolov5s.pt : PyTorch trained YOLO v5 model to detect the B-Robot and R-Robot used in our edge demo 
3. ultralytics_yolov5_master : [Master repo from ultralytics](https://github.com/ultralytics/yolov5)  
4. Dockerfile : To deploy and expose the model on Openshift  
5. requirements.py : required python packages
6. run.py : Run locally on your machine at port 5000


# How to use
1. Copy yolov5.pt model into the directory and push to git
2. Login to Openshift
3. In Developer preview click +Add
4. Select Import from Git 
   1. Git Repo URL: https://github.com/odh-labs/edge-robotics/tree/main/model
   2. Import Strategy: Dockerfile
      1. Dockerfile path: model/Dockerfile
   3. Target port: 5000
   4. Create 
5. Model will be exposed at https://`<cluster-url`>/v1/object-detection/yolov5



