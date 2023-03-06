#!/bin/bash
echo '### \n ensure that vgs (volume groups) displays volume groups with storage available > 10Gb'
sudo vgs

echo '### \n setup subscription manager - provide username / password'
sudo subscription-manager register

echo '# enable repos'
sudo subscription-manager repos \
--enable rhocp-4.12-for-rhel-8-$(uname -i)-rpms \
--enable fast-datapath-for-rhel-8-$(uname -i)-rpms

sudo dnf install -y microshift

echo '### prepare pull secret from https://console.redhat.com/openshift/install/pull-secret'
read -p "Press Enter when you done copying your pull secret to $HOME/openshift-pull-secret" </dev/tty

echo '### copy pull secret to /etc/crio'
sudo cp $HOME/openshift-pull-secret /etc/crio/openshift-pull-secret

echo '### ensure root user is owner of the pull-secret'
sudo chown root:root /etc/crio/openshift-pull-secret

echo '### if firewalld is running ensure firewall configuration is setup for the cluster networks'
sudo firewall-cmd --permanent --zone=trusted --add-source=10.42.0.0/16
sudo firewall-cmd --permanent --zone=trusted --add-source=169.254.169.1
sudo firewall-cmd --reload


echo '### start MicroShift'
sudo systemctl start microshift

echo '### enable MicroShift'
sudo systemctl enable microshift

echo '### setting up cluster access'
mkdir -p ~/.kube/
sudo cat /var/lib/microshift/resources/kubeadmin/kubeconfig > ~/.kube/config

echo '### verifying that MicroShift is running'
oc get all -A

echo '### done ###'



