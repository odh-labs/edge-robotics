# What is model-lean?
Wraps the yolo model in flask api and deploys it onto openshift or podman. 

## 1. Differences from Files in the Model Directory
This is different from the files in the 'model' folder in that:
1. Removed Nvidia support in torch and torchvision to reduce the image size
2. Changed the based image (the old Debian image used has many vulnerabilities) to Fedora 38.
3. Removed the run.sh file
4. The new image built will no longer require Internet connection to work.

## 2. Directory contents
1. backend.py : Loads the model (yolov5s.pt) and expose the detect funtion as flask API  
2. yolov5s.pt : PyTorch trained YOLO v5 model to detect the B-Robot and R-Robot used in our edge demo 
3. ultralytics_yolov5_master : [Master repo from ultralytics](https://github.com/ultralytics/yolov5)  
4. Dockerfiles : To build container images for AMD-64 and ARM64  
5. requirements.txt files: required python packages for AMD-64 and ARM-64 builds


## 3. AMD-64 and ARM-64 Images
You can build an AMD-64 image on an Intel PC or an ARM-64 images on an ARM machine such as a Reapberry Pi 4.
The AMD-64 and ARM-64 images can be pulled from quay.io:
* quay.io/andyyuen/robots-cpu:latest
* quay.io/andyyuen/robots-cpu-arm64:latest

respectively.



