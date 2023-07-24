FROM registry.fedoraproject.org/fedora:38

RUN dnf install -y \
https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-38.noarch.rpm \
https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-38.noarch.rpm

RUN dnf install -y cmake gcc gcc-c++ ffmpeg python3 python3-pip python3-devel python3-wheel && \
ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ARG user=appuser
ARG group=appuser
ARG uid=1000
ARG gid=1000
RUN groupadd -g ${gid} ${group} && \
	useradd -u ${uid} -g ${group} ${user} && \
	chown -R ${uid}:${gid} /app &&  \
	chmod -R 777 /app 

# Expose the port
EXPOSE 6000

USER ${uid}:${gid}

CMD [ "python", "detect_apriltag.py" ]
