# Deployment

The deployment has changed significantly from the previous version. Before, each application is deployed in a separate namespace or project. The new way puts all 3 containers (edge-rtsp, robots-cpu and edge-server) in a singe pod to make the communication faster using localhost to reduce video ghosting.

The demo will be deployed in a namespace/project named 'edge-demo'.

And the services are exposed using node ports.

## 1. Deploy using Podman
<pre>
podmanDeploy.sh amd64|arm64
</pre>
amd64|arm64 means installing either amd64 or Arm64 version. Specify one or the other.

And point your browser at http://host:5005/

host is either the hostname or the node IP address.

## 2. Deploy to OpenShift
<pre>
openshiftDeploy.sh loggedinUser
</pre>
loggedinUser is the user used to login to OpenShift.

And point your browser at http://host:30505/

## 3. Deploy to MicroShift and Kubernetes
<pre>
microshiftAndKxsDeploy.sh amd64|arm64
</pre>
amd64|arm64 means installing either amd64 or arm64 version. Specify one or the other.

And point your browser at http://host:30505/


## 4. Set Up Video Source
You have to set up the video source (a video file or a camera video stream) to the edge-rtsp container. The command line described below is for streaming a video file defined in the environment variable: $FILE

For podman:
<pre>
ffmpeg -re -stream_loop -1 -i $FILE -c copy -f rtsp rtsp://host:8554/mystream
</pre>

For OpenShift/MicroShift/KxS:
<pre>
ffmpeg -re -stream_loop -1 -i $FILE -c copy -f rtsp rtsp://host:30854/mystream
</pre>

