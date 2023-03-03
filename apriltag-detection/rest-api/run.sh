#!/bin/bash

# Start the first process
python3 detect_apriltag.py --port 6000 &

  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?