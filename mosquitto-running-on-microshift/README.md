# mosquitto-running-on-microshift

## 1. Introduction
According to the 
[MicroShift Home Page](https://microshift.io/microShift-home-page) :

~~~~
MicroShift is a project that is exploring how OpenShift and Kubernetes can be optimized for small form factor and edge computing.
~~~~
And it requires only modest resources to operate according to its [Github page](https://microshift.io/docs/getting-started//github-page) :
~~~~
* a supported 64-bit CPU architecture (amd64/x86_64, arm64, or riscv64)
* a supported OS (see below)
* 2 CPU cores
* 2GB of RAM
* 1GB of free storage space for MicroShift
~~~~
I successfully installed MicroShift in a VM using kcli. On second thought, an edge environment will unlikely have the resources to run a VM! Consequently, I decided to run it bare-metal.

## 2. Installing MicroShift
I don't want to reinvent the wheel. I used the [microshift-installer](https://github.com/nerdalert/microshift-installer) I found on Github.

You must make sure your machine's host name is set up in the /etc/hosts file with a fully qualified domain name before you follow the instructions from the link above or your installation may fail. Once you do that, all you need to do, slightly modified from the procedure described in the link, is to execute the following commands:
~~~~
curl -sfL https://raw.githubusercontent.com/nerdalert/microshift-installer/main/microshift-install.sh |  sh -s -

curl -O https://mirror.openshift.com/pub/openshift-v4/$(uname -m)/clients/ocp/stable/openshift-client-linux.tar.gz
sudo tar -xf openshift-client-linux.tar.gz -C /usr/local/bin oc kubectl

mkdir ~/.kube
sudo cat /var/lib/microshift/resources/kubeadmin/kubeconfig > ~/.kube/config

// check if the containers are running
oc get pods -A
~~~~
And after a few minutes, your MicroShift will be ready for action.

## 3 Creating an Eclipse Mosquitto Image
Our robots use a MQTT server. We are using Mosquitto as our MQTT server. Sticking to my principle of not reinventing the wheel, I used another great time saver I found on Github:
[mosquitto-openshift](https://github.com/kevinboone/mosquitto-openshift/mosquitto-openshift)

I only need to make 1 change in the files/mosquitto.conf file from:
~~~~
port 1883
~~~~
to
~~~~
listener 1883
~~~~
to support a http connection with user:password equal admin:admin. The image I built is available on quay.io: 
~~~~
quay.io/andyyuen/mymosquitto
~~~~

## 4 Deploying Mosquitto on MicroShift
To deploy my mosquitto image on MicroShift, execute the following commands from the mosquitto-running-on-microshift directory:
~~~~
oc new-project mosquitto
oc create -f manifests/mosquitto.yaml

oc get svc mosquitto -o yaml
~~~~
I am exposing the mosquitto application using a NodePort and let MicroShift assign the node port number. The last command will show you the NodePort number assigned by MicroShift. Alternatively, you can modify the mosquitto.yaml file to specify a NodePort number.

## Verifying Mosquitto is Working
On another machine or your MicroShift machine, install mosquitto. We don't enable the mosquitto server. All we want are the publish and subscribe utilities.

On Fedora, you could install mosquitto as follows:
~~~~
sudo dnf install mosquitto
~~~~
Make sure that mosquitto is running on Microshift and not the mosquitto server we just installed. From one terminal window, execute:
~~~~
mosquitto_sub -h hostIP -p nodePortNumber  -t mytopic -u admin -P admin
~~~~
where
* hostIP is your MicroShift host's IP address
* nodePortNumber is the node port number you found in the previous 'oc get svc..." command output

<br />and from another terminal window:
~~~~
mosquitto_pub -h hostIP -p nodePortNumber  -u admin -P admin -m "hello 1" -t mytopic
~~~~
Each time you publish a message, you will see the message displayed in the subscribe window.

