# What this directory does 
Wraps the yolo model in flask api and deploys it on openshift via Dockerfile. 

This is different from the files in the model folder in that:
1. No longer include Nvidia support in torch and torchvision to reduce the image size
2. Changed the based image (the old Debian image used has many vulnerabilities) to Fedora 38.
3. Removed the run.sh file
4. The new image built will no longer require Internet connection to work.

# Directory contents
1. backend.py : Loads the model (yolov5s.pt) and expose the detect funtion as flask API  
2. yolov5s.pt : PyTorch trained YOLO v5 model to detect the B-Robot and R-Robot used in our edge demo 
3. ultralytics_yolov5_master : [Master repo from ultralytics](https://github.com/ultralytics/yolov5)  
4. Dockerfile : To deploy and expose the model on Openshift  
5. requirements.txt : required python packages


# How to use
Create image using:
podman build -t robots-cpu .



