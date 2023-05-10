# What this directory does 
Wraps the yolo model in flask api and deploys it on openshift via Dockerfile. 

This is different from the files in the model folder in that:
1. it does not include the Nvidia support in torch and torchvision reducing the image size from 4.71G to 1.81G
2. Simplified the Dockerfile

# Directory contents
1. backend.py : Loads the model (yolov5s.pt) and expose the detect funtion as flask API  
2. yolov5s.pt : PyTorch trained YOLO v5 model to detect the B-Robot and R-Robot used in our edge demo 
3. ultralytics_yolov5_master : [Master repo from ultralytics](https://github.com/ultralytics/yolov5)  
4. Dockerfile : To deploy and expose the model on Openshift  
5. requirements.py : required python packages
6. run.py : Run locally on your machine at port 5000


# How to use
1. Copy yolov5.pt model into the directory and push to git 
   > Skip this step if you want to use the yolov5.pt provided in the directory already
2. Login to Openshift
3. In Developer preview click `+Add`
4. Select `Import from Git`
   1. Git Repo URL: https://github.com/odh-labs/edge-robotics/tree/main/model-lean
   2. Import Strategy: `Dockerfile`
      1. Dockerfile path: `Dockerfile`
   3. Target port: `5000`
   4. Create 
5. Model will be exposed at https://`<cluster-url`>/v1/object-detection/yolov5



