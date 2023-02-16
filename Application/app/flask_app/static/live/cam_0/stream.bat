set VIDSOURCE="test1.mp4"
set OUTPUT_PATH="D:\Guise\guise_anpr_dev\flask_app\static\live\cam_0\mystream.m3u8"
set VIDEO_OPTS="-c:v h264 -preset:v ultrafast -g 48 -keyint_min 48 -sc_threshold 0 -b:v 2500k -maxrate 2675k -bufsize 3750k -threads 1 -movflags +faststart"
set OUTPUT_HLS="-hls_time 5 -hls_list_size 5 -start_number 1"
:loop
echo "Starting Conversion..."
ffmpeg -i "%VIDSOURCE%" -y "%VIDEO_OPTS%" "%OUTPUT_HLS%" -hls_flags delete_segments "%OUTPUT_PATH%"
del "D:\Guise\guise_anpr_dev\flask_app\static\live\cam_0\mystream*"
echo "Deleted old files"
goto loop