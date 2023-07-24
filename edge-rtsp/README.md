# A simple RTSP Server

This is a simple change based on the:
<pre>
docker.io/aler9/rtsp-simple-server
</pre>
 image. The only change is to run the container as a non-root user with uid=1000 and gid=1000. 

The AMD-64 and ARM-64 images can be pulled from quay.io:
* quay.io/andyyuen/edge-rtsp:latest
* quay.io/andyyuen/edge-rtsp-arm64:latest

respectively.
