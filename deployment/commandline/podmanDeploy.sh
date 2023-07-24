#! /bin/bash

# check if required parameter is present in command line
if [ $#  -ne 1  ]; then
	echo "Usage: $0 amd64|arm64"
	exit 1
fi
if [ \( $1  != "amd64" \) -a \( $1 != "arm64" \) ]; then
        echo "Usage: $0 amd64|arm64"
        exit 2
fi
if [ $1 == "arm64" ]; then
	SUFFIX="-$1"
fi

#echo "SUFFIX=$SUFFIX"


# create pod
podman pod create \
--name edge-demo-pod \
-p 8554:8554 \
-p 5000:5000 \
-p 5005:5005 

# add rtsp container
podman run -d --rm --pod edge-demo-pod \
-e RTSP_PROTOCOLS=tcp --name rtsp \
quay.io/andyyuen/edge-rtsp${SUFFIX}:latest

# add yolo5 AI model
podman run -d --rm --pod edge-demo-pod \
--name yolo quay.io/andyyuen/robots-cpu${SUFFIX}:latest

# add edge-server container
podman run -d --rm --pod edge-demo-pod \
-e TARGET_FPS=2 \
--name edge-server quay.io/andyyuen/edge-server${SUFFIX}:latest
