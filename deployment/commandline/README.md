## Will be updated soon.
Usage:
edge-setup-openshift.sh username
- username is the user you have logged in to OpenShift

edge-setup-microshift.sh
- no input parameter required

All apps are deployed using node port to make using them easy for MicroShift.

Note that rtsp only installed the rtsp server. You need to stream video to it:
OpenShift:
ffmpeg -re -stream_loop -1 -r 15 -i $FILE -c copy -f rtsp rtsp://openshift-host-ip:30854/mystream

MicroShift:
ffmpeg -re -stream_loop -1 -i $FILE -c copy -f rtsp rtsp://192.168.130.11:30854/mystream

To invoke the annotated video with events, point you browser to:
http://host-ip:30505

