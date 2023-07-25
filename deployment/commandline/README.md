# Deployment

The deployment has changed significantly from the previous version. Before, each application is deployed in a separate namespace or project. The new way puts all 3 containers (edge-rtsp, robots-cpu and edge-server) in a singe pod to make the communication faster using localhost to reduce video ghosting.

The demo will be deployed in a namespace/project named 'edge-demo'.
You can use the optional paremeter 'targetFps' to set the frame rate at which the edge-server process the input video stream from the 'edge-rtsp' server.

See the section on 'Target Frame Rate'.

And the services are exposed using node ports.

## 1. Deploy using Podman
<pre>
podmanDeploy.sh amd64|arm64 [targetFps]
</pre>
amd64|arm64 means installing either amd64 or Arm64 version. Specify one or the other.

And point your browser at http://host:5005/

host is either the hostname or the node IP address.

## 2. Deploy to OpenShift
<pre>
openshiftDeploy.sh loggedinUser [targetFps]
</pre>
loggedinUser is the user used to login to OpenShift.

And point your browser at http://host:30505/

## 3. Deploy to MicroShift and Kubernetes
<pre>
microshiftAndKxsDeploy.sh amd64|arm64 [targetFps]
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

## 5. Target Frame Rate (targetFps parameter)
This parameter, if specified, is used to set the nominal frame rate at which the edge-server processes the input video stream. This is necessary to avoid video ghosting on slow CPUs as the processing of the frames cannot keep up with the video frames coming in.

Please read carefully on how it works or you may be surprised that it is no doing what your expect.

To keep things simple, we calculate the skipCount, the number of frames to skip after processing a frame, based on the formula below:

<pre>
skipCount = int(fps / float(targetFps))
...
if skipCount > 1 and frameId % skipCount != 0:
    continue

</pre>
where 
* fps is the input video stream frame rate,
* targetFps is the targetFps you specified in the command line, and
* frameId is the id (monotonically increasing number) of a frame in a video stream

The following table will help you understanding the impact of the targetFps value better.
| fps    | targetFps | skipCount |
| ------ | --------- | --------- |
| 15     | 1         | 15        |
| 15     | 2         | 7         |
| 15     | 3         | 5         |
| 15     | 4         | 3         |
| 15     | 5         | 3         |
| 15     | 6         | 2         |
| 15     | 7         | 2         |
| 15     | 8         | 1         |
| 15     | 9         | 1         |
| 15     | 10        | 1         |
| 15     | 11        | 1         |
| 15     | 12        | 1         |
| 15     | 13        | 1         |
| 15     | 14        | 1         |
| 15     | 15        | 1         |


The default targetFps value is:
* 7 for amd64, and
* 2 for arm64 (Raspberry pi 4)

You can experiment with the value of targetFps value to suit your device.


