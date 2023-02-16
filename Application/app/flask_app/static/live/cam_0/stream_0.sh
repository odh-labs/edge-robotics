#!/bin/bash
VIDSOURCE="D:\guise_robot/test.mov"
OUTPUT_PATH="D:\guise_robot/flask_app/static/live//cam_0/mystream.m3u8"
VIDEO_OPTS="-c:v h264 -preset:v ultrafast -g 48 -keyint_min 48 -sc_threshold 0 -b:v 2500k -maxrate 2675k -bufsize 3750k -threads 1 -movflags +faststart -tune zerolatency"
OUTPUT_HLS="-hls_time 5 -hls_list_size 5 -start_number 1"
while :
do
echo "Starting Conversion..."
ffmpeg -rtsp_transport tcp -i "$VIDSOURCE" -y $VIDEO_OPTS $OUTPUT_HLS -hls_flags delete_segments $OUTPUT_PATH
ffmpeg -i "$VIDSOURCE" -y $VIDEO_OPTS $OUTPUT_HLS -hls_flags delete_segments $OUTPUT_PATH
echo "deleted old files"
done