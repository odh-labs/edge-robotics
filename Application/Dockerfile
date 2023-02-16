#FROM openvino/ubuntu20_runtime
FROM docker.io/openvino/ubuntu20_runtime
ENV TZ=Australia/Sydney \
    DEBIAN_FRONTEND=noninteractive
WORKDIR /guise

USER root
RUN apt-get update -y \
    && apt-get install -y python3-pip python3-dev \
    && apt-get install -y ffmpeg \
    && apt-get install tree

# COPY <file/folder-to-copy> <file/folder-to-copy> <destination>
# app/ , /app/ , app , ./app/ will copy all files in 'app' to /guise/ folder. Not app folder itself !!!!

COPY requirements.txt app /guise/
# Tree command to see folder structure
RUN tree /guise/
RUN python3 -m pip install -r requirements.txt

RUN chmod -R 777 /guise/
RUN chgrp -R 0 /guise/ && chmod -R g=u /guise/

# RUN python3 -m pip install openvino
EXPOSE 30000
CMD [ "python3","-u","/guise/run.py" ]
