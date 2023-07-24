# Tracking the Robots

The edge-server is the application to track the robots and display the annotated video and events.

## 1. Prerequisites to run the Demo:
1. A RTSP server streaming video to the edge server
2. ffmpeg to stream a video or a camera video stream to the RTSP server as input
3. The AI Inference REST API to detect our robots in an image
4. The edge server gets its video feed from the RTSP server and uses the REST API to detect the robots and tracks their movements.

## 2. Ways to run:
1. Deploy all components using podman and point your browser at http://host:5005/
2. Deploy all components on OpenShift/MicroShift and point your browser at http://host:30505/
3. Deploy all components on Kubernetes and point your browser at http://host:30505/

More information on how to deploy the components can be found in folder: "deployment/commandline"

## 3. AMD-64 and ARM-64 Images
You can build an AMD-64 image on an Intel PC or an ARM-64 images on an ARM machine such as a Reapberry Pi 4.
The AMD-64 and ARM-64 images can be pulled from quay.io:
* quay.io/andyyuen/edge-server:latest
* quay.io/andyyuen/edge-server-arm64:latest

respectively.