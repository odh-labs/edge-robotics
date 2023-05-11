FROM registry.fedoraproject.org/fedora:38

RUN dnf install -y \
https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-38.noarch.rpm \
https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-38.noarch.rpm

RUN dnf install  -y cmake ffmpeg python3 python3-pip && ln -s /usr/bin/python3 /usr/bin/python && \
dnf group install -y "C Development Tools and Libraries" "Development Tools"

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && \
chmod -R 777 /app && \
chgrp -R 0 /app && chmod -R g=u /app && \
mkdir -p /.cache/hub/ultralytics_yolov5_master && \
p -r ultralytics_yolov5_master /.cache/hub/ultralytics_yolov5_master && \
mkdir -p /.local && \
chgrp -R 0 /.cache && chmod -R g=u /.cache && \
chgrp -R 0 /.local && chmod -R g=u /.local

# Expose the port
EXPOSE 6000

CMD [ "python", "detect_apriltag.py" ]
