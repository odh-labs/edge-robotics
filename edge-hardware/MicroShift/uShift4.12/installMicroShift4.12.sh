
# Steps taken from: https://access.redhat.com/documentation/en-us/red_hat_build_of_microshift/4.12/html-single/installing/index
# This script is based on a RHEL8.7 instance with lvm storage management. For example you can use:
# AMI ID: ami-040eb61173ba40e89
# Platform details: Red Hat Enterprise Linux
# AMI name: ProComputers RHEL-8.7-x86_64-LVM-10GiB-HVM-20221220_052520-3686aad7-f1c3-4f97-9872-a6f8176d0f60
# on an t2.medium EC2.instance
###
# To run MicroShift, the minimum system requirements are:
#     x86_64 or aarch64 CPU architecture
#     Red Hat Enterprise Linux 8 with Extended Update Support (8.6 or later)
#     2 CPU cores
#     2GB of RAM
#     2GB of free system root storage for MicroShift and its container images - I'd got with 10GB 

#!/bin/bash

check_exit_code()
{
   # There is no error found
	if [ "$1" -eq 0 ] 
    then
         echo -e "\033[32mStatus: OK\033[0m"
         return
    else    
        echo -e "\033[31mStatus: NOT OK - SH*T HIT THE FAN!!!\033[0m"
    fi
}


echo -n "Provide path to pull-secret eg. $HOME/openshift-pullsecret: "
read path2pullsecret
echo -n "Provide Red Hat Username: "
read username
echo "Red Hat Username: $username"
echo -n "Provide Red Hat Password: "
read -s password

#debug
#echo "password provided: $password"

if [ -z "$username" ]
    then
        echo '###'
        echo "usage installMicroShift.sh redhat_username"
        echo '###'
        #check_exit_code $?
        exit
fi

echo '###ensure that vgs (volume groups) displays volume groups with storage available > 10Gb'
sudo vgs
check_exit_code $?

echo '### setup subscription manager - provide username / password'
sudo -S subscription-manager register --username $username --password $password
check_exit_code $?


echo '# enabling repos'
sudo subscription-manager repos \
--enable rhocp-4.12-for-rhel-8-$(uname -i)-rpms \
--enable fast-datapath-for-rhel-8-$(uname -i)-rpms
check_exit_code $?


echo '### installing microshift'
sudo dnf install -y microshift
check_exit_code $?

echo '### copy pull secret from path2pullsecret to /etc/crio'
sudo cp $path2pullsecret /etc/crio/openshift-pull-secret
check_exit_code $?

echo '### ensuring root user is owner of the pull-secret'
sudo chown root:root /etc/crio/openshift-pull-secret
check_exit_code $?

echo '### if firewalld is running ensure firewall configuration is setup for the cluster networks'
sudo firewall-cmd --permanent --zone=trusted --add-source=10.42.0.0/16
sudo firewall-cmd --permanent --zone=trusted --add-source=169.254.169.1
sudo firewall-cmd --reload
check_exit_code $?

echo '### start MicroShift'
sudo systemctl start microshift
check_exit_code $?

echo '### enable MicroShift'
sudo systemctl enable microshift
check_exit_code $?

echo '### installing client tooling'
sudo dnf install -y openshift-clients 
check_exit_code $?

echo '### setting up cluster access'
mkdir -p ~/.kube/
sudo cat /var/lib/microshift/resources/kubeadmin/kubeconfig > ~/.kube/config
check_exit_code $?

echo '### verifying that MicroShift is running'
oc get all -A
check_exit_code $?

echo '### MicroShift install done ###'
