### preping the FDO server ###
echo 'installing the FDO binaries'
sudo dnf install -y fdo-admin-cli-0.4.5-1.el8.x86_64  fdo-manufacturing-server
echo 'enabling the fdo-aio.service'
sudo systemctl enable --now fdo-aio.service 
echo 'check status of fdo-aio service'
systemctl status fdo-aio.service
echo 'verify FDO ports 8080 (manufacturing server), 8081 (owner_onboarding server), 8082 (rendezvous server) and 8083 (serviceinfo api server) are open and listenting...'
ss -ltnp | grep -E '^State|:808[0-3]'
echo 'check if firewalld is running'
systemctl status firewalld
#change later: below firewall-cmd command only if firewalld is running
systemctl is-active firewalld
if [$? ==0]
then
	sudo firewall-cmd --add-port=8080-8083/tcp --permanent^
	sudo  firewall-cmd --permanent --list-ports
fi;

#download fdo configs & extract

#create public private key

#encode RHT username & password

#extract service token & admin token

#echo 'start manufacturing server'
#sudo systemctl enable --now fdo-manufacturing-server.service 

####### STEP 2 #####
#Install Image builder
sudo dnf install -y osbuild-composer composer-cli  bash-completion
#Enable Image builder service
sudo systemctl enable osbuild-composer.socket --now
#Load the shell config script so that bash completion works immediately w/o reboot
source /etc/bash_completion.d/composer-cli

##optional install cockpit - real wo/men use the CLI :)
#sudo dnf install -y cockpit-composer
#sudo systemctl enable cockpit.socket --now
#sudo firewall-cmd --add-service=cockpit --permanent
#sudo firewall-cmd --reload

### download the automation blueprint sample from git
echo 'downloading automatin blueprint to customize'
curl -o ~/blueprint-insights.toml https://raw.githubusercontent.com/luisarizmendi/tutorial-secure-onboarding/master/documentation/modules/ROOT/examples/blueprint-insights.toml

echo ' need following variabale to be defined'
echo 'SSH_PUB_KEY=$SSH_PUB_KEY'
echo 'getting admin password, eg redhat'
ADMIN_PASSW=$(python3 -c 'import crypt,getpass;pw=getpass.getpass();print(crypt.crypt(pw) if (pw==getpass.getpass("Confirm: ")) else exit())')

echo 'applying SSH_PUB_KEY and $ADMIN_PASSW to blueprint file'
sed -i "s|<SSH PUB KEY>|${SSH_PUB_KEY}|g" ~/blueprint-insights.toml
sed -i "s|<ADMIN PASSW>|${ADMIN_PASSW}|g" ~/blueprint-insights.toml

echo 'push customized blueprint file into compose'
sudo composer-cli blueprints push ~/blueprint-insights.toml

#list blueprints
echo ('listing blueprints in composer')
sudo composer-cli blueprints list

echo ('creating edge-commit type image')
sudo composer-cli compose start-ostree kvm-insights edge-commit

echo ('checking compose status...until finished')
watch -g sudo composer-cli compose status

echo ('download image builder image')
sudo composer-cli compose status
echo ('provide image id (as per previous command):')
read imageID
sudo composer-cli compose image $imageID

echo 'installing podman'
sudo dnf install -y podman

### for PXE network boot create webserver ####
cat <<EOF > nginx.conf
events {
}
http {
    server{
        listen 8080;
        root /usr/share/nginx/html;
        location / {
            autoindex on;
            }
        }
     }
pid /run/nginx.pid;
daemon off;
EOF

echo 'creating Containerfile for ngnix based webserver'

cat <<EOF > Containerfile
FROM registry.access.redhat.com/ubi8/ubi
RUN yum -y install nginx && yum clean all
ARG commit
ADD \$commit /usr/share/nginx/html/
ADD nginx.conf /etc/
EXPOSE 8080
CMD ["/usr/sbin/nginx", "-c", "/etc/nginx.conf"]
EOF

### building commit image
echo 'building container'
sudo podman build -t blueprint-insights:$imageID --build-arg commit=$imageID`-commit.tar .

echo 'tagging container'
sudo podman tag blueprint-insights:$imageID blueprint-insights:latest

echo 'defining service ports and update firewall'
IMAGE_BUILDER_IP=localhost
IMAGE_PUBLISH_PORT=8090
sudo firewall-cmd --add-port=${IMAGE_PUBLISH_PORT}/tcp --permanent
sudo firewall-cmd --reload

echo 'start container'
#sudo podman run --name <blueprint_name>-<image id> -d -p  ${IMAGE_PUBLISH_PORT}:8080 <blueprint_name>:<image id>
sudo podman run --name blueprint-insights -d -p  ${IMAGE_PUBLISH_PORT}:8080 blueprint-insights

echo 'checking repo is available up and running'
curl http://${IMAGE_BUILDER_IP}:${IMAGE_PUBLISH_PORT}/repo/

echo 'checking repo contents are correct'
curl http://localhost:${IMAGE_PUBLISH_PORT}/compose.json


### break out into separte script ###
echo '##########################'
echo 'now creating Edge image...'
#sda for physical device install
DISK_DEVICE=sda  #vda for virtual devices
#vda for virtual device install
#DISK_DEVICE=vda
FDO_MANUFACTURING_URL="192.168.68.62:8090"


echo 'creating blueprint for edge image'
cat <<EOF > blueprint-fdo.toml
name = "blueprint-fdo"
description = "Blueprint for FDO"
version = "0.0.1"
packages = []
modules = []
groups = []
distro = ""
[customizations]
installation_device = "/dev/${DISK_DEVICE}"
[customizations.fdo]
manufacturing_server_url = "${FDO_MANUFACTURING_URL}"
diun_pub_key_insecure = "true"
EOF

echo 'creating edge image based on blueprint'
sudo composer-cli blueprints push blueprint-fdo.toml

baserelease=$(cat /etc/redhat-release | awk '{print $6}' | awk -F . '{print $1}')
basearch=$(arch)

echo 'building edge device image'
sudo composer-cli compose start-ostree blueprint-fdo edge-simplified-installer --ref rhel/${baserelease}/${basearch}/edge --url http://${IMAGE_BUILDER_IP}:${IMAGE_PUBLISH_PORT}/repo/

echo 'switching to watch composer build in 3 - 2 - 1'
sleep 3
sudo watch -g composer-cli compose status

echo 'assigning iso image id to variable in prepration for download'
FDO_ISO_IMAGE_ID=1d1533f7-6672-4c44-a16c-b9e33680828c

sudo composer-cli compose image ${FDO_ISO_IMAGE_ID}
sudo chown $(whoami) ${FDO_ISO_IMAGE_ID}-simplified-installer.iso

