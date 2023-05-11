FROM registry.fedoraproject.org/fedora:38

RUN dnf install -y \
https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-38.noarch.rpm \
https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-38.noarch.rpm

RUN dnf update -y && \
dnf install -y ffmpeg python3-pip && \
ln -s /usr/bin/python3 /usr/bin/python 

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod -R 777 /app

RUN chgrp -R 0 /app && chmod -R g=u /app

# Expose the port
EXPOSE 5000

CMD ["python", "backend.py"]
