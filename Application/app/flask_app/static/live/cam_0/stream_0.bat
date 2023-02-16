set VIDSOURCE="rtsp://admin:cpplus123@183.82.250.57:554/cam/realmonitor?channel=1^&subtype=0"
set OUTPUT_PATH="D:\robot_container\app\flask_app\static\live\cam_0\mystream.m3u8"
set VIDEO_OPTS="-c:v h264 -preset:v ultrafast -g 48 -keyint_min 48 -sc_threshold 0 -b:v 2500k -maxrate 2675k -bufsize 3750k -threads 1 -movflags +faststart -tune zerolatency"
set OUTPUT_HLS="-hls_time 5 -hls_list_size 5 -start_number 1"
:loop
echo "Starting Conversion..."
ffmpeg  -rtsp_transport tcp -i "%VIDSOURCE%" -y "%VIDEO_OPTS%" "%OUTPUT_HLS%" -hls_flags delete_segments "%OUTPUT_PATH%"
del "D:\robot_container\app\flask_app\static\live\cam_0\mystream*"
echo "Deleted old files"
goto loop