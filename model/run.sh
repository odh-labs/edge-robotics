#!/bin/bash

# Start the first process
python3 backend.py --port 5000 &

  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?