FROM registry.fedoraproject.org/fedora:36

RUN dnf install -y \
https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-36.noarch.rpm \
https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-36.noarch.rpm

RUN dnf install  -y ffmpeg python3 python3-pip && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod -R 777 /app

RUN chgrp -R 0 /app && chmod -R g=u /app

EXPOSE 5005

CMD [ "python", "trackRobotsApp.py" ]
