FROM docker.io/library/python:3.8-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install build-essential cmake ffmpeg libsm6 libxext6 -y
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod -R 777 /app

RUN chgrp -R 0 /app && chmod -R g=u /app

# Expose the port
EXPOSE 6000

CMD ./run.sh